# TestHub 项目记忆

## 项目概述
TestHub 是一个 AI 驱动的全栈测试管理平台，Django 4.2 + Vue 3 技术栈。

## App 自动化模块（2026-07-06）
- 采用在现有 `ui_automation` 模块中扩展的方案，而非新建独立 Django App
- 新增文件：`apps/ui_automation/appium_engine.py` - Appium 移动端测试引擎
- 修改文件：`models.py`（新增 AppDevice、AppConfig 模型）、`test_executor.py`（新增 engine='appium' 分支）、`requirements.txt`（新增 Appium-Python-Client）
- 执行流程：AI生成Markdown用例 → 人工采纳到TestCase → 手动配置元素/步骤 → 选择Appium引擎执行
- 环境依赖：需要 Appium Server + Android/iOS 设备，通过 `AppDevice` 模型管理
- AppConfig 新增 `ai_project` 字段（FK→projects.Project），使"所属项目"下拉框可同时选择 UI自动化项目和 AI用例项目

## 统一项目选择（2026-07-06）
- **新增后端 API**：`/api/ui-automation/all-projects/` 返回合并后的项目列表（UiProject + AI Project）
- **新增后端 API**：`/api/ui-automation/ensure-ui-project/` 接受 AI Project ID，自动查找/创建对应 UiProject
- **新增前端 composable**：`frontend/src/utils/useUnifiedProjects.js` 统一管理项目加载和 ID 解析
- **修改 11 个前端页面**的项目下拉框，均按 `el-option-group` 分组展示 UI自动化项目 / AI用例项目
- 选择 AI 项目时自动调用 `ensure-ui-project` 创建映射的 UiProject，无需用户手动创建
- 修改文件：SuiteList.vue、TestCaseManager.vue、ScriptList.vue、ScriptEditorEnhanced.vue、ElementList.vue、ElementManagerEnhanced.vue、PageObjectManager.vue、ExecutionList.vue、ReportList.vue、ScheduledTasks.vue、AppConfigList.vue

## AI生成用例 → UI自动化一键运行（方案A，2026-07-06）
- 用户需求：把需求分析模块生成的AI用例直接转到UI自动化运行；并明确要求"相同问题不要每次重新思考，记住结论"
- 已采纳方案A（非结构化转换）：AI生成用例 → 转为 `AICase`（UI自动化AI用例），导入后可在"AI用例管理"页直接点"执行"；执行由 AI Agent 读取自然语言任务描述驱动浏览器（browser-use），**不需要元素定位器、不需要手写结构化步骤**
- 后端：`AICaseViewSet.import_from_generated` action，按 `task_id` 查 **`TestCaseGenerationTask`**（不是 AnalysisTask！），从其 `final_test_cases` 解析用例并创建 AICase；**支持可选 `cases` 参数**（前端传解析后的用例 dict 列表），传入时只转换这些用例，不传则转换全部
- ⚠️ 用户明确诉求：**不要整个任务全转**，要能"选择哪一条用例就只转哪一条"。已实现：在 `TaskDetail.vue` 每条用例操作列加「🚀 转UI」单条按钮，并在批量操作区加「🚀 转UI自动化(N)」按钮作用于勾选的 `selectedCases`；`GeneratedTestCaseList.vue` 任务行仍有"转UI自动化"按钮（转整个任务，保留作快捷入口）
- ⚠️ 前端列表 API `/requirement-analysis/api/testcase-generation/` 返回的是 TestCaseGenerationTask，不要和 AnalysisTask 混淆
- 前端：`GeneratedTestCaseList.vue` 操作列"🚀 转UI自动化"按钮 → `importGeneratedToAICase` → 跳转 `/ai-intelligent-mode/cases`
- **用例库（apps.testcases.TestCase）也已支持转UI**：`AICaseViewSet.import-from-testcases` action（POST /api/ui-automation/ai-cases/import-from-testcases/，接收 `case_ids`），前端 `frontend/src/views/testcases/TestCaseList.vue` 批量区"🚀 转UI自动化(N)"按钮 + 每行"🚀 转UI"按钮 → `importTestcasesToAICase` → 跳转 `/ai-intelligent-mode/cases`
- 未采纳方案B（转为结构化 UI 用例 + 补元素定位器），因不是"直接运行"且工作量大
- ⚠️ 部署踩坑（重要）：本项目 `docker-compose up -d --build` 在镜像名相同（`testhub-backend:latest`/`testhub-frontend:latest`）时**不会重启容器**，必须用 `docker rm -f <容器> && docker-compose up -d <服务>` 强制重建容器；且 `Dockerfile.frontend` 只 `COPY frontend/dist`，**自己不跑构建**，部署前端前必须先 `cd frontend && npm run build` 生成 dist；验证后端路由可直接 `curl -X POST http://localhost:8000/api/ui-automation/ai-cases/import-from-generated/` 看是否返回 401（未认证=路由已生效，404=未注册）

## 用例库 → 结构化 Appium 用例转换器（2026-07-06，路A）
- 用户最终真实需求是 **App 自动化（Appium + 真机）**，来源=用例库 `apps.testcases.TestCase`。这区别于第22-31行的 AICase 方案（AICase=自然语言、browser-use 驱动电脑 Chrome、免定位器）。
- 已实现半自动转换器：后端 `TestCaseViewSet.convert-from-testcases` action（POST /ui-automation/test-cases/convert-from-testcases/，参数 `case_ids` + `ui_project_id`）；前端 `TestCaseList.vue` 批量区「📱 转Appium用例(N)」+ 行内「📱 转Appium」→ 选目标 UiProject 弹窗 → `convertTestcasesToAppium`。
- 转换逻辑：用例库用例 → `ui_automation.TestCase`（project=UiProject，注意与用例库 Project 是两套独立项目，必须前端传 `ui_project_id`）；步骤文字推断 `action_type`（click/fill/assert/wait/screenshot），每条交互步骤自动建占位 `Element`（locator_value='TODO_待补充控件定位器'，定位策略默认 xpath），用例级 expected_result 追加为 assert 步骤。同项目同名跳过防重复。用户只需到「元素管理」回填控件定位器即可用 Appium 引擎执行。
- helper：`infer_appium_action_type` / `extract_step_input_value`（views.py 模块级）。
