<#
.SYNOPSIS
  TestHub 生产部署脚本（GitHub Actions self-hosted runner 与人工发布共用）。

.DESCRIPTION
  按改动类型选择最小代价的部署动作：
    · 后端代码改动 -> docker build 后端镜像（FROM 本地 base 镜像 + COPY，约 30 秒）+ compose 替换容器
                     加 -HotPatch 则改走 tar + docker cp + restart（更快，但容器一旦重建代码就丢）
    · 前端改动     -> docker build 前端镜像（Dockerfile.frontend 内部 npm ci + npm run build）并替换容器
    · 依赖变更     -> 必须重建“基础镜像”（apt/pip/playwright，30~100 分钟），本脚本只提示不自动执行

  两个目录概念（CI 场景必需，否则会建出第二套容器/卷）：
    · 代码目录  = 本脚本所在仓库根目录（CI 中是 runner 的 checkout，内容等于本次提交）
    · 编排目录  = 生产 docker-compose.yml/.env 所在目录（默认 C:\TestHub）
  镜像用 docker build 显式构建（tag 必须等于 compose 派生名 <project>-<service>），再用生产
  编排目录 `docker compose -f ... -p ... up -d --no-build` 替换容器，保证卷挂载路径与既有容器一致。

.EXAMPLE
  .\scripts\deploy_prod.ps1 -All
.EXAMPLE
  .\scripts\deploy_prod.ps1 -BackendOnly
.EXAMPLE
  .\scripts\deploy_prod.ps1 -BackendOnly -HotPatch
.EXAMPLE
  .\scripts\deploy_prod.ps1 -ChangedFilesFile changed.txt
.EXAMPLE
  .\scripts\deploy_prod.ps1 -All -DryRun
#>
[CmdletBinding()]
param(
    [string[]]$ChangedFiles = @(),
    [string]$ChangedFilesFile,
    [switch]$All,
    [switch]$BackendOnly,
    [switch]$FrontendOnly,
    # 后端走 tar + docker cp + restart（约 15 秒）。代价：容器下次被重建时这些 .py 会丢失，
    # 因为 /app 不是 bind mount。默认走镜像重建（约 30 秒且持久）。
    [switch]$HotPatch,
    [switch]$DryRun,
    [int]$HealthTimeoutSec = 180,
    # /api/schema/ 会加载全部 ViewSet；某个 filterset_fields 写错就会 500。置此开关可跳过。
    [switch]$SkipSchemaCheck,
    # compose 服务名（与 docker-compose.yml 一致）
    [string]$BackendService = 'backend',
    [string]$FrontendService = 'frontend',
    # 容器名取 compose 里的 container_name 字面值（不受 -p 影响）
    [string]$BackendContainer = 'testhub-backend',
    [string]$FrontendContainer = 'testhub-frontend',
    # 生产编排目录（含 docker-compose.yml 与 .env）；默认取 TESTHUB_COMPOSE_DIR，否则探测 C:\TestHub
    [string]$ComposeRoot = $env:TESTHUB_COMPOSE_DIR,
    # 编排文件名（默认 docker-compose.yml）；改成 docker-compose.dev.yml 即可在 dev 环境演练同一脚本
    [string]$ComposeFile = 'docker-compose.yml',
    [string]$ComposeProject = 'testhub'
)

$ErrorActionPreference = 'Stop'
$buildRoot = Split-Path -Parent $PSScriptRoot
Set-Location $buildRoot

# 镜像 tag 必须与 compose 派生名一致，否则 `up -d --no-build` 会拉到旧镜像/找不到镜像。
$backendImage = "${ComposeProject}-${BackendService}:latest"
$frontendImage = "${ComposeProject}-${FrontendService}:latest"

function Write-Step([string]$msg) {
    Write-Host ""
    Write-Host "==> $msg" -ForegroundColor Cyan
}

function Write-Warn([string]$msg) {
    Write-Host "!!! $msg" -ForegroundColor Yellow
}

