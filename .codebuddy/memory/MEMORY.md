# TestHub 项目记忆

## 环境注意（Windows 机器）
- **PowerShell 5.x 不支持 `&&`**（会报 "标记'&&'不是此版本中的有效语句分隔符"）。用分号 `;` 分隔、或 `cmd /c "..."` 包裹、或升级到 PowerShell 7。
- **PowerShell 里 `curl` 是 `Invoke-WebRequest` 别名**，真实 curl 用 `curl.exe`；若 JSON 含引号，把请求体写文件后用 `curl.exe -d "@file.json"`。

## 项目概述
TestHub 是 AI 驱动的全栈测试管理平台，Django 4.2 + Vue 3。

## 部署踩坑（重要！反复踩过）
- `docker-compose up -d --build` 在镜像名相同时**不会重启容器**，必须 `docker rm -f <容器> && docker-compose up -d <服务>` 强制重建。
- `Dockerfile.frontend` 只 `COPY frontend/dist`，**自己不跑构建**，部署前端前必须先 `cd frontend && npm run build` 生成 dist。
- ⚠️ **前端 dist 缓存坑**：普通 `docker compose build frontend` 的 COPY 层在 Windows/Docker Desktop 会**命中缓存（CACHED）**。必须 `docker compose build --no-cache frontend` 强制重建。验证：`docker exec testhub-frontend sh -c "grep -rl '关键词' /usr/share/nginx/html/assets/"`。改完前端浏览器务必 Ctrl+F5 硬刷新。
- ⚠️ **Docker Desktop 绑定挂载 Windows 路径的已知 bug**：把 `C:/...`/`./...`/`/c/...` 绑定挂载进容器时，Docker 把路径翻译成 `/run/desktop/mnt/host/c/...` 后会对父目录 `/run/desktop/mnt/host/c` 执行 `mkdir` 报 `file exists`，容器卡在 `Created` 起不来。**与路径写法无关**，唯一可靠修法是重启 Docker Desktop 引擎（托盘 Restart 或 `wsl --shutdown`）。重启会短暂中断所有容器。知识库实时同步需求因此受阻，目前用命名卷 `testhub-kb`（数据卷 `testhub_testhub-kb`）+ 手动 `docker cp` 变通。

## 迁移系统约定（关键）
- **本项目 `apps/*/migrations/0001_initial.py` 是空占位（`operations=[]`），表实际已存在于库中**——这是设计使然，不要当缺失去"补全"建表。
- 新增/修改模型字段需要加列时，**必须用 raw SQL 幂等加列**（`information_schema` 判断存在性再 `ALTER TABLE ADD COLUMN`）。
- `docker_start.py` 自愈流程：`DELETE FROM django_migrations` → raw SQL 幂等加列 → **`migrate --fake`**。不要用 `--fake-initial`。

## App 自动化模块
- 扩展现有 `ui_automation` 模块：新增 `appium_engine.py`、AppDevice/AppConfig 模型
- AI用例→UI自动化一键运行（方案A）：AI生成用例→转AICase→browser-use驱动执行，无需定位器
- 用例库→结构化Appium转换器：TestCase→ui_automation.TestCase+占位Element
- Airtest集成：Phase0导入解析器已完成（`/airtest/import/`）；Phase1知识库表化待做
- 操作录制：基于Appium+真机已端到端通过；纯Airtest录制模式代码完成待构建镜像

## 统一项目选择
- 后端 `/api/ui-automation/all-projects/` + `/ensure-ui-project/`
- 前端 `useUnifiedProjects.js` composable，11个页面已改用分组下拉框

## 需求分析模块（2026-07-13 重点）
- 拆解结果渲染：**纯 markdown 渲染是唯一稳定方案**，结构化表格渲染（parsedAnalyzeSections）会导致白屏崩溃，不要再改回
- 前端 API 文件：`frontend/src/api/requirement-analysis.js`
- 后端关键文件：`apps/requirement_analysis/views.py`, `serializers.py`, `models.py`
- TestCaseGenerationTask（用例生成任务）≠ AnalysisTask（需求拆解任务），别混淆

## 用户偏好
- 用户喜欢**可编辑的内容展示**、**美观的格式**、**流式对话式深度追问**