function Wait-Http([string]$url, [int[]]$expected, [int]$timeoutSec, [string]$label) {
    $deadline = (Get-Date).AddSeconds($timeoutSec)
    while ((Get-Date) -lt $deadline) {
        try {
            $code = [int](curl.exe -s -o NUL -w "%{http_code}" --max-time 5 $url)
            if ($expected -contains $code) {
                Write-Host "    $label 健康检查通过（HTTP $code）" -ForegroundColor Green
                return $true
            }
        }
        catch { }
        Start-Sleep -Seconds 3
    }
    Write-Warn "$label 健康检查超时（${timeoutSec}s 内未拿到预期状态：$($expected -join '/')）"
    return $false
}

# ---------- 0. 目录与前置检查 ----------
# 显式传进来的路径不存在时必须报错，不能静默回退（否则 CI 里编排文件漏了就悄悄用了别的目录）
if ($ComposeRoot) {
    $composeFile = if ([System.IO.Path]::IsPathRooted($ComposeFile)) { $ComposeFile } else { Join-Path $ComposeRoot $ComposeFile }
}
else {
    foreach ($cand in @('C:\TestHub', $buildRoot)) {
        $probe = if ([System.IO.Path]::IsPathRooted($ComposeFile)) { $ComposeFile } else { Join-Path $cand $ComposeFile }
        if (Test-Path $probe) { $ComposeRoot = $cand; $composeFile = $probe; break }
    }
    if (-not $composeFile) {
        $ComposeRoot = $buildRoot
        $composeFile = if ([System.IO.Path]::IsPathRooted($ComposeFile)) { $ComposeFile } else { Join-Path $ComposeRoot $ComposeFile }
    }
}
$composeDir = Split-Path -Parent $composeFile

Write-Host "代码目录：$buildRoot" -ForegroundColor DarkGray
Write-Host "编排目录：$composeDir（file=$ComposeFile, project=$ComposeProject）" -ForegroundColor DarkGray

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) { throw '找不到 docker 命令（请在装有 Docker 的生产机执行）' }
if (-not (Test-Path $composeFile)) { throw "找不到编排文件：$composeFile" }
if (-not (Test-Path (Join-Path $composeDir '.env'))) {
    throw "编排目录缺少 .env（$composeDir），无法执行 docker compose"
}
foreach ($f in @('Dockerfile.backend', 'Dockerfile.frontend')) {
    if (-not (Test-Path (Join-Path $buildRoot $f))) { throw "代码目录缺少 $f（$buildRoot）" }
}

# ---------- 1. 计算需要部署哪些部分 ----------
if ($ChangedFilesFile) {
    if (-not (Test-Path $ChangedFilesFile)) { throw "改动清单文件不存在：$ChangedFilesFile" }
    $ChangedFiles = @(Get-Content $ChangedFilesFile | Where-Object { $_.Trim() -ne '' } | ForEach-Object { $_.Trim() })
}
# `powershell -File xxx.ps1 -ChangedFiles a,b` 会把 "a,b" 当成一个字符串传进来，这里统一拆开
$ChangedFiles = @($ChangedFiles | ForEach-Object { $_ -split ',' } | Where-Object { $_.Trim() -ne '' } | ForEach-Object { $_.Trim() })

$needBackend = [bool]($All -or $BackendOnly)
$needFrontend = [bool]($All -or $FrontendOnly)
$needDepsReview = $false
$manualNotes = New-Object System.Collections.Generic.List[string]

if (-not ($All -or $BackendOnly -or $FrontendOnly)) {
    if (-not $ChangedFiles -or $ChangedFiles.Count -eq 0) {
        Write-Warn '没有检测到改动，也没有指定部署范围；如需全量发布请加 -All'
        exit 0
    }
    foreach ($raw in $ChangedFiles) {
        $p = ($raw -replace '\\', '/').Trim()
        if ($p -match '^frontend/') { $needFrontend = $true }
        if ($p -match '^(apps/|backend/|manage\.py$|docker_start\.py$|tester[^/]*\.md$)') { $needBackend = $true }
        if ($p -match '^(Dockerfile\.frontend|nginx\.conf)$') { $needFrontend = $true }
        # 依赖层已经烧进 testhub-backend-base，改 requirements 只重建后端镜像是不够的
        if ($p -match '^(requirements[^/]*\.txt|Dockerfile\.backend-deps|Dockerfile\.backend-base)$') { $needDepsReview = $true }
        if ($p -match '^Dockerfile\.backend$') { $needBackend = $true }
        if ($p -match '^docker-compose\.yml$') {
            $manualNotes.Add('生产 docker-compose.yml 有改动：脚本不修改生产编排文件，请人工确认后 docker compose up -d 重建对应服务')
        }
        if ($p -match '^(\.codebuddy/|_ext/|skills-dist/|docs/|scripts/|\.github/)') {
            $manualNotes.Add("$p 不参与运行，已跳过")
        }
    }
}

$mode = if ($HotPatch) { 'tar + docker cp 热更新（容器重建即丢失）' } else { '镜像重建（约 30 秒）' }

Write-Step '部署计划'
Write-Host ("    后端            : {0}" -f $needBackend)
if ($needBackend) { Write-Host ("    后端方式        : {0}" -f $mode) }
Write-Host ("    前端构建+替换   : {0}" -f $needFrontend)
Write-Host ("    镜像 tag        : {0} / {1}" -f $backendImage, $frontendImage)
if ($ChangedFiles.Count -gt 0) {
    Write-Host ("    改动文件        : {0} 个" -f $ChangedFiles.Count)
}
if ($manualNotes.Count -gt 0) {
    foreach ($n in ($manualNotes | Select-Object -Unique)) { Write-Warn $n }
}
if ($needDepsReview) {
    Write-Warn '检测到依赖层文件变更：必须重建基础镜像（本脚本不自动执行，约 30~100 分钟）'
    Write-Warn '  python scripts/gen_backend_base.py'
    Write-Warn '  docker build -f Dockerfile.backend-base -t testhub-backend-base:<YYYYMMDD> .'
    Write-Warn '  然后把 Dockerfile.backend 的 FROM 改成新 tag 再发布（否则新包在容器里不存在）'
}
if (-not ($needBackend -or $needFrontend)) {
    Write-Warn '本次改动不涉及运行代码，无需部署'
    exit 0
}
if ($DryRun) {
    Write-Warn 'DryRun：以上动作未真正执行'
    exit 0
}

# ---------- 2. 后端 ----------
if ($HotPatch) {
    Write-Step '后端代码热更新（tar + docker cp + restart，不重建镜像）'
    $tar = '_deploy_sync.tar'
    if (Test-Path $tar) { Remove-Item $tar -Force }
    $paths = @()
    foreach ($p in @('apps', 'backend', 'manage.py', 'docker_start.py')) {
        if (Test-Path $p) { $paths += $p }
    }
    $paths += @(Get-ChildItem -Path . -Filter 'tester*.md' -File -ErrorAction SilentlyContinue | ForEach-Object { $_.Name })
    if (-not $paths) { throw '没有可同步的后端代码路径' }

    # Windows 下手动 docker cp 目录会随机漏文件，先在宿主机打 tar 再进容器解包
    & tar -cf $tar --exclude '__pycache__' --exclude '*.pyc' @paths
    if ($LASTEXITCODE -ne 0) { throw "打包失败：tar -cf $tar $($paths -join ' ')" }

    docker cp $tar "${BackendContainer}:/tmp/$tar"
    if ($LASTEXITCODE -ne 0) { throw "docker cp 到 $BackendContainer 失败（容器是否在运行？）" }
    docker exec $BackendContainer sh -c "tar -xf /tmp/$tar -C /app && find /app -name __pycache__ -type d -exec rm -rf {} + && rm -f /tmp/$tar"
    if ($LASTEXITCODE -ne 0) { throw '容器内解包失败' }
    Remove-Item $tar -Force -ErrorAction SilentlyContinue

    docker restart $BackendContainer
    if ($LASTEXITCODE -ne 0) { throw "重启 $BackendContainer 失败" }
}
else {
    Write-Step "后端镜像重建（FROM testhub-backend-base + COPY . . -> $backendImage）"
    docker build -f (Join-Path $buildRoot 'Dockerfile.backend') -t $backendImage $buildRoot
    if ($LASTEXITCODE -ne 0) { throw '后端镜像构建失败' }

    Write-Step '后端容器替换（compose 只看镜像 tag，不重新 build）'
    docker compose -f $composeFile -p $ComposeProject up -d --no-build $BackendService
    if ($LASTEXITCODE -ne 0) { throw '后端容器替换失败' }
}

Write-Step '后端健康检查（/api/ 返回 404 即代表 Django 已起来）'
if (-not (Wait-Http -url 'http://localhost:8000/api/' -expected @(404, 200) -timeoutSec $HealthTimeoutSec -label 'backend')) {
    docker logs --tail 40 $BackendContainer
    throw '后端健康检查失败，请查看上面的容器日志'
}

if (-not $SkipSchemaCheck) {
    Write-Step '接口 schema 检查（某个 ViewSet filterset 写错会让这里 500）'
    if (-not (Wait-Http -url 'http://localhost:8000/api/schema/' -expected @(200, 404) -timeoutSec $HealthTimeoutSec -label 'schema')) {
        docker logs --tail 40 $BackendContainer
        throw '/api/schema/ 未返回 200，通常是某个 ViewSet 的 filterset_fields/filterset_class 指向了不存在的字段（可用 -SkipSchemaCheck 跳过）'
    }
}

# 后端容器被 Recreate 后 IP 可能变化，而前端 nginx 的静态 proxy_pass 只在启动时解析一次 upstream。
# 本次不部署前端时必须探测 8080 反代，异常则重启前端容器，否则会静默 502（页面能开、接口全挂）。
if (-not $needFrontend) {
    Write-Step '前端反向代理探测（后端换 IP 后 nginx 可能仍指向旧地址）'
    $frontendUp = (docker ps --format '{{.Names}}' | Select-String -Pattern "^$([regex]::Escape($FrontendContainer))$")
    if (-not $frontendUp) {
        Write-Warn "未检测到运行中的 $FrontendContainer，跳过反代探测"
    }
    else {
        $proxyUrl = 'http://localhost:8080/api/'
        $proxyOk = @(200, 301, 401, 403, 404)
        $code = 0
        try { $code = [int](curl.exe -s -o NUL -w "%{http_code}" --max-time 8 $proxyUrl) } catch { $code = 0 }
        if ($proxyOk -contains $code) {
            Write-Host "    反代正常（HTTP $code）" -ForegroundColor Green
        }
        else {
            Write-Warn "经 8080 访问后端返回 $code，重启 $FrontendContainer 以刷新 upstream 解析"
            docker restart $FrontendContainer | Out-Null
            if ((Wait-Http -url 'http://localhost:8080/' -expected @(200) -timeoutSec 60 -label 'frontend') -and
                (Wait-Http -url $proxyUrl -expected $proxyOk -timeoutSec 60 -label 'frontend->backend')) {
                Write-Host '    反代已恢复' -ForegroundColor Green
            }
            else {
                Write-Warn '反代仍未恢复，请人工检查 nginx.conf 的 upstream 与容器网络'
            }
        }
    }
}

# ---------- 3. 前端 ----------
if ($needFrontend) {
    # Dockerfile.frontend 内有 node:20-alpine builder 阶段，自己 npm ci + npm run build，
    # 且 .dockerignore 已排除 frontend/dist —— 宿主机无需 Node，也不需要预先 build。
    Write-Step "前端镜像构建（builder 阶段内部 npm ci + npm run build -> $frontendImage）"
    Push-Location $buildRoot
    try {
        docker build -f (Join-Path $buildRoot 'Dockerfile.frontend') -t $frontendImage $buildRoot
        if ($LASTEXITCODE -ne 0) { throw '前端镜像构建失败' }
    }
    finally {
        Pop-Location
    }

    Write-Step '前端容器替换'
    docker compose -f $composeFile -p $ComposeProject up -d --no-build $FrontendService
    if ($LASTEXITCODE -ne 0) { throw '前端容器替换失败' }

    Write-Step '前端健康检查'
    if (-not (Wait-Http -url 'http://localhost:8080/' -expected @(200) -timeoutSec $HealthTimeoutSec -label 'frontend')) {
        docker logs --tail 20 $FrontendContainer
        throw '前端健康检查失败'
    }
}

Write-Step '部署完成'
docker ps --format '{{.Names}} | {{.Status}}' | Select-String -Pattern "$BackendContainer|$FrontendContainer"
exit 0
