<template>
  <div class="requirement-analysis">
    <div class="page-header">
      <h1>智能测试用例生成</h1>
      <p>基于需求描述或文档，AI将直接为您生成高质量的测试用例</p>
    </div>

    <!-- 配置引导弹出窗口 -->
    <div v-if="showConfigGuide && !checkingConfig" class="modal-overlay" @click.self="showConfigGuide = false" :key="modalKey">
      <div class="guide-config-modal">
      <div class="guide-header">
        <svg class="guide-icon" viewBox="0 0 1024 1024" xmlns="http://www.w3.org/2000/svg">
          <path d="M512 64C264.6 64 64 264.6 64 512s200.6 448 448 448 448-200.6 448-448S759.4 64 512 64zm0 820c-205.4 0-372-166.6-372-372s166.6-372 372-372 372 166.6 372 372-166.6 372-372 372z" fill="#f59e0b"/>
          <path d="M464 336a48 48 0 1 0 96 0 48 48 0 1 0-96 0zm72 112h-48c-4.4 0-8 3.6-8 8v272c0 4.4 3.6 8 8 8h48c4.4 0 8-3.6 8-8V456c0-4.4-3.6-8-8-8z" fill="#f59e0b"/>
        </svg>
        <div class="guide-title">
          <h2>开始使用AI用例生成功能</h2>
          <p>在使用前，请先完成以下配置：</p>
        </div>
      </div>

      <div class="config-groups">
        <!-- 模型配置行 -->
        <div class="config-group">
          <div class="group-label">模型配置</div>
          <div class="config-items-row">
            <div class="config-item-inline" :class="getConfigItemClass('writer_model')">
              <span class="status-symbol" v-html="getStatusSymbol('writer_model')"></span>
              <span class="config-label">用例编写</span>
              <span class="config-name" v-if="configStatus.writer_model.name">{{ configStatus.writer_model.name }}</span>
              <span class="status-text" v-if="!configStatus.writer_model.configured">未配置</span>
              <span class="status-text warning" v-else-if="!configStatus.writer_model.enabled">已禁用</span>
            </div>

            <div class="config-item-inline" :class="getConfigItemClass('reviewer_model')">
              <span class="status-symbol" v-html="getStatusSymbol('reviewer_model')"></span>
              <span class="config-label">用例评审</span>
              <span class="config-name" v-if="configStatus.reviewer_model.name">{{ configStatus.reviewer_model.name }}</span>
              <span class="status-text" v-if="!configStatus.reviewer_model.configured">未配置</span>
              <span class="status-text warning" v-else-if="!configStatus.reviewer_model.enabled">已禁用</span>
            </div>
          </div>
        </div>

        <!-- 提示词配置行 -->
        <div class="config-group">
          <div class="group-label">提示词配置</div>
          <div class="config-items-row">
            <div class="config-item-inline" :class="getConfigItemClass('writer_prompt')">
              <span class="status-symbol" v-html="getStatusSymbol('writer_prompt')"></span>
              <span class="config-label">用例编写</span>
              <span class="config-name" v-if="configStatus.writer_prompt.name">{{ configStatus.writer_prompt.name }}</span>
              <span class="status-text" v-if="!configStatus.writer_prompt.configured">未配置</span>
              <span class="status-text warning" v-else-if="!configStatus.writer_prompt.enabled">已禁用</span>
            </div>

            <div class="config-item-inline" :class="getConfigItemClass('reviewer_prompt')">
              <span class="status-symbol" v-html="getStatusSymbol('reviewer_prompt')"></span>
              <span class="config-label">用例评审</span>
              <span class="config-name" v-if="configStatus.reviewer_prompt.name">{{ configStatus.reviewer_prompt.name }}</span>
              <span class="status-text" v-if="!configStatus.reviewer_prompt.configured">未配置</span>
              <span class="status-text warning" v-else-if="!configStatus.reviewer_prompt.enabled">已禁用</span>
            </div>
          </div>
        </div>

        <!-- 生成行为配置行 -->
        <div class="config-group">
          <div class="group-label">生成行为配置</div>
          <div class="config-items-row">
            <div class="config-item-inline" :class="getConfigItemClass('generation_config')">
              <span class="status-symbol" v-html="getStatusSymbol('generation_config')"></span>
              <span class="config-label">生成配置</span>
              <span class="config-name" v-if="configStatus.generation_config && configStatus.generation_config.name">{{ configStatus.generation_config.name }}</span>
              <span class="status-text" v-if="!configStatus.generation_config || !configStatus.generation_config.configured">未配置</span>
            </div>
          </div>
        </div>
      </div>

        <div class="guide-actions">
          <button class="generate-manual-btn" @click="goToConfig">
            去配置
          </button>
          <div class="skip-action" @click="showConfigGuide = false">
            稍后配置
          </div>
        </div>
      </div>
    </div>

    <!-- 输出模式选择器 - 全局设置 -->
    <div class="output-mode-section" v-if="!isGenerating && !showResults">
      <div class="output-mode-card">
        <h3>📤 输出模式设置</h3>
        <p class="mode-section-desc">选择测试用例生成的输出方式（适用于手动输入和文档上传两种方式）</p>
        <div class="output-mode-selector">
          <label class="mode-option" :class="{ active: globalOutputMode === 'stream' }">
            <input type="radio" v-model="globalOutputMode" value="stream">
            <div class="mode-content">
              <div class="mode-title">⚡ 实时流式输出</div>
              <div class="mode-desc">内容逐字显示，体验流畅，适合大需求文档</div>
            </div>
          </label>
          <label class="mode-option" :class="{ active: globalOutputMode === 'complete' }">
            <input type="radio" v-model="globalOutputMode" value="complete">
            <div class="mode-content">
              <div class="mode-title">📄 完整输出</div>
              <div class="mode-desc">完成后一次性展示，适合简单需求</div>
            </div>
          </label>
        </div>
      </div>
    </div>

    <div class="main-content">
      <!-- 手动输入需求描述区域 -->
      <div class="manual-input-section" v-if="!isGenerating && !showResults">
        <div class="manual-input-card">
          <h2>✍️ 手动输入需求描述</h2>
          <div class="input-form">
            <div class="form-group">
              <label>需求标题 <span class="required">*</span></label>
              <input 
                v-model="manualInput.title" 
                type="text" 
                class="form-input"
                placeholder="请输入需求标题，如：用户登录功能需求">
            </div>
            
            <div class="form-group">
              <label>需求描述 <span class="required">*</span></label>
              <textarea 
                v-model="manualInput.description" 
                class="form-textarea"
                rows="8"
                placeholder="请详细描述您的需求，包括功能描述、使用场景、业务流程等。例如：&#10;&#10;1. 用户可以通过用户名和密码登录系统&#10;2. 系统需要验证用户身份&#10;3. 登录成功后跳转到主页面&#10;4. 支持记住登录状态&#10;5. 登录失败要给出明确提示..."></textarea>
              <div class="char-count">{{ manualInput.description.length }}/2000</div>
            </div>
            
            <div class="form-group">
              <label>关联项目（可选）</label>
              <select v-model="manualInput.selectedProject" class="form-select">
                <option value="">请选择项目</option>
                <option v-for="project in projects" :key="project.id" :value="project.id">
                  {{ project.name }}
                </option>
              </select>
            </div>

            <div class="form-group">
              <label>关联版本（可选）</label>
              <div class="version-select-row">
                <select v-model="selectedVersion" class="form-select version-select">
                  <option value="">不关联版本</option>
                  <option v-for="ver in availableVersions" :key="ver.id" :value="ver.id">
                    {{ ver.name }}{{ ver.is_baseline ? ' (基线)' : '' }}
                  </option>
                </select>
                <button class="quick-create-ver-btn" @click="openQuickCreateVersion(manualInput.selectedProject)" title="快速新建版本">+</button>
              </div>
            </div>

            <button
              class="generate-manual-btn"
              @click="generateFromManualInput"
              :disabled="!canGenerateManual || isGenerating">
              <span v-if="isGenerating">🔄 生成中...</span>
              <span v-else>🚀 生成测试用例</span>
            </button>
          </div>
        </div>
      </div>

      <!-- 分隔线 -->
      <div class="divider" v-if="!isGenerating && !showResults">
        <span>或</span>
      </div>

      <!-- 文档上传区域 -->
      <div class="upload-section" v-if="!isGenerating && !showResults">
        <div class="upload-card">
          <h2>📄 上传需求文档</h2>
          <div class="upload-area" 
               @dragover.prevent 
               @drop="handleDrop"
               :class="{ 'drag-over': isDragOver }"
               @dragenter="isDragOver = true"
               @dragleave="isDragOver = false">
            <div v-if="!selectedFile" class="upload-placeholder">
              <i class="upload-icon">📁</i>
              <p>拖拽文件到此处或点击选择文件</p>
              <p class="upload-hint">支持 PDF、Word、TXT、Markdown 格式</p>
              <input 
                type="file" 
                ref="fileInput" 
                @change="handleFileSelect"
                accept=".pdf,.doc,.docx,.txt,.md"
                style="display: none;">
              <button class="select-file-btn" @click="$refs.fileInput.click()">
                选择文件
              </button>
            </div>
            
            <div v-else class="file-selected">
              <div class="file-info">
                <i class="file-icon">📄</i>
                <div class="file-details">
                  <p class="file-name">{{ selectedFile.name }}</p>
                  <p class="file-size">{{ formatFileSize(selectedFile.size) }}</p>
                </div>
                <button class="remove-file" @click="removeFile">❌</button>
              </div>
            </div>
          </div>

          <div v-if="selectedFile" class="document-info">
            <div class="form-group">
              <label>文档标题</label>
              <input 
                v-model="documentTitle" 
                type="text" 
                class="form-input"
                placeholder="请输入文档标题">
            </div>
            
            <div class="form-group">
              <label>关联项目（可选）</label>
              <select v-model="selectedProject" class="form-select">
                <option value="">请选择项目</option>
                <option v-for="project in projects" :key="project.id" :value="project.id">
                  {{ project.name }}
                </option>
              </select>
            </div>

            <div class="form-group">
              <label>关联版本（可选）</label>
              <div class="version-select-row">
                <select v-model="selectedVersion" class="form-select version-select">
                  <option value="">不关联版本</option>
                  <option v-for="ver in availableVersions" :key="ver.id" :value="ver.id">
                    {{ ver.name }}{{ ver.is_baseline ? ' (基线)' : '' }}
                  </option>
                </select>
                <button class="quick-create-ver-btn" @click="openQuickCreateVersion(selectedProject)" title="快速新建版本">+</button>
              </div>
            </div>

            <button 
              class="generate-btn" 
              @click="generateFromDocument"
              :disabled="!documentTitle || isGenerating">
              <span v-if="isGenerating">🔄 生成中...</span>
              <span v-else>🚀 生成测试用例</span>
            </button>
          </div>
        </div>
      </div>

      <!-- 分隔线2 -->
      <div class="divider" v-if="!isGenerating && !showResults">
        <span>或</span>
      </div>

      <!-- 需求文档生成区域（后门流程） -->
      <div class="req-doc-section" v-if="!isGenerating && !showResults">
        <div class="req-doc-card">
          <div class="req-doc-header">
            <h2>📋 需求文档生成</h2>
            <p class="req-doc-desc">将原始需求文案整理成结构化 Markdown 文档，再直接喂入 AI 生成测试用例</p>
          </div>

          <!-- 输入方式 Tab 切换 -->
          <div class="rd-tabs" v-if="!reqDoc.markdown">
            <button
              :class="['rd-tab', { active: reqDoc.inputMode === 'text' }]"
              @click="reqDoc.inputMode = 'text'">
              ✏️ 粘贴文字
            </button>
            <button
              :class="['rd-tab', { active: reqDoc.inputMode === 'file' }]"
              @click="reqDoc.inputMode = 'file'">
              📁 上传文件
            </button>
          </div>

          <!-- 文字输入模式 -->
          <div class="form-group rd-text-input" v-if="!reqDoc.markdown && reqDoc.inputMode === 'text'">
            <textarea
              v-model="reqDoc.rawText"
              class="form-textarea"
              rows="7"
              placeholder="粘贴需求文案、产品说明、功能描述等原始文字，AI 将帮你整理成标准格式的需求文档…"></textarea>
          </div>

          <!-- 文件上传模式 -->
          <div class="rd-upload-zone" v-if="!reqDoc.markdown && reqDoc.inputMode === 'file'">
            <!-- 隐藏的文件选择 input（多文件） -->
            <input
              type="file"
              ref="reqDocFileInput"
              @change="handleReqDocFileSelect"
              accept=".pdf,.doc,.docx,.txt,.md"
              multiple
              style="display: none">
            <!-- 隐藏的文件夹选择 input（webkitdirectory） -->
            <input
              type="file"
              ref="reqDocFolderInput"
              @change="handleReqDocFolderSelect"
              accept=".pdf,.doc,.docx,.txt,.md"
              webkitdirectory
              directory
              multiple
              style="display: none">

            <!-- 上传入口（两个入口：文件 / 文件夹） -->
            <div class="rd-upload-entries">
              <div class="rd-drop-zone" @click.stop.prevent="$refs.reqDocFileInput.click()">
                <div class="rd-drop-icon">📄</div>
                <p class="rd-drop-title">选择文件</p>
                <p class="rd-drop-hint">支持 PDF / Word / TXT / MD</p>
              </div>
              <div class="rd-drop-zone rd-folder-zone" @click.stop.prevent="$refs.reqDocFolderInput.click()">
                <div class="rd-drop-icon">📁</div>
                <p class="rd-drop-title">选择文件夹</p>
                <p class="rd-drop-hint">读取文件夹内所有文档合并</p>
              </div>
            </div>

            <!-- 已选文件列表（按文件夹分组） -->
            <div v-if="reqDoc.files.length" class="rd-file-list">
              <template v-for="(group, gIdx) in fileGroups" :key="'g'+gIdx">
                <!-- 文件夹标题行 -->
                <div v-if="group.isFolder" class="rd-folder-header">
                  <span class="rd-folder-icon">📁</span>
                  <span class="rd-folder-name">{{ group.name }}</span>
                  <span class="rd-folder-count">{{ group.items.length }} 个文件</span>
                  <button class="rd-folder-clear" @click="removeFolder(gIdx)" :disabled="group.items.some(f => f.extracting)">✕</button>
                </div>
                <!-- 文件条目 -->
                <div
                  v-for="(f, i) in group.items"
                  :key="'gf'+gIdx+'f'+i"
                  :class="['rd-file-item', { 'rd-file-sub': group.isFolder }]">
                  <span class="rd-file-icon">📄</span>
                  <span class="rd-file-name" :title="f.file.webkitRelativePath || f.file.name">{{ f.file.name }}</span>
                  <span v-if="f.extracting" class="rd-extract-status extracting">⏳ 提取中…</span>
                  <span v-else-if="f.error" class="rd-extract-status error" :title="f.error">❌ 失败</span>
                  <span v-else-if="f.isImagePdf" class="rd-extract-status image-pdf">📷 图片型PDF · AI视觉识别</span>
                  <span v-else-if="f.extracted" class="rd-extract-status done">✅ 文字已提取</span>
                  <button class="rd-file-clear" @click="removeReqDocFile(gIdx, i)" :disabled="f.extracting">✕</button>
                </div>
              </template>

              <!-- 无文件夹归属的单独文件 -->
              <template v-if="flatFiles.length && fileGroups.some(g => g.isFolder)">
                <div class="rd-folder-header">
                  <span class="rd-folder-icon">📄</span>
                  <span class="rd-folder-name">单独文件</span>
                  <span class="rd-folder-count">{{ flatFiles.length }} 个</span>
                </div>
              </template>
              <div
                v-for="(f, i) in flatFiles"
                :key="'f'+i"
                :class="['rd-file-item', { 'rd-file-sub': fileGroups.some(g => g.isFolder) }]">
                <span class="rd-file-icon">📄</span>
                <span class="rd-file-name">{{ f.file.name }}</span>
                <span v-if="f.extracting" class="rd-extract-status extracting">⏳ 提取中…</span>
                <span v-else-if="f.error" class="rd-extract-status error" :title="f.error">❌ 失败</span>
                <span v-else-if="f.isImagePdf" class="rd-extract-status image-pdf">📷 图片型PDF · AI视觉识别</span>
                <span v-else-if="f.extracted" class="rd-extract-status done">✅ 文字已提取</span>
                <button class="rd-file-clear" @click="removeFlatFile(i)" :disabled="f.extracting">✕</button>
              </div>
            </div>
          </div>

          <!-- 操作按钮（未生成时显示） -->
          <div class="req-doc-actions" v-if="!reqDoc.markdown">
            <button
              class="req-doc-btn primary"
              @click="generateReqDoc"
              :disabled="!canGenerateReqDoc || reqDoc.isGenerating || reqDoc.isExtracting">
              <span v-if="reqDoc.isExtracting">⏳ 文件提取中…</span>
              <span v-else-if="reqDoc.isGenerating && hasImagePdfFiles">👁️ AI 视觉识别中…</span>
              <span v-else-if="reqDoc.isGenerating">⏳ AI 生成中…</span>
              <span v-else-if="hasImagePdfFiles">👁️ AI 视觉识别并生成文档</span>
              <span v-else>✨ AI 自动生成文档</span>
            </button>
            <button
              class="req-doc-btn secondary"
              @click="getReqDocTemplate"
              :disabled="reqDoc.isGenerating || reqDoc.isExtracting">
              📄 使用空白模板
            </button>
          </div>

          <!-- 生成后的编辑区 -->
          <div v-if="reqDoc.markdown" class="req-doc-editor">
            <div class="editor-toolbar">
              <span class="editor-label">📝 需求文档（可直接编辑）</span>
              <div class="editor-toolbar-actions">
                <button class="toolbar-btn" @click="toggleReqDocPreview">
                  {{ reqDoc.showPreview ? '✏️ 编辑' : '👁️ 预览' }}
                </button>
                <button class="toolbar-btn danger" @click="resetReqDoc">
                  🔄 重新生成
                </button>
              </div>
            </div>

            <!-- 编辑模式 -->
            <textarea
              v-if="!reqDoc.showPreview"
              v-model="reqDoc.markdown"
              class="req-doc-textarea"
              rows="18"
              spellcheck="false"></textarea>

            <!-- 预览模式 -->
            <div
              v-else
              class="req-doc-preview markdown-body"
              v-html="formatMarkdown(reqDoc.markdown)"></div>

            <!-- 项目选择 + 版本选择 + 生成按钮 -->
            <div class="req-doc-generate-row">
              <div class="form-group project-select-inline">
                <label>关联项目（可选）</label>
                <select v-model="reqDoc.selectedProject" class="form-select">
                  <option value="">请选择项目</option>
                  <option v-for="project in projects" :key="project.id" :value="project.id">
                    {{ project.name }}
                  </option>
                </select>
              </div>
              <div class="form-group project-select-inline">
                <label>关联版本（可选）</label>
                <div class="version-select-row">
                  <select v-model="selectedVersion" class="form-select version-select">
                    <option value="">不关联版本</option>
                    <option v-for="ver in availableVersions" :key="ver.id" :value="ver.id">
                      {{ ver.name }}{{ ver.is_baseline ? ' (基线)' : '' }}
                    </option>
                  </select>
                  <button class="quick-create-ver-btn" @click="openQuickCreateVersion(reqDoc.selectedProject)" title="快速新建版本">+</button>
                </div>
              </div>
              <button
                class="generate-manual-btn use-req-doc-btn"
                @click="useReqDocForGeneration"
                :disabled="!reqDoc.markdown.trim() || isGenerating">
                🚀 用此文档生成测试用例
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 历史文档面板 -->
      <div class="history-section" v-if="!isGenerating && !showResults">
        <div class="history-card">
          <div class="history-header">
            <h2>📚 历史需求文档</h2>
            <div class="history-version-row">
              <span class="history-count" v-if="reqDocHistoryLoaded" style="margin-right:12px">{{ reqDocHistory.length }} 条记录</span>
              <label style="font-size:0.8rem;color:#64748b;margin-right:6px;white-space:nowrap">关联版本：</label>
              <select v-model="selectedVersion" class="form-select version-select" style="width:160px;font-size:0.8rem;padding:4px 8px">
                <option value="">不关联版本</option>
                <option v-for="ver in availableVersions" :key="ver.id" :value="ver.id">
                  {{ ver.name }}{{ ver.is_baseline ? ' (基线)' : '' }}
                </option>
              </select>
              <button class="quick-create-ver-btn" @click="openQuickCreateVersion(null)" title="快速新建版本" style="margin-left:4px">+</button>
            </div>
          </div>
          <!-- 加载中 -->
          <div v-if="!reqDocHistoryLoaded" class="history-loading">
            <span class="loading-spinner"></span> 加载中...
          </div>
          <!-- 加载失败 -->
          <div v-else-if="reqDocHistoryError" class="history-error">
            ⚠️ 加载失败，<a href="javascript:void(0)" @click="loadReqDocHistory">点击重试</a>
          </div>
          <!-- 空列表 -->
          <div v-else-if="reqDocHistory.length === 0" class="history-empty">
            📭 暂无历史需求文档，<br>在下方生成需求文档后自动保存到此处
          </div>
          <!-- 有数据 -->
          <div v-else class="history-list">
            <div
              v-for="doc in reqDocHistory"
              :key="doc.id"
              class="history-item">
              <div class="history-item-main">
                <div class="history-item-title">{{ doc.title || '未命名文档' }}</div>
                <div class="history-item-meta">
                  <span class="history-source">
                    <span v-if="doc.source_type === 'file'">📁</span>
                    <span v-else-if="doc.source_type === 'text'">✏️</span>
                    <span v-else>📄</span>
                    {{ doc.source_type_display }}
                  </span>
                  <span class="history-time">{{ formatDateTime(doc.created_at) }}</span>
                </div>
              </div>
              <div class="history-item-actions">
                <button class="history-btn view" @click="viewHistoryDoc(doc)" title="查看文档">
                  👁️ 查看
                </button>
                <button class="history-btn edit" @click="editHistoryDoc(doc)" title="编辑文档">
                  ✏️ 编辑
                </button>
                <button class="history-btn generate" @click="generateFromHistoryDoc(doc)" title="一键提交生成测试用例">
                  🚀 生成用例
                </button>
                <button class="history-btn del" @click="deleteReqDocHistory(doc)" title="删除此文档">
                  🗑️ 删除
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 历史文档查看/编辑弹窗 -->
      <div v-if="showHistoryPreview" class="modal-overlay" @click.self="closePreview">
        <div class="history-preview-modal">
          <div class="preview-header">
            <h3 v-if="!isEditingDoc">{{ viewingDoc?.title || '文档详情' }}</h3>
            <input v-else v-model="editingTitle" class="edit-title-input" placeholder="文档标题" />
            <button class="preview-close" @click="closePreview">✕</button>
          </div>
          <!-- 预览模式 -->
          <div v-if="!isEditingDoc" class="preview-body markdown-body" v-html="formatMarkdown(viewingDoc?.markdown_content || '')"></div>
          <!-- 编辑模式 -->
          <div v-else class="edit-body">
            <textarea v-model="editingMarkdown" class="edit-textarea" placeholder="在此编辑 Markdown 需求文档..."></textarea>
          </div>
          <div class="preview-actions">
            <template v-if="!isEditingDoc">
              <button class="history-btn edit" @click="enterEditMode">✏️ 编辑修改</button>
              <button class="generate-manual-btn" @click="generateFromPreviewDoc" style="width:auto;padding:10px 28px;">
                🚀 用此文档生成测试用例
              </button>
            </template>
            <template v-else>
              <button class="toolbar-btn" @click="cancelEdit">❌ 取消编辑</button>
              <button class="generate-manual-btn" @click="saveDocEdit" :disabled="editingSaving || !editingMarkdown.trim()" style="width:auto;padding:10px 28px;">
                {{ editingSaving ? '保存中...' : '✅ 保存修改' }}
              </button>
            </template>
          </div>
        </div>
      </div>

      <!-- 生成用例确认弹窗 -->
      <div v-if="showGenerateConfirm" class="modal-overlay" @click.self="showGenerateConfirm = false">
        <div class="generate-confirm-modal">
          <div class="quick-version-header">
            <h3>🚀 生成测试用例</h3>
            <button class="preview-close" @click="showGenerateConfirm = false">✕</button>
          </div>
          <div class="quick-version-body">
            <p style="color:#666;margin-bottom:16px;font-size:0.9rem">
              请确认关联的项目和版本号，生成的测试用例将绑定到所选版本。
            </p>
            <div class="form-group">
              <label>生成模式 <span class="required">*</span></label>
              <div class="generation-mode-selector">
                <label 
                  v-for="mode in generationModes" 
                  :key="mode.value"
                  class="mode-option"
                  :class="{ active: generateConfirmForm.generation_mode === mode.value }"
                >
                  <input type="radio" v-model="generateConfirmForm.generation_mode" :value="mode.value" class="mode-radio" />
                  <span class="mode-icon">{{ mode.icon }}</span>
                  <span class="mode-name">{{ mode.label }}</span>
                  <span class="mode-desc">{{ mode.desc }}</span>
                </label>
              </div>
            </div>
            <div class="form-group">
              <label>归属项目 <span class="required">*</span></label>
              <select v-model="generateConfirmForm.project_id" class="form-select" @change="onConfirmProjectChange">
                <option :value="null">请选择项目</option>
                <option v-for="project in projects" :key="project.id" :value="project.id">
                  {{ project.name }}
                </option>
              </select>
            </div>
            <div class="form-group">
              <label>关联版本 <span class="required">*</span></label>
              <select v-model="generateConfirmForm.version_id" class="form-select">
                <option :value="null">请选择版本</option>
                <option v-for="ver in generateConfirmVersions" :key="ver.id" :value="ver.id">
                  {{ ver.name }}{{ ver.is_baseline ? ' (基线)' : '' }}
                </option>
              </select>
              <button class="quick-create-ver-btn" style="margin-left:8px;vertical-align:middle" @click="openQuickCreateVersion(generateConfirmForm.project_id)" title="快速新建版本">+</button>
            </div>
            <div class="form-group">
              <label>功能模块</label>
              <select v-model="generateConfirmForm.feature_module_id" class="form-select" @change="onConfirmFeatureModuleChange">
                <option :value="null">请选择功能模块</option>
                <option v-for="fm in generateConfirmFeatureModules" :key="fm.id" :value="fm.id">
                  {{ fm.name }}
                </option>
              </select>
              <button class="quick-create-ver-btn" style="margin-left:8px;vertical-align:middle" @click="openQuickCreateFeatureModule(generateConfirmForm.project_id)" title="快速新建功能模块">+</button>
            </div>
            <div class="form-group">
              <label>测试点</label>
              <select v-model="generateConfirmForm.test_point_id" class="form-select">
                <option :value="null">请选择测试点</option>
                <option v-for="tp in generateConfirmTestPoints" :key="tp.id" :value="tp.id">
                  {{ tp.name }}
                </option>
              </select>
              <button class="quick-create-ver-btn" style="margin-left:8px;vertical-align:middle" @click="openQuickCreateTestPoint(generateConfirmForm.feature_module_id)" :disabled="!generateConfirmForm.feature_module_id" title="快速新建测试点">+</button>
            </div>
          </div>
          <div class="quick-version-actions">
            <button class="toolbar-btn" @click="showGenerateConfirm = false">取消</button>
            <button class="generate-manual-btn" @click="confirmStartGeneration" :disabled="!canConfirmGenerate || isGenerating" style="width:auto;padding:8px 24px;">
              {{ isGenerating ? '生成中...' : '✅ 确认并开始生成' }}
            </button>
          </div>
        </div>
      </div>

      <!-- 快速创建版本弹窗 -->
      <div v-if="showQuickCreateVersion" class="modal-overlay" @click.self="showQuickCreateVersion = false">
        <div class="quick-version-modal">
          <div class="quick-version-header">
            <h3>⚡ 快速新建版本</h3>
            <button class="preview-close" @click="showQuickCreateVersion = false">✕</button>
          </div>
          <div class="quick-version-body">
            <div class="form-group">
              <label>版本名称 <span class="required">*</span></label>
              <input v-model="quickVersionForm.name" class="form-input" placeholder="例如：v2.1.0、2026-Q3" @keyup.enter="saveQuickVersion" />
            </div>
            <div class="form-group">
              <label>关联项目</label>
              <select v-model="quickVersionForm.project_id" class="form-select">
                <option :value="null">请选择项目</option>
                <option v-for="project in projects" :key="project.id" :value="project.id">
                  {{ project.name }}
                </option>
              </select>
            </div>
            <div class="form-group">
              <label>版本描述</label>
              <input v-model="quickVersionForm.description" class="form-input" placeholder="可选填版本说明" />
            </div>
            <div class="form-group">
              <label class="checkbox-label">
                <input type="checkbox" v-model="quickVersionForm.is_baseline" />
                设为基线版本
              </label>
            </div>
          </div>
          <div class="quick-version-actions">
            <button class="toolbar-btn" @click="showQuickCreateVersion = false">取消</button>
            <button class="generate-manual-btn" @click="saveQuickVersion" :disabled="!quickVersionForm.name.trim() || quickVersionSaving" style="width:auto;padding:8px 24px;">
              {{ quickVersionSaving ? '保存中...' : '✅ 创建' }}
            </button>
          </div>
        </div>
      </div>

      <!-- 快速创建功能模块弹窗 -->
      <div v-if="showQuickCreateFeatureModule" class="modal-overlay" @click.self="showQuickCreateFeatureModule = false">
        <div class="quick-version-modal">
          <div class="quick-version-header">
            <h3>⚡ 快速新建功能模块</h3>
            <button class="preview-close" @click="showQuickCreateFeatureModule = false">✕</button>
          </div>
          <div class="quick-version-body">
            <div class="form-group">
              <label>模块名称 <span class="required">*</span></label>
              <input v-model="quickFeatureModuleForm.name" class="form-input" placeholder="例如：用户登录、搜索功能" maxlength="100" @keyup.enter="saveQuickFeatureModule" />
            </div>
            <div class="form-group">
              <label>关联项目 <span class="required">*</span></label>
              <select v-model="quickFeatureModuleForm.project_id" class="form-select">
                <option :value="null">请选择项目</option>
                <option v-for="project in projects" :key="project.id" :value="project.id">
                  {{ project.name }}
                </option>
              </select>
            </div>
            <div class="form-group">
              <label>模块描述</label>
              <input v-model="quickFeatureModuleForm.description" class="form-input" placeholder="可选填模块描述" />
            </div>
          </div>
          <div class="quick-version-actions">
            <button class="toolbar-btn" @click="showQuickCreateFeatureModule = false">取消</button>
            <button class="generate-manual-btn" @click="saveQuickFeatureModule" :disabled="!quickFeatureModuleForm.name.trim() || !quickFeatureModuleForm.project_id || quickFeatureModuleSaving" style="width:auto;padding:8px 24px;">
              {{ quickFeatureModuleSaving ? '保存中...' : '✅ 创建' }}
            </button>
          </div>
        </div>
      </div>

      <!-- 快速创建测试点弹窗 -->
      <div v-if="showQuickCreateTestPoint" class="modal-overlay" @click.self="showQuickCreateTestPoint = false">
        <div class="quick-version-modal">
          <div class="quick-version-header">
            <h3>🎯 快速新建测试点</h3>
            <button class="preview-close" @click="showQuickCreateTestPoint = false">✕</button>
          </div>
          <div class="quick-version-body">
            <div class="form-group">
              <label>所属功能模块</label>
              <input :value="generateConfirmFeatureModules.find(fm => fm.id === generateConfirmForm.feature_module_id)?.name || ''" class="form-input" disabled />
            </div>
            <div class="form-group">
              <label>测试点名称 <span class="required">*</span></label>
              <input v-model="quickTestPointForm.name" class="form-input" placeholder="例如：登录按钮点击、密码输入校验" maxlength="200" @keyup.enter="saveQuickTestPoint" />
            </div>
            <div class="form-group">
              <label>测试点描述</label>
              <input v-model="quickTestPointForm.description" class="form-input" placeholder="可选填测试点描述" />
            </div>
          </div>
          <div class="quick-version-actions">
            <button class="toolbar-btn" @click="showQuickCreateTestPoint = false">取消</button>
            <button class="generate-manual-btn" @click="saveQuickTestPoint" :disabled="!quickTestPointForm.name.trim() || quickTestPointSaving" style="width:auto;padding:8px 24px;">
              {{ quickTestPointSaving ? '保存中...' : '✅ 创建' }}
            </button>
          </div>
        </div>
      </div>

      <!-- 生成进度和结果 -->
      <div v-if="isGenerating || showResults" class="generation-progress">
        <div class="progress-card">
          <h3>
            🤖 AI正在为您生成测试用例
            <span class="current-mode-badge">
              (当前模式: {{ globalOutputMode === 'stream' ? '⚡实时流式输出' : '📄完整输出' }})
            </span>
          </h3>
          <div class="progress-info">
            <div class="progress-item">
              <span class="label">任务ID:</span>
              <span class="value">{{ currentTaskId || '准备中...' }}</span>
            </div>
            <div class="progress-item">
              <span class="label">当前状态:</span>
              <span class="value">{{ showResults ? '生成完成' : progressText }}</span>
            </div>
          </div>

          <!-- 流式内容实时显示区域 -->
          <div v-if="streamedContent" class="stream-content-display">
            <div class="stream-header">
              <span class="stream-title">✍️ 实时生成内容</span>
              <span class="stream-status">{{ streamedContent.length }} 字符</span>
            </div>
            <div class="stream-content" v-html="formatMarkdown(streamedContent)"></div>
          </div>

          <!-- 评审内容显示区域 -->
          <div v-if="streamedReviewContent" class="stream-content-display" style="margin-top: 15px;">
            <div class="stream-header">
              <span class="stream-title">📝 AI评审意见</span>
              <span class="stream-status">{{ streamedReviewContent.length }} 字符</span>
            </div>
            <div class="stream-content" v-html="formatMarkdown(streamedReviewContent)"></div>
          </div>

          <!-- 最终版用例显示区域 -->
          <div v-if="finalTestCases" class="stream-content-display" style="margin-top: 15px;">
            <div class="stream-header">
              <span class="stream-title">
                🎯 最终版用例
                <span v-if="isGenerating" class="streaming-indicator">🔄 正在生成...</span>
              </span>
              <span class="stream-status">{{ finalTestCases.length }} 字符</span>
            </div>
            <div class="stream-content final-testcases" v-html="formatMarkdown(finalTestCases)"></div>
          </div>

          <div class="progress-steps">
            <div class="step" :class="{ active: currentStep >= 1 }">
              <span class="step-number">1</span>
              <span class="step-text">需求分析</span>
            </div>
            <div class="step" :class="{ active: currentStep >= 2 }">
              <span class="step-number">2</span>
              <span class="step-text">用例编写</span>
            </div>
            <div v-if="showReviewStep" class="step" :class="{ active: currentStep >= 3 }">
              <span class="step-number">3</span>
              <span class="step-text">用例评审</span>
            </div>
            <div class="step" :class="{ active: currentStep >= (showReviewStep ? 4 : 3) }">
              <span class="step-number">{{ showReviewStep ? 4 : 3 }}</span>
              <span class="step-text">完成</span>
            </div>
          </div>

          <!-- 任务完成后的操作按钮 -->
          <div v-if="showResults" class="completion-actions">
            <button class="download-btn" @click="downloadTestCases">
              <span>📥 下载测试用例</span>
            </button>
            <button class="save-btn" @click="saveToTestCaseRecords">
              <span>💾 保存到用例库</span>
            </button>
            <button class="new-generation-btn" @click="resetGeneration">
              <span>📝 生成新用例</span>
            </button>
          </div>
          <button v-else class="cancel-generation-btn" @click="cancelGeneration">
            取消生成
          </button>
        </div>
      </div>

      <!-- 旧的生成结果区域已废弃，保留用于兼容 -->
      <!-- 现在使用流式显示区域 + 最终版用例区域 -->
      <div v-if="false && showResults && generationResult" class="generation-result">
        <div class="result-header">
          <h2>✅ 测试用例生成完成</h2>
          <div class="result-summary">
            <span class="summary-item">
              📊 任务ID: {{ generationResult.task_id }}
            </span>
            <span class="summary-item">
              ⏱️ 生成时间: {{ formatDateTime(generationResult.completed_at) }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '@/utils/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as XLSX from 'xlsx'
import { useUserStore } from '@/stores/user'

export default {
  name: 'RequirementAnalysisView',
  data() {
    return {
      // 全局输出模式设置
      globalOutputMode: 'stream',  // 默认使用流式输出

      // 手动输入需求
      manualInput: {
        title: '',
        description: '',
        selectedProject: ''
      },

      // 文件上传
      selectedFile: null,
      documentTitle: '',
      selectedProject: '',
      selectedVersion: '',
      selectedFeatureModule: '',
      projects: [],
      allVersions: [],
      allFeatureModules: [],
      // 快速创建版本
      showQuickCreateVersion: false,
      quickVersionSaving: false,
      quickVersionForm: {
        name: '',
        project_id: null,
        description: '',
        is_baseline: false
      },
      // 快速创建功能模块
      showQuickCreateFeatureModule: false,
      quickFeatureModuleSaving: false,
      quickFeatureModuleForm: {
        name: '',
        project_id: null,
        description: ''
      },
      // 快速创建测试点
      showQuickCreateTestPoint: false,
      quickTestPointSaving: false,
      quickTestPointForm: {
        name: '',
        feature_module_id: null,
        description: ''
      },
      // 测试点相关
      moduleTestPoints: [],
      // 生成确认弹窗
      showGenerateConfirm: false,
      generateConfirmForm: {
        project_id: null,
        version_id: null,
        feature_module_id: null,
        test_point_id: null,
        generation_mode: 'smart'
      },
      generationModes: [
        { value: 'smart', label: '智能', icon: '🤖', desc: 'AI评估' },
        { value: 'quick', label: '快速', icon: '⚡', desc: '10~20条' },
        { value: 'standard', label: '标准', icon: '📋', desc: '20~40条' },
        { value: 'comprehensive', label: '全面', icon: '🔬', desc: '全量覆盖' }
      ],
      pendingGeneratePayload: null,
      isDragOver: false,

      // 生成状态
      isGenerating: false,
      currentTaskId: null,
      progressText: '准备开始生成...',
      currentStep: 0,
      pollInterval: null,
      eventSource: null,  // SSE连接
      streamedContent: '',  // 流式接收的内容
      streamedReviewContent: '',  // 流式接收的评审内容
      finalTestCases: '',  // 最终版用例
      hasShownCompletionMessage: false,  // 是否已经显示过完成消息
      showReviewStep: true,  // 是否显示评审步骤（根据生成配置决定）

      // 生成结果
      showResults: false,
      generationResult: null,

      // AI配置状态
      configStatus: {
        overall_status: 'unknown',
        message: '',
        writer_model: {
          configured: false,
          enabled: false,
          name: null,
          provider: null,
          id: null,
          required: true
        },
        writer_prompt: {
          configured: false,
          enabled: false,
          name: null,
          id: null,
          required: true
        },
        reviewer_model: {
          configured: false,
          enabled: false,
          name: null,
          id: null,
          required: true
        },
        reviewer_prompt: {
          configured: false,
          enabled: false,
          name: null,
          id: null,
          required: true
        },
        generation_config: {
          configured: false,
          enabled: false,
          name: null,
          id: null,
          required: true,
          default_output_mode: null
        }
      },
      showConfigGuide: false,
      checkingConfig: true,
      modalKey: 0,  // 用于强制重新渲染弹窗

      // 历史需求文档
      reqDocHistory: [],
      reqDocHistoryLoaded: false,
      reqDocHistoryError: false,
      showHistoryPreview: false,
      viewingDoc: null,
      // 编辑模式
      isEditingDoc: false,
      editingMarkdown: '',
      editingTitle: '',
      editingSaving: false,

      // 需求文档生成（后门流程）
      reqDoc: {
        inputMode: 'text',      // 'text' | 'file'
        rawText: '',
        files: [],              // [{ file, documentId, isImagePdf, extracting, extracted, folder?, relativePath? }]
        isExtracting: false,    // 是否有文件仍在提取中（汇总）
        markdown: '',
        isGenerating: false,
        showPreview: false,
        selectedProject: ''
      }
    }
  },
  
  computed: {
    canGenerateManual() {
      return this.manualInput.title.trim() && 
             this.manualInput.description.trim() && 
             this.manualInput.description.length <= 2000
    },
    canGenerateReqDoc() {
      if (this.reqDoc.inputMode === 'text') return !!this.reqDoc.rawText.trim()
      if (!this.reqDoc.files.length) return false
      return this.reqDoc.files.every(f => f.extracted || f.isImagePdf)
    },
    hasImagePdfFiles() {
      return this.reqDoc.files.some(f => f.isImagePdf)
    },
    // 按文件夹分组
    fileGroups() {
      const groups = []
      const seen = new Set()
      for (const f of this.reqDoc.files) {
        if (!f.folder) continue
        if (seen.has(f.folder)) continue
        seen.add(f.folder)
        groups.push({
          isFolder: true,
          name: f.folder,
          items: this.reqDoc.files.filter(x => x.folder === f.folder)
        })
      }
      return groups
    },
    // 无文件夹归属的单独文件
    flatFiles() {
      return this.reqDoc.files.filter(f => !f.folder)
    },
    availableVersions() {
      return this.allVersions
    },
    // 生成确认弹窗的版本列表（根据选择的项目过滤）
    generateConfirmVersions() {
      if (!this.generateConfirmForm.project_id) {
        return this.allVersions
      }
      return this.allVersions.filter(v =>
        !v.projects || v.projects.length === 0 || v.projects.some(p => p.id === this.generateConfirmForm.project_id)
      )
    },
    generateConfirmFeatureModules() {
      if (!this.generateConfirmForm.project_id) {
        return this.allFeatureModules || []
      }
      if (!this.allFeatureModules) return []
      return this.allFeatureModules.filter(fm => fm.project?.id === this.generateConfirmForm.project_id)
    },
    generateConfirmTestPoints() {
      if (!this.generateConfirmForm.feature_module_id) return []
      return this.moduleTestPoints || []
    },
    // 是否可以确认生成
    canConfirmGenerate() {
      return this.generateConfirmForm.project_id && this.generateConfirmForm.version_id && this.pendingGeneratePayload
    }
  },
  
  mounted() {
    this.loadProjects()
    this.loadVersions()
    this.loadFeatureModules()
    this.checkConfigStatus()
    this.loadReqDocHistory()
  },

  activated() {
    // 当从其他页面返回时，重新检查配置状态
    // 立即隐藏弹窗和遮罩层，强制重新渲染
    this.showConfigGuide = false
    this.checkingConfig = true
    this.modalKey += 1  // 改变key值，强制重新渲染弹窗

    // 延迟检查配置，确保页面完全加载后再显示弹窗
    setTimeout(async () => {
      await this.checkConfigStatus()
    }, 200)

    // 刷新历史文档列表
    this.loadReqDocHistory()
  },

  beforeUnmount() {
    if (this.pollInterval) {
      clearInterval(this.pollInterval)
    }
    // 停止token自动刷新定时器
    const userStore = useUserStore()
    userStore.stopAutoRefresh()
  },
  
  methods: {
    async loadProjects() {
      try {
        const response = await api.get('/projects/')
        this.projects = response.data.results || response.data
      } catch (error) {
        console.error('加载项目失败:', error)
      }
    },

    async loadVersions() {
      try {
        const response = await api.get('/versions/')
        this.allVersions = response.data.results || response.data || []
      } catch (error) {
        console.error('加载版本失败:', error)
        this.allVersions = []
      }
    },

    async loadFeatureModules() {
      try {
        const response = await api.get('/feature-modules/')
        this.allFeatureModules = response.data.results || response.data || []
      } catch (error) {
        console.error('加载功能模块失败:', error)
        this.allFeatureModules = []
      }
    },

    async loadModuleTestPoints(moduleId) {
      if (!moduleId) {
        this.moduleTestPoints = []
        return
      }
      try {
        const response = await api.get(`/feature-modules/modules/${moduleId}/test-points/`)
        this.moduleTestPoints = response.data || []
      } catch (error) {
        console.error('加载测试点失败:', error)
        this.moduleTestPoints = []
      }
    },

    openQuickCreateVersion(projectId) {
      this.showQuickCreateVersion = true
      this.quickVersionForm = {
        name: '',
        project_id: projectId || null,
        description: '',
        is_baseline: false
      }
      // 聚焦到名称输入框
      this.$nextTick(() => {
        const input = document.querySelector('.quick-version-body .form-input')
        if (input) input.focus()
      })
    },

    async saveQuickVersion() {
      const name = this.quickVersionForm.name.trim()
      if (!name) {
        ElMessage.warning('请输入版本名称')
        return
      }
      if (!this.quickVersionForm.project_id) {
        ElMessage.warning('请选择关联项目')
        return
      }
      this.quickVersionSaving = true
      try {
        const payload = {
          name: name,
          description: this.quickVersionForm.description.trim(),
          is_baseline: this.quickVersionForm.is_baseline,
          project_ids: [this.quickVersionForm.project_id]
        }
        const response = await api.post('/versions/', payload)
        // 刷新版本列表
        await this.loadVersions()
        // 自动选中新创建的版本
        this.selectedVersion = response.data.id
        ElMessage.success(`版本「${name}」创建成功`)
        this.showQuickCreateVersion = false
      } catch (error) {
        if (error.response?.data) {
          const errors = Object.values(error.response.data).flat()
          ElMessage.error(errors[0] || '创建版本失败')
        } else {
          ElMessage.error('创建版本失败')
        }
      } finally {
        this.quickVersionSaving = false
      }
    },

    openQuickCreateFeatureModule(projectId) {
      this.showQuickCreateFeatureModule = true
      this.quickFeatureModuleForm = {
        name: '',
        project_id: projectId || null,
        description: ''
      }
      this.$nextTick(() => {
        const input = document.querySelector('.quick-version-body .form-input')
        if (input) input.focus()
      })
    },

    async saveQuickFeatureModule() {
      const name = this.quickFeatureModuleForm.name.trim()
      if (!name) {
        ElMessage.warning('请输入模块名称')
        return
      }
      if (!this.quickFeatureModuleForm.project_id) {
        ElMessage.warning('请选择关联项目')
        return
      }
      this.quickFeatureModuleSaving = true
      try {
        const response = await api.post('/feature-modules/', {
          name: name,
          description: this.quickFeatureModuleForm.description.trim(),
          project_id: this.quickFeatureModuleForm.project_id
        })
        // 刷新功能模块列表
        await this.loadFeatureModules()
        // 自动选中新创建的功能模块
        this.generateConfirmForm.feature_module_id = response.data.id
        ElMessage.success(`功能模块「${name}」创建成功`)
        this.showQuickCreateFeatureModule = false
      } catch (error) {
        if (error.response?.data) {
          const detail = error.response.data.detail || error.response.data.name || '创建功能模块失败'
          ElMessage.error(Array.isArray(detail) ? detail[0] : detail)
        } else {
          ElMessage.error('创建功能模块失败')
        }
      } finally {
        this.quickFeatureModuleSaving = false
      }
    },

    openQuickCreateTestPoint(moduleId) {
      this.showQuickCreateTestPoint = true
      this.quickTestPointForm = {
        name: '',
        feature_module_id: moduleId || null,
        description: ''
      }
      this.$nextTick(() => {
        const input = document.querySelectorAll('.quick-version-body .form-input')[1]
        if (input) input.focus()
      })
    },

    async saveQuickTestPoint() {
      const name = this.quickTestPointForm.name.trim()
      if (!name) {
        ElMessage.warning('请输入测试点名称')
        return
      }
      if (!this.quickTestPointForm.feature_module_id) {
        ElMessage.warning('请先选择功能模块')
        return
      }
      this.quickTestPointSaving = true
      try {
        const response = await api.post('/feature-modules/test-points/', {
          name: name,
          description: this.quickTestPointForm.description.trim(),
          feature_module_id: this.quickTestPointForm.feature_module_id
        })
        // 刷新当前模块的测试点列表
        await this.loadModuleTestPoints(this.quickTestPointForm.feature_module_id)
        // 自动选中新创建的测试点
        this.generateConfirmForm.test_point_id = response.data.id
        ElMessage.success(`测试点「${name}」创建成功`)
        this.showQuickCreateTestPoint = false
      } catch (error) {
        if (error.response?.data) {
          const detail = error.response.data.detail || error.response.data.name || '创建测试点失败'
          ElMessage.error(Array.isArray(detail) ? detail[0] : detail)
        } else {
          ElMessage.error('创建测试点失败')
        }
      } finally {
        this.quickTestPointSaving = false
      }
    },

    async checkConfigStatus() {
      try {
        this.checkingConfig = true
        const response = await api.get('/requirement-analysis/api/config/check/')
        this.configStatus = response.data

        // 判断逻辑：只有当"用例编写模型"、"用例评审模型"、"用例编写提示词"和"用例评审提示词"都配置且启用时，才不显示弹框
        const writerModelReady = response.data.writer_model &&
                                response.data.writer_model.configured &&
                                response.data.writer_model.enabled

        const reviewerModelReady = response.data.reviewer_model &&
                                  response.data.reviewer_model.configured &&
                                  response.data.reviewer_model.enabled

        const writerPromptReady = response.data.writer_prompt &&
                                 response.data.writer_prompt.configured &&
                                 response.data.writer_prompt.enabled

        const reviewerPromptReady = response.data.reviewer_prompt &&
                                   response.data.reviewer_prompt.configured &&
                                   response.data.reviewer_prompt.enabled

        // 检查生成行为配置
        const generationConfigReady = response.data.generation_config &&
                                      response.data.generation_config.configured

        // 根据生成配置的enable_auto_review决定是否显示评审步骤（无论其他配置状态，始终读取）
        if (response.data.generation_config && response.data.generation_config.enable_auto_review !== null) {
          this.showReviewStep = response.data.generation_config.enable_auto_review
        } else {
          this.showReviewStep = true  // 默认显示
        }

        // 只有五项都准备好时才不显示引导弹框
        if (writerModelReady && reviewerModelReady && writerPromptReady && reviewerPromptReady && generationConfigReady) {
          this.showConfigGuide = false

          // 如果生成配置允许用户修改，则使用配置的默认输出模式
          if (response.data.generation_config && response.data.generation_config.default_output_mode) {
            this.globalOutputMode = response.data.generation_config.default_output_mode
          }
        } else {
          this.showConfigGuide = true
        }
      } catch (error) {
        console.error('检查配置状态失败:', error)
        // 如果检查失败，默认不显示引导，避免影响正常使用
        this.showConfigGuide = false
        this.checkingConfig = false
      } finally {
        this.checkingConfig = false
      }
    },

    goToConfig() {
      // 智能判断跳转目标：优先跳转到未配置/未启用的页面
      // 优先级：必需配置 > 可选配置，提示词 > 模型

      // 0. 首先检查生成行为配置（generation_config）
      if (!this.configStatus.generation_config || !this.configStatus.generation_config.configured) {
        this.$router.push('/configuration/generation-config')
        return
      }

      // 1. 优先检查必需的提示词配置（writer_prompt）
      if (!this.configStatus.writer_prompt.configured || !this.configStatus.writer_prompt.enabled) {
        this.$router.push('/configuration/prompt-config')
        return
      }

      // 2. 检查必需的模型配置（writer_model）
      if (!this.configStatus.writer_model.configured || !this.configStatus.writer_model.enabled) {
        this.$router.push('/configuration/ai-model')
        return
      }

      // 3. 检查可选的评审提示词（reviewer_prompt）
      if (!this.configStatus.reviewer_prompt.configured || !this.configStatus.reviewer_prompt.enabled) {
        this.$router.push('/configuration/prompt-config')
        return
      }

      // 4. 检查可选的评审模型（reviewer_model）
      if (!this.configStatus.reviewer_model.configured || !this.configStatus.reviewer_model.enabled) {
        this.$router.push('/configuration/ai-model')
        return
      }

      // 默认跳转到生成行为配置
      this.$router.push('/configuration/generation-config')
    },

    goToPromptConfig() {
      this.$router.push('/configuration/prompt-config')
    },

    getConfigItemClass(configKey) {
      const config = this.configStatus[configKey]
      if (config.enabled) {
        return 'status-enabled'
      } else if (config.configured) {
        return 'status-disabled'
      } else {
        return 'status-unconfigured'
      }
    },

    getStatusIcon(configKey) {
      const config = this.configStatus[configKey]
      if (config.enabled) {
        // 绿色对号
        return '<path d="M512 64C264.6 64 64 264.6 64 512s200.6 448 448 448 448-200.6 448-448S759.4 64 512 64zm193.5 301.7l-210.6 292c-12.7 17.7-39 17.7-51.7 0L318.5 484.9c-3.8-5.3 0-12.7 6.5-12.7h46.9c10.2 0 19.9 4.9 25.9 13.3l71.2 98.8 157.2-218c6-8.3 15.6-13.3 25.9-13.3H699c6.5 0 10.3 7.4 6.5 12.7z" fill="#27ae60"/>'
      } else if (config.configured) {
        // 禁用图标（灰色圆圈和斜线）
        return '<path d="M512 64C264.6 64 64 264.6 64 512s200.6 448 448 448 448-200.6 448-448S759.4 64 512 64zm0 820c-205.4 0-372-166.6-372-372s166.6-372 372-372 372 166.6 372 372-166.6 372-372 372zm128-412c0 4.4-3.6 8-8 8H392c-4.4 0-8-3.6-8-8v-48c0-4.4 3.6-8 8-8h240c4.4 0 8 3.6 8 8v48z" fill="#95a5a6"/>'
      } else {
        // 红色叉号
        return '<path d="M512 64C264.6 64 64 264.6 64 512s200.6 448 448 448 448-200.6 448-448S759.4 64 512 64zm165.4 618.2l-66-70.7c-10.6-10.1-28.1-10.1-38.8 0l-66.7 71.5-66.7-71.5c-10.6-10.1-28.1-10.1-38.8 0l-66 70.7c-9.9 10.6-9.9 27.4 0 38l66 70.7c10.6 10.1 28.1 10.1 38.8 0l66.7-71.5 66.7 71.5c10.6 10.1 28.1 10.1 38.8 0l66-70.7c9.9-10.6 9.9-27.4 0-38z" fill="#e74c3c"/>'
      }
    },

    getStatusSymbol(configKey) {
      const config = this.configStatus[configKey]
      if (config.enabled) {
        // 绿色对勾
        return '<span style="color: #27ae60; font-size: 18px;">✓</span>'
      } else if (config.configured) {
        // 禁用图标
        return '<span style="color: #95a5a6; font-size: 18px;">○</span>'
      } else {
        // 红色叉号
        return '<span style="color: #e74c3c; font-size: 18px;">✗</span>'
      }
    },

    handleDrop(event) {
      event.preventDefault()
      this.isDragOver = false
      const files = event.dataTransfer.files
      if (files.length > 0) {
        this.handleFileSelect({ target: { files } })
      }
    },

    handleFileSelect(event) {
      const file = event.target.files[0]
      if (file) {
        const allowedTypes = [
          'application/pdf',
          'application/msword',
          'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
          'text/plain',
          'text/markdown',
          'text/x-markdown'
        ]
        
        if (allowedTypes.includes(file.type) || 
            file.name.match(/\.(pdf|doc|docx|txt|md)$/i)) {
          this.selectedFile = file
          this.documentTitle = file.name.replace(/\.[^/.]+$/, "")
        } else {
          ElMessage.error('请选择 PDF、Word、TXT 或 Markdown 格式的文件')
        }
      }
    },

    removeFile() {
      this.selectedFile = null
      this.documentTitle = ''
      this.$refs.fileInput.value = ''
    },

    formatFileSize(bytes) {
      if (bytes === 0) return '0 Bytes'
      const k = 1024
      const sizes = ['Bytes', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    },

    // ────── 历史文档面板 ──────
    async loadReqDocHistory() {
      this.reqDocHistoryError = false
      try {
        const response = await api.get('/requirement-analysis/api/req-docs/')
        this.reqDocHistory = response.data.results || response.data || []
        this.reqDocHistoryLoaded = true
      } catch (error) {
        console.error('加载历史文档失败:', error)
        this.reqDocHistoryError = true
        this.reqDocHistoryLoaded = true
        this.reqDocHistory = []
      }
    },

    async viewHistoryDoc(doc) {
      // 加载完整内容，预览模式打开
      try {
        const response = await api.get(`/requirement-analysis/api/req-docs/${doc.id}/`)
        this.viewingDoc = response.data
        this.isEditingDoc = false
        this.showHistoryPreview = true
      } catch (error) {
        ElMessage.error('加载文档详情失败')
      }
    },

    async editHistoryDoc(doc) {
      // 加载完整内容，直接进入编辑模式
      try {
        const response = await api.get(`/requirement-analysis/api/req-docs/${doc.id}/`)
        this.viewingDoc = response.data
        this.editingMarkdown = response.data.markdown_content || ''
        this.editingTitle = response.data.title || ''
        this.isEditingDoc = true
        this.showHistoryPreview = true
      } catch (error) {
        ElMessage.error('加载文档详情失败')
      }
    },

    enterEditMode() {
      // 从预览模式切换到编辑模式
      if (!this.viewingDoc) return
      this.editingMarkdown = this.viewingDoc.markdown_content || ''
      this.editingTitle = this.viewingDoc.title || ''
      this.isEditingDoc = true
    },

    cancelEdit() {
      this.isEditingDoc = false
      this.editingMarkdown = ''
      this.editingTitle = ''
    },

    async saveDocEdit() {
      if (!this.viewingDoc || !this.editingMarkdown.trim()) return
      this.editingSaving = true
      try {
        const response = await api.patch(
          `/requirement-analysis/api/req-docs/${this.viewingDoc.id}/`,
          { title: this.editingTitle.trim(), markdown_content: this.editingMarkdown }
        )
        const updated = response.data
        // 更新 viewingDoc（包含后端返回的 updated_at 等）
        if (updated.markdown_content) {
          this.viewingDoc.markdown_content = updated.markdown_content
        }
        if (updated.title) {
          this.viewingDoc.title = updated.title
        }
        // 同步本地列表中的标题
        const idx = this.reqDocHistory.findIndex(d => d.id === this.viewingDoc.id)
        if (idx !== -1 && updated.title) {
          this.reqDocHistory[idx].title = updated.title
        }
        this.isEditingDoc = false
        ElMessage.success('文档已保存')
      } catch (error) {
        ElMessage.error('保存失败：' + (error.response?.data?.error || error.message))
      } finally {
        this.editingSaving = false
      }
    },

    closePreview() {
      this.showHistoryPreview = false
      this.isEditingDoc = false
      this.editingMarkdown = ''
      this.editingTitle = ''
    },

    async deleteReqDocHistory(doc) {
      try {
        await ElMessageBox.confirm(
          `确定删除「${doc.title || '未命名文档'}」？此操作不可恢复。`,
          '确认删除',
          { confirmButtonText: '删除', cancelButtonText: '取消', type: 'warning' }
        )
      } catch {
        return
      }
      try {
        await api.delete(`/requirement-analysis/api/req-docs/${doc.id}/`)
        this.reqDocHistory = this.reqDocHistory.filter(d => d.id !== doc.id)
        ElMessage.success('已删除')
      } catch (error) {
        ElMessage.error('删除失败')
        console.error('删除历史文档失败:', error)
      }
    },

    async generateFromHistoryDoc(doc) {
      // 先加载文档，然后弹出确认弹窗
      try {
        const response = await api.get(`/requirement-analysis/api/req-docs/${doc.id}/`)
        const fullDoc = response.data
        const firstLine = (fullDoc.markdown_content || '').split('\n')[0].replace(/^#+\s*/, '').trim()
        const title = firstLine || fullDoc.title || '需求文档'
        
        // 打开确认弹窗，保存待生成的 payload
        this.pendingGeneratePayload = { title, content: fullDoc.markdown_content, source: 'history' }
        // 预填项目（如果历史文档有关联项目）
        const defaultProjectId = fullDoc.project?.id || null
        this.generateConfirmForm = {
          project_id: defaultProjectId,
          version_id: this.selectedVersion || null,
          feature_module_id: null,
          test_point_id: null,
          generation_mode: 'smart'
        }
        this.showGenerateConfirm = true
      } catch (error) {
        ElMessage.error('加载文档失败：' + (error.response?.data?.error || error.message))
      }
    },

    async generateFromPreviewDoc() {
      if (!this.viewingDoc) return
      const firstLine = (this.viewingDoc.markdown_content || '').split('\n')[0].replace(/^#+\s*/, '').trim()
      const title = firstLine || this.viewingDoc.title || '需求文档'
      
      // 打开确认弹窗
      this.pendingGeneratePayload = { title, content: this.viewingDoc.markdown_content, source: 'preview' }
      const defaultProjectId = this.viewingDoc.project?.id || null
      this.generateConfirmForm = {
        project_id: defaultProjectId,
        version_id: this.selectedVersion || null,
        feature_module_id: null,
        test_point_id: null,
        generation_mode: 'smart'
      }
      this.showGenerateConfirm = true
    },

    // 生成确认弹窗：项目切换时清空版本
    onConfirmProjectChange() {
      this.generateConfirmForm.version_id = null
      this.generateConfirmForm.feature_module_id = null
      this.generateConfirmForm.test_point_id = null
      this.moduleTestPoints = []
    },

    // 生成确认弹窗：功能模块切换时加载测试点
    async onConfirmFeatureModuleChange() {
      this.generateConfirmForm.test_point_id = null
      if (this.generateConfirmForm.feature_module_id) {
        await this.loadModuleTestPoints(this.generateConfirmForm.feature_module_id)
      } else {
        this.moduleTestPoints = []
      }
    },

    // 确认后开始生成
    async confirmStartGeneration() {
      if (!this.canConfirmGenerate) return
      
      const payload = this.pendingGeneratePayload
      if (!payload) return
      
      const confirmedProjectId = this.generateConfirmForm.project_id
      const confirmedVersionId = this.generateConfirmForm.version_id
      const confirmedFeatureModuleId = this.generateConfirmForm.feature_module_id
      const confirmedTestPointId = this.generateConfirmForm.test_point_id
      const confirmedGenerationMode = this.generateConfirmForm.generation_mode || 'smart'
      
      // 同步到全局变量（供其他入口使用）
      this.selectedVersion = confirmedVersionId
      this.selectedProject = confirmedProjectId ? String(confirmedProjectId) : ''
      this.selectedFeatureModule = confirmedFeatureModuleId || null
      
      this.showGenerateConfirm = false
      try {
        await this.startGeneration(
          payload.title,
          payload.content,
          confirmedProjectId,
          this.globalOutputMode,
          confirmedVersionId,
          confirmedFeatureModuleId,
          confirmedTestPointId,
          confirmedGenerationMode
        )
        this.showHistoryPreview = false
      } catch (error) {
        console.error('生成失败:', error)
      } finally {
        this.pendingGeneratePayload = null
      }
    },
    // ────── END 历史文档面板 ──────

    // ────── 需求文档生成（后门流程）──────
    async generateReqDoc() {
      if (!this.canGenerateReqDoc) return
      this.reqDoc.isGenerating = true
      try {
        let payload
        if (this.reqDoc.inputMode === 'text') {
          payload = { raw_text: this.reqDoc.rawText }
        } else {
          // 文件模式：分离 vision 和 text 两类文档
          const textIds = []
          const visionIds = []
          for (const f of this.reqDoc.files) {
            if (f.isImagePdf && f.documentId) {
              visionIds.push(f.documentId)
            } else if (f.extracted && f.documentId) {
              textIds.push(f.documentId)
            }
          }
          if (visionIds.length) {
            // 有图片型 PDF → 走 vision 模式，文字型作为补充
            payload = {
              document_ids: visionIds,
              text_document_ids: textIds,
              raw_text: this.reqDoc.rawText || undefined
            }
          } else if (textIds.length) {
            // 纯文字型文档 → 走文字模式
            payload = {
              text_document_ids: textIds,
              raw_text: this.reqDoc.rawText || undefined
            }
          } else {
            // 兜底
            payload = { raw_text: this.reqDoc.rawText }
          }
        }
        const response = await api.post('/requirement-analysis/api/generate-req-doc/', payload, { timeout: 300000 })
        this.reqDoc.markdown = response.data.markdown
        ElMessage.success('需求文档生成成功，请检查并编辑后使用')
        // 刷新历史文档列表
        this.loadReqDocHistory()
      } catch (error) {
        console.error('生成需求文档失败:', error)
        ElMessage.error('生成失败：' + (error.response?.data?.error || error.message))
      } finally {
        this.reqDoc.isGenerating = false
      }
    },

    async getReqDocTemplate() {
      try {
        const response = await api.get('/requirement-analysis/api/req-doc-template/')
        this.reqDoc.markdown = response.data.template
        ElMessage.success('已加载空白模板，请填写内容')
      } catch (error) {
        ElMessage.error('获取模板失败')
      }
    },

    toggleReqDocPreview() {
      this.reqDoc.showPreview = !this.reqDoc.showPreview
    },

    resetReqDoc() {
      this.reqDoc.markdown = ''
      this.reqDoc.showPreview = false
      this.reqDoc.rawText = ''
      this.reqDoc.files = []
      this.reqDoc.isExtracting = false
      if (this.$refs.reqDocFileInput) this.$refs.reqDocFileInput.value = ''
      if (this.$refs.reqDocFolderInput) this.$refs.reqDocFolderInput.value = ''
    },

    // ── 共享：上传单个文件并提取文字 ──
    async _uploadOneFile(file, extraMeta = {}) {
      const entry = { file, documentId: null, isImagePdf: false, extracting: true, extracted: false, error: null, ...extraMeta }
      this.reqDoc.files.push(entry)
      const idx = this.reqDoc.files.length - 1
      try {
        const formData = new FormData()
        formData.append('title', file.name)
        formData.append('file', file)
        const uploadResp = await api.post('/requirement-analysis/api/documents/', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })
        const docId = uploadResp.data.id
        this.reqDoc.files[idx].documentId = docId

        const extractResp = await api.get(`/requirement-analysis/api/documents/${docId}/extract_text/`)
        const text = extractResp.data.extracted_text

        if (text && text.trim().length >= 50) {
          this.reqDoc.files[idx].extracted = true
          this.reqDoc.files[idx].isImagePdf = false
          // 不累积到 rawText，generateReqDoc 走 document_ids 模式
        } else {
          this.reqDoc.files[idx].isImagePdf = true
          this.reqDoc.files[idx].extracted = false
        }
      } catch (error) {
        this.reqDoc.files[idx].error = error.response?.data?.error || error.message
      } finally {
        this.reqDoc.files[idx].extracting = false
      }
    },

    // ── 汇总+提示 ──
    _finishFileUpload(refName) {
      this.reqDoc.isExtracting = this.reqDoc.files.some(f => f.extracting)
      if (this.$refs[refName]) this.$refs[refName].value = ''

      const allDone = this.reqDoc.files.filter(f => !f.error)
      const textCount = allDone.filter(f => f.extracted).length
      const imgCount = allDone.filter(f => f.isImagePdf).length
      const errCount = this.reqDoc.files.filter(f => f.error).length

      if (allDone.length === textCount + imgCount && !errCount && this.reqDoc.files.length > 0) {
        const parts = []
        if (textCount) parts.push(`${textCount} 个文字提取成功`)
        if (imgCount) parts.push(`${imgCount} 个图片型PDF将由AI视觉识别`)
        ElMessage.success(parts.join('，') + '，可点击生成文档')
      } else if (errCount) {
        ElMessage.warning(`${errCount} 个文件处理失败，请检查`)
      }
    },

    // ── 多文件选择 → 逐文件上传提取 ──
    async handleReqDocFileSelect(event) {
      const newFiles = Array.from(event.target.files)
      if (!newFiles.length) return
      for (const file of newFiles) {
        await this._uploadOneFile(file)
      }
      this._finishFileUpload('reqDocFileInput')
    },

    // ── 文件夹选择 → 遍历文件夹内所有文件 ──
    async handleReqDocFolderSelect(event) {
      const rawFiles = Array.from(event.target.files)
      if (!rawFiles.length) return

      // 提取文件夹名（从第一个文件的 webkitRelativePath 取第一段）
      const firstPath = rawFiles[0].webkitRelativePath || rawFiles[0].name
      const folderName = firstPath.split('/')[0]

      // 过滤支持的文件类型
      const supportedExts = ['pdf', 'doc', 'docx', 'txt', 'md']
      const validFiles = rawFiles.filter(f => {
        const ext = f.name.split('.').pop().toLowerCase()
        return supportedExts.includes(ext)
      })

      if (!validFiles.length) {
        ElMessage.warning('该文件夹内没有支持的文档文件')
        if (this.$refs.reqDocFolderInput) this.$refs.reqDocFolderInput.value = ''
        return
      }

      ElMessage.info(`正在读取文件夹「${folderName}」内 ${validFiles.length} 个文件…`)

      for (const file of validFiles) {
        await this._uploadOneFile(file, {
          folder: folderName,
          relativePath: file.webkitRelativePath || file.name
        })
      }
      this._finishFileUpload('reqDocFolderInput')
    },

    // ── 删除操作（适配分组索引） ──
    removeReqDocFile(groupIdx, fileIdx) {
      // 找到该分组在 files 数组中的实际索引
      let cursor = 0
      for (let g = 0; g < this.fileGroups.length; g++) {
        if (g === groupIdx) {
          const targetIdx = cursor + fileIdx
          this.reqDoc.files.splice(targetIdx, 1)
          break
        }
        cursor += this.fileGroups[g].items.length
      }
      this.reqDoc.rawText = ''  // 清空 rawText，generateReqDoc 从 document_ids 取
      this.reqDoc.isExtracting = this.reqDoc.files.some(f => f.extracting)
    },

    removeFolder(groupIdx) {
      let cursor = 0
      for (let g = 0; g < this.fileGroups.length; g++) {
        if (g === groupIdx) {
          this.reqDoc.files.splice(cursor, this.fileGroups[g].items.length)
          break
        }
        cursor += this.fileGroups[g].items.length
      }
      this.reqDoc.rawText = ''
      this.reqDoc.isExtracting = this.reqDoc.files.some(f => f.extracting)
    },

    removeFlatFile(flatIdx) {
      // flatFiles 对应的是 files 中 folder 为空的条目
      const target = this.flatFiles[flatIdx]
      if (!target) return
      const realIdx = this.reqDoc.files.indexOf(target)
      if (realIdx !== -1) {
        this.reqDoc.files.splice(realIdx, 1)
      }
      this.reqDoc.rawText = ''
      this.reqDoc.isExtracting = this.reqDoc.files.some(f => f.extracting)
    },

    clearReqDocFiles() {
      this.reqDoc.files = []
      this.reqDoc.rawText = ''
      this.reqDoc.isExtracting = false
      if (this.$refs.reqDocFileInput) this.$refs.reqDocFileInput.value = ''
      if (this.$refs.reqDocFolderInput) this.$refs.reqDocFolderInput.value = ''
    },

    async useReqDocForGeneration() {
      if (!this.reqDoc.markdown.trim()) return
      const firstLine = this.reqDoc.markdown.split('\n')[0].replace(/^#+\s*/, '').trim()
      const title = firstLine || '需求文档'
      // 弹出确认弹窗
      this.pendingGeneratePayload = { title, content: this.reqDoc.markdown, source: 'reqDoc' }
      this.generateConfirmForm = {
        project_id: this.reqDoc.selectedProject ? Number(this.reqDoc.selectedProject) : null,
        version_id: this.selectedVersion || null,
        feature_module_id: null,
        test_point_id: null,
        generation_mode: 'smart'
      }
      this.showGenerateConfirm = true
    },
    // ────── END 需求文档生成 ──────

    async generateFromManualInput() {
      if (!this.canGenerateManual) {
        ElMessage.error('请填写完整的需求信息')
        return
      }

      const requirementText = `需求标题: ${this.manualInput.title}\n\n需求描述:\n${this.manualInput.description}`
      // 弹出确认弹窗
      this.pendingGeneratePayload = { title: this.manualInput.title, content: requirementText, source: 'manual' }
      this.generateConfirmForm = {
        project_id: this.manualInput.selectedProject ? Number(this.manualInput.selectedProject) : null,
        version_id: this.selectedVersion || null,
        feature_module_id: null,
        test_point_id: null,
        generation_mode: 'smart'
      }
      this.showGenerateConfirm = true
    },

    async generateFromDocument() {
      if (!this.selectedFile || !this.documentTitle) {
        ElMessage.error('请选择文件并输入文档标题')
        return
      }

      try {
        // 首先上传并提取文档内容
        const formData = new FormData()
        formData.append('title', this.documentTitle)
        formData.append('file', this.selectedFile)
        if (this.selectedProject) {
          formData.append('project', this.selectedProject)
        }

        ElMessage.info('正在提取文档内容...')
        const uploadResponse = await api.post('/requirement-analysis/api/documents/', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        })

        // 提取文档内容
        const extractResponse = await api.get(`/requirement-analysis/api/documents/${uploadResponse.data.id}/extract_text/`)
        const extractedText = extractResponse.data.extracted_text

        if (!extractedText || extractedText.trim().length === 0) {
          ElMessage.error('无法从文档中提取到有效内容，请检查文档格式')
          return
        }

        const requirementText = `文档标题: ${this.documentTitle}\n\n文档内容:\n${extractedText}`

        // 弹出确认弹窗
        this.pendingGeneratePayload = { title: this.documentTitle, content: requirementText, source: 'document' }
        this.generateConfirmForm = {
          project_id: this.selectedProject ? Number(this.selectedProject) : null,
          version_id: this.selectedVersion || null,
          feature_module_id: null,
          test_point_id: null,
          generation_mode: 'smart'
        }
        this.showGenerateConfirm = true

      } catch (error) {
        console.error('文档处理失败:', error)
        ElMessage.error('文档处理失败: ' + (error.response?.data?.error || error.message))
      }
    },

    async startGeneration(title, requirementText, projectId, outputMode = 'stream', versionId = '', featureModuleId = null, testPointId = null, generationMode = 'smart') {
      // 在开始生成前，主动刷新token确保生成过程中不会过期
      try {
        const userStore = useUserStore()
        if (userStore.isTokenExpiringSoon && userStore.refreshToken) {
          console.log('生成前主动刷新token...')
          await userStore.refreshAccessToken()
          console.log('Token刷新成功，可以安全开始生成')
        } else if (userStore.accessToken) {
          console.log('Token状态良好，无需刷新')
        }
      } catch (error) {
        console.error('Token刷新失败:', error)
        ElMessage.error('Token刷新失败，请重新登录')
        return
      }

      this.isGenerating = true
      this.currentStep = 1
      this.progressText = '正在创建生成任务...'
      this.streamedContent = ''  // 清空流式内容
      this.finalTestCases = ''  // 清空最终版用例
      this.streamedReviewContent = ''  // 清空评审内容
      this.hasShownCompletionMessage = false  // 重置完成消息标志位
      this.showResults = false  // 隐藏上一次的结果

      try {
        // 调用新的生成API
        const requestData = {
          title: title,
          requirement_text: requirementText,
          use_writer_model: true,
          use_reviewer_model: this.showReviewStep,
          output_mode: outputMode,  // 添加输出模式参数
          generation_mode: generationMode  // 生成模式
        }

        // 如果选择了项目，添加到请求中
        if (projectId) {
          requestData.project = projectId
        }
        // 如果选择了版本，添加到请求中
        if (versionId) {
          requestData.version = versionId
        }
        // 如果选择了功能模块，添加到请求中
        if (featureModuleId) {
          requestData.feature_module = featureModuleId
        }
        // 如果选择了测试点，添加到请求中
        if (testPointId) {
          requestData.test_point = testPointId
        }

        const response = await api.post('/requirement-analysis/api/testcase-generation/generate/', requestData)

        this.currentTaskId = response.data.task_id
        this.progressText = '任务已创建，正在处理中...'

        ElMessage.success('测试用例生成任务已启动')

        // 根据输出模式选择不同的进度获取方式
        if (outputMode === 'stream') {
          this.startStreamingProgress()
        } else {
          this.startPolling()
        }

      } catch (error) {
        console.error('创建生成任务失败:', error)
        ElMessage.error('创建任务失败: ' + (error.response?.data?.error || error.message))
        this.isGenerating = false
      }
    },

    startStreamingProgress() {
      // 使用SSE进行流式进度获取
      // 注意：EventSource不使用axios代理，需要直接指向后端服务器
      // 完整的URL路径: /api/requirement-analysis/api/testcase-generation/{task_id}/stream_progress/
      const isDev = import.meta.env.DEV
      const baseUrl = isDev ? 'http://127.0.0.1:8000' : ''
      const apiUrl = `${baseUrl}/api/requirement-analysis/api/testcase-generation/${this.currentTaskId}/stream_progress/`

      console.log('SSE连接URL:', apiUrl)

      // 创建EventSource（不支持自定义headers，使用withCredentials发送cookie）
      this.eventSource = new EventSource(apiUrl, { withCredentials: true })

      // 监听连接打开事件
      this.eventSource.onopen = (event) => {
        console.log('✅ SSE连接已打开', event)
      }

      this.eventSource.onmessage = (event) => {
        console.log('📨 收到SSE消息:', event.data)

        try {
          const data = JSON.parse(event.data)
          console.log('📦 解析后的数据:', data)

          if (data.type === 'progress') {
            // 更新进度状态
            if (data.status === 'generating') {
              this.currentStep = 2
              this.progressText = `正在编写测试用例... ${data.progress}%`
            } else if (data.status === 'reviewing') {
              this.currentStep = 3
              this.progressText = `正在评审测试用例... ${data.progress}%`
            } else if (data.status === 'revising') {
              this.currentStep = 3
              this.progressText = `正在生成最终版用例... ${data.progress}%`
            }
          } else if (data.type === 'content') {
            // 实时接收流式内容（用例生成）
            console.log('✍️ 收到流式内容:', data.content.length, '个字符')
            this.streamedContent += data.content
            this.currentStep = 2
            this.progressText = '正在生成测试用例...'
          } else if (data.type === 'review_content') {
            // 实时接收评审内容
            console.log('📝 收到评审内容:', data.content.length, '个字符', '当前总长度:', this.streamedReviewContent.length + data.content.length)
            this.streamedReviewContent += data.content
            this.currentStep = 3
            this.progressText = '正在评审测试用例...'
          } else if (data.type === 'final_content') {
            // 实时接收最终版用例内容
            console.log('🎯 收到最终用例内容:', data.content.length, '个字符', '当前总长度:', this.finalTestCases.length + data.content.length)
            this.finalTestCases += data.content
            this.currentStep = 3
            this.progressText = '🎯 正在流式生成最终版用例...'
          } else if (data.type === 'status') {
            // 最终状态
            console.log('📊 收到状态更新:', data.status)
            if (data.status === 'completed') {
              this.progressText = '生成完成！'
              // 获取最终结果
              this.fetchFinalResult()
            } else if (data.status === 'failed') {
              this.progressText = '生成失败'
              this.handleGenerationError()
            }
          } else if (data.type === 'done') {
            // 流式结束，立即关闭EventSource，获取最终结果
            console.log('✅ 流式传输完成')
            if (this.eventSource) {
              console.log('🔒 关闭SSE连接')
              this.eventSource.close()
              this.eventSource = null
            }
            this.fetchFinalResult()
          }
        } catch (e) {
          console.error('❌ 解析SSE数据失败:', e, '原始数据:', event.data)
        }
      }

      this.eventSource.onerror = (error) => {
        console.log('⚠️ SSE连接事件:', error)

        // 如果EventSource已经被关闭（在onmessage中关闭的），不做任何处理
        if (!this.eventSource) {
          console.log('ℹ️ EventSource已关闭，忽略错误事件')
          return
        }

        console.log('EventSource状态:', {
          readyState: this.eventSource.readyState,
          url: this.eventSource.url
        })

        // 如果任务已经完成或不在生成中，不要降级
        if (this.showResults || !this.isGenerating) {
          console.log('ℹ️ 任务已完成或不在生成中，不降级到轮询')
          // 清理EventSource
          if (this.eventSource) {
            this.eventSource.close()
            this.eventSource = null
          }
          return
        }

        // readyState=0表示连接中断，可能需要降级到轮询模式
        // 但由于我们在done消息中主动关闭了连接，这里再次检查状态
        if (this.eventSource.readyState === 0) {
          console.error('❌ SSE连接中断，降级到轮询模式')
          this.eventSource.close()
          this.eventSource = null
          ElMessage.warning('流式连接中断，切换到轮询模式')
          this.startPolling()
        }
      }
    },

    async fetchFinalResult() {
      try {
        // 修复URL：去掉多余的/api/前缀（axios baseURL已经包含/api）
        const response = await api.get(`/requirement-analysis/api/testcase-generation/${this.currentTaskId}/progress/`)
        const task = response.data

        this.generationResult = task
        this.showResults = true
        this.isGenerating = false

        // 设置第4步为完成状态
        this.currentStep = 4

        // 设置最终版用例（如果还没有通过流式接收完整）
        if (task.final_test_cases) {
          console.log('📝 从task对象获取最终用例')
          // 无论this.finalTestCases是否已有值，都用最新的final_test_cases覆盖
          // 这样确保完整输出模式下也能正确显示最终版用例
          this.finalTestCases = task.final_test_cases
        }

        // 如果评审内容为空，从task对象中获取
        if (!this.streamedReviewContent && task.review_feedback) {
          console.log('📝 从task对象获取评审内容')
          this.streamedReviewContent = task.review_feedback
        }

        // 如果生成内容为空，从task对象中获取
        if (!this.streamedContent && task.generated_test_cases) {
          console.log('✍️ 从task对象获取生成内容')
          this.streamedContent = task.generated_test_cases
        }

        if (this.eventSource) {
          this.eventSource.close()
          this.eventSource = null
        }

        // 只显示一次完成消息
        if (!this.hasShownCompletionMessage) {
          ElMessage.success('测试用例生成完成！')
          this.hasShownCompletionMessage = true
        }
      } catch (error) {
        console.error('获取最终结果失败:', error)
        ElMessage.error('获取结果失败')
        this.isGenerating = false
      }
    },

    handleGenerationError() {
      this.isGenerating = false
      if (this.eventSource) {
        this.eventSource.close()
        this.eventSource = null
      }
      if (this.pollInterval) {
        clearInterval(this.pollInterval)
        this.pollInterval = null
      }
    },

    startPolling() {
      this.pollInterval = setInterval(async () => {
        try {
          // 修复URL：去掉多余的/api/前缀（axios baseURL已经包含/api）
          const response = await api.get(`/requirement-analysis/api/testcase-generation/${this.currentTaskId}/progress/`)
          const task = response.data

          console.log(`轮询 - 任务状态: ${task.status}, 进度: ${task.progress}%`)

          // 更新进度显示
          if (task.status === 'generating') {
            this.currentStep = 2
            this.progressText = '正在编写测试用例...'
          } else if (task.status === 'reviewing') {
            this.currentStep = 3
            this.progressText = '正在评审测试用例...'
          } else if (task.status === 'completed') {
            this.currentStep = 4
            this.progressText = '生成完成！'

            // 任务完成，显示结果
            this.generationResult = task
            this.showResults = true
            this.isGenerating = false

            // 设置显示内容（完整输出模式下需要）
            if (task.generated_test_cases) {
              console.log('✍️ 轮询模式 - 设置生成内容')
              this.streamedContent = task.generated_test_cases
            }
            if (task.review_feedback) {
              console.log('📝 轮询模式 - 设置评审内容')
              this.streamedReviewContent = task.review_feedback
            }
            if (task.final_test_cases) {
              console.log('🎯 轮询模式 - 设置最终版用例')
              this.finalTestCases = task.final_test_cases
            }

            clearInterval(this.pollInterval)
            this.pollInterval = null

            // 只显示一次完成消息
            if (!this.hasShownCompletionMessage) {
              ElMessage.success('测试用例生成完成！')
              this.hasShownCompletionMessage = true
            }
            return
          } else if (task.status === 'failed') {
            this.progressText = '生成失败'
            this.isGenerating = false

            clearInterval(this.pollInterval)
            this.pollInterval = null

            ElMessage.error('测试用例生成失败: ' + (task.error_message || '未知错误'))
            return
          }

        } catch (error) {
          console.error('轮询 - 检查任务进度失败:', error)
          // 继续轮询，不中断
        }
      }, 3000) // 每3秒检查一次
    },

    cancelGeneration() {
      if (this.pollInterval) {
        clearInterval(this.pollInterval)
        this.pollInterval = null
      }
      this.isGenerating = false
      this.currentTaskId = null
      ElMessage.info('已取消生成任务')
    },

    // 下载测试用例为xlsx文件
    async downloadTestCases() {
      try {
        // 解析最终测试用例内容
        const finalTestCases = this.generationResult.final_test_cases;
        const taskId = this.generationResult.task_id;

        // 创建工作簿
        const workbook = XLSX.utils.book_new();

        // 过滤掉总结和建议部分，只保留测试用例内容
        const filteredContent = this.filterTestCasesOnly(finalTestCases);

        // 尝试解析表格格式的测试用例（参考AutoGenTestCase的做法）
        const tableFormat = this.parseTableFormat(filteredContent);

        let worksheetData = [];

        if (tableFormat.length > 0) {
          // 如果解析到表格格式，直接使用，但要确保表头正确
          worksheetData = tableFormat;
          
          // 检查并修正表头
          if (worksheetData.length > 0) {
            const header = worksheetData[0];
            for (let i = 0; i < header.length; i++) {
              if (header[i] && header[i].includes('测试步骤')) {
                header[i] = header[i].replace('测试步骤', '操作步骤');
              }
              if (header[i] && header[i].includes('Test Steps')) {
                header[i] = header[i].replace('Test Steps', '操作步骤');
              }
            }
          }
        } else {
          // 否则尝试解析结构化格式
          worksheetData = this.parseStructuredFormat(filteredContent);
        }

        // 将所有单元格中的<br>标签转换为换行符
        worksheetData = worksheetData.map(row =>
          row.map(cell => this.convertBrToNewline(cell))
        );

        // 创建工作表
        const worksheet = XLSX.utils.aoa_to_sheet(worksheetData);

        // 设置列宽
        const colWidths = [
          { wch: 15 }, // 测试用例编号
          { wch: 30 }, // 测试场景
          { wch: 25 }, // 前置条件
          { wch: 40 }, // 操作步骤
          { wch: 30 }, // 预期结果
          { wch: 10 }  // 优先级
        ];
        worksheet['!cols'] = colWidths;

        // 设置表头样式（加粗）
        if (worksheetData.length > 1) {
          for (let col = 0; col < Math.min(6, worksheetData[0].length); col++) {
            const cellAddress = XLSX.utils.encode_cell({ r: 0, c: col });
            if (!worksheet[cellAddress]) continue;
            worksheet[cellAddress].s = {
              font: { bold: true },
              alignment: { horizontal: 'center', vertical: 'center', wrapText: true }
            };
          }
          
          // 设置自动换行
          for (let row = 1; row < worksheetData.length; row++) {
            for (let col = 0; col < Math.min(6, worksheetData[row].length); col++) {
              const cellAddress = XLSX.utils.encode_cell({ r: row, c: col });
              if (worksheet[cellAddress]) {
                worksheet[cellAddress].s = {
                  alignment: { vertical: 'top', wrapText: true }
                };
              }
            }
          }
        }

        // 将工作表添加到工作簿
        XLSX.utils.book_append_sheet(workbook, worksheet, '测试用例');

        // 生成文件名（包含任务ID和日期）
        const fileName = `测试用例_${taskId}_${new Date().toISOString().slice(0, 10)}.xlsx`;

        // 导出文件
        XLSX.writeFile(workbook, fileName);

        ElMessage.success('测试用例下载成功');
      } catch (error) {
        console.error('下载测试用例失败:', error);
        ElMessage.error('下载测试用例失败: ' + (error.message || '未知错误'));
      }
    },

    // 保存到用例记录
    async saveToTestCaseRecords() {
      try {
        // 调用后端API保存到记录
        const response = await api.post(`/requirement-analysis/api/testcase-generation/${this.generationResult.task_id}/save_to_records/`)

        if (response.data.already_saved) {
          ElMessage.info('测试用例已经保存过了')
        } else {
          const importedCount = response.data.imported_count || 0
          ElMessage.success(`测试用例已保存！已导入 ${importedCount} 条测试用例到测试用例管理系统`)
        }

        // 不跳转，留在当前页面
        // this.$router.push('/generated-testcases')
      } catch (error) {
        console.error('保存测试用例失败:', error)
        ElMessage.error('保存测试用例失败: ' + (error.response?.data?.error || error.message))
      }
    },

    resetGeneration() {
      // 重置生成状态
      this.isGenerating = false;
      this.currentTaskId = null;
      this.progressText = '准备开始生成...';
      this.currentStep = 0;
      this.showResults = false;
      this.generationResult = null;

      // 清空流式内容和最终版用例
      this.streamedContent = '';
      this.streamedReviewContent = '';
      this.finalTestCases = '';

      if (this.pollInterval) {
        clearInterval(this.pollInterval);
        this.pollInterval = null;
      }

      // 刷新页面以获取最新的配置
      window.location.reload();
    },

    // 格式化日期时间
    formatDateTime(dateTimeString) {
      if (!dateTimeString) return '';
      const date = new Date(dateTimeString);
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      const hours = String(date.getHours()).padStart(2, '0');
      const minutes = String(date.getMinutes()).padStart(2, '0');
      return `${year}-${month}-${day} ${hours}:${minutes}`;
    },

    // 格式化Markdown为HTML（简化版）
    formatMarkdown(content) {
      if (!content) return '';

      // 先去除"新增"标记，在markdown转换之前处理
      // 这样可以避免markdown转换后无法匹配的问题
      let html = content
        .replace(/\*\*新增\*\*-/g, '')  // **新增**-xxx -> xxx (保留xxx的原有格式)
        .replace(/新增-/g, '');  // 新增-xxx -> xxx (保留xxx的原有格式)

      // 转义HTML特殊字符
      html = html
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');

      // 转换Markdown语法
      // 标题 #
      html = html.replace(/^#{6}\s+(.+)$/gm, '<h6>$1</h6>');
      html = html.replace(/^#{5}\s+(.+)$/gm, '<h5>$1</h5>');
      html = html.replace(/^#{4}\s+(.+)$/gm, '<h4>$1</h4>');
      html = html.replace(/^#{3}\s+(.+)$/gm, '<h3>$1</h3>');
      html = html.replace(/^#{2}\s+(.+)$/gm, '<h2>$1</h2>');
      html = html.replace(/^#{1}\s+(.+)$/gm, '<h1>$1</h1>');

      // 粗体 **text** 或 __text__
      html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
      html = html.replace(/__(.+?)__/g, '<strong>$1</strong>');

      // 斜体 *text* 或 _text_
      html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');
      html = html.replace(/_(.+?)_/g, '<em>$1</em>');

      // 代码块 ```code```
      html = html.replace(/```([\s\S]+?)```/g, '<pre><code>$1</code></pre>');

      // 行内代码 `code`
      html = html.replace(/`([^`]+)`/g, '<code>$1</code>');

      // 换行符转换为<br>
      html = html.replace(/\n/g, '<br>');

      return html;
    },

    // 将HTML的<br>标签转换为换行符（用于Excel导出）
    convertBrToNewline(text) {
      if (!text) return '';
      return text.replace(/<br\s*\/?>/gi, '\n');
    },

    // 过滤掉总结和建议部分，只保留测试用例内容
    filterTestCasesOnly(content) {
      if (!content) return '';

      const lines = content.split('\n');
      const filteredLines = [];
      let inTestCaseSection = true;
      
      for (let line of lines) {
        const trimmedLine = line.trim();
        
        // 检查是否到了总结或建议部分
        if (trimmedLine.includes('总结') || 
            trimmedLine.includes('建议') || 
            trimmedLine.includes('Summary') || 
            trimmedLine.includes('Recommendation') ||
            trimmedLine.includes('最后') ||
            trimmedLine.includes('补充说明')) {
          inTestCaseSection = false;
          break;
        }
        
        if (inTestCaseSection) {
          filteredLines.push(line);
        }
      }
      
      return filteredLines.join('\n');
    },

    // 解析表格格式的测试用例（参考AutoGenTestCase的做法）
    parseTableFormat(content) {
      if (!content) return [];
      
      const lines = content.split('\n').filter(line => line.trim());
      const worksheetData = [];
      
      for (let line of lines) {
        const trimmedLine = line.trim();
        
        // 检查是否是表格行（包含|分隔符，且不是分隔线）
        if (trimmedLine.includes('|') && !trimmedLine.includes('--------')) {
          let cells = trimmedLine.split('|').map(cell => cell.trim())
          // 移除首尾空字符串（split('|') 在首尾会产生空字符串）
          while (cells.length > 0 && cells[0] === '') cells.shift()
          while (cells.length > 0 && cells[cells.length - 1] === '') cells.pop()
          if (cells.length > 1) {
            worksheetData.push(cells);
          }
        }
      }
      
      return worksheetData;
    },

    // 解析结构化格式的测试用例
    parseStructuredFormat(content) {
      if (!content) return [];
      
      const lines = content.split('\n').filter(line => line.trim());
      const worksheetData = [];
      
      // 添加表头
      worksheetData.push(['测试用例编号', '测试场景', '前置条件', '操作步骤', '预期结果', '优先级']);
      
      let currentTestCase = {};
      let testCaseNumber = 1;
      let i = 0;
      
      while (i < lines.length) {
        const line = lines[i].trim();
        
        // 识别测试用例开始标志
        if (line.includes('测试用例') || line.includes('Test Case') || 
            line.match(/^(\d+\.|\*|\-|\d+、)/)) {
          
          // 如果之前有测试用例数据，先保存
          if (Object.keys(currentTestCase).length > 0) {
            worksheetData.push([
              currentTestCase.number || `TC${testCaseNumber}`,
              currentTestCase.scenario || '',
              currentTestCase.precondition || '',
              currentTestCase.steps || '',
              currentTestCase.expected || '',
              currentTestCase.priority || '中'
            ]);
            testCaseNumber++;
          }
          
          // 开始新的测试用例
          currentTestCase = {
            number: `TC${testCaseNumber}`,
            scenario: line.replace(/^(\d+\.|\*|\-|\d+、)\s*/, '').replace(/测试用例\d*[:：]?\s*/, ''),
            precondition: '',
            steps: '',
            expected: '',
            priority: '中'
          };
          i++;
        }
        // 识别前置条件
        else if (line.includes('前置条件') || line.includes('前提') || 
                 line.includes('Precondition')) {
          let precondition = line.replace(/.*?[:：]\s*/, '');
          // 收集后续的前置条件行
          i++;
          while (i < lines.length) {
            const nextLine = lines[i].trim();
            if (nextLine.includes('测试步骤') || nextLine.includes('操作步骤') || 
                nextLine.includes('Test Steps') || nextLine.includes('步骤') ||
                nextLine.includes('预期结果') || nextLine.includes('Expected') ||
                nextLine.includes('优先级') || nextLine.includes('Priority') ||
                nextLine.includes('测试用例') || nextLine.includes('Test Case') ||
                nextLine.match(/^(\d+\.|\*|\-|\d+、)/)) {
              break;
            }
            if (nextLine) {
              precondition += '\n' + nextLine;
            }
            i++;
          }
          currentTestCase.precondition = precondition;
        }
        // 识别测试步骤
        else if (line.includes('测试步骤') || line.includes('操作步骤') || 
                 line.includes('Test Steps') || line.includes('步骤')) {
          let steps = line.replace(/.*?[:：]\s*/, '');
          // 收集后续的步骤行
          i++;
          while (i < lines.length) {
            const nextLine = lines[i].trim();
            if (nextLine.includes('预期结果') || nextLine.includes('Expected') ||
                nextLine.includes('优先级') || nextLine.includes('Priority') ||
                nextLine.includes('测试用例') || nextLine.includes('Test Case') ||
                nextLine.match(/^(\d+\.|\*|\-|\d+、)/)) {
              break;
            }
            if (nextLine) {
              steps += '\n' + nextLine;
            }
            i++;
          }
          currentTestCase.steps = steps;
        }
        // 识别预期结果
        else if (line.includes('预期结果') || line.includes('Expected') || 
                 line.includes('期望')) {
          let expected = line.replace(/.*?[:：]\s*/, '');
          // 收集后续的结果行
          i++;
          while (i < lines.length) {
            const nextLine = lines[i].trim();
            if (nextLine.includes('优先级') || nextLine.includes('Priority') ||
                nextLine.includes('测试用例') || nextLine.includes('Test Case') ||
                nextLine.match(/^(\d+\.|\*|\-|\d+、)/)) {
              break;
            }
            if (nextLine) {
              expected += '\n' + nextLine;
            }
            i++;
          }
          currentTestCase.expected = expected;
        }
        // 识别优先级
        else if (line.includes('优先级') || line.includes('Priority')) {
          currentTestCase.priority = line.replace(/.*?[:：]\s*/, '');
          i++;
        }
        // 如果是没有明确标识的行，可能是场景描述的延续
        else if (Object.keys(currentTestCase).length > 0 && 
                 !currentTestCase.steps && !currentTestCase.expected && 
                 !currentTestCase.precondition) {
          if (currentTestCase.scenario && line.length > 5) {
            currentTestCase.scenario += '\n' + line;
          }
          i++;
        } else {
          i++;
        }
      }
      
      // 保存最后一个测试用例
      if (Object.keys(currentTestCase).length > 0) {
        worksheetData.push([
          currentTestCase.number || `TC${testCaseNumber}`,
          currentTestCase.scenario || '',
          currentTestCase.precondition || '',
          currentTestCase.steps || '',
          currentTestCase.expected || '',
          currentTestCase.priority || '中'
        ]);
      }
      
      // 如果没有解析到结构化数据，则按原格式输出
      if (worksheetData.length <= 1) {
        worksheetData.length = 0; // 清空
        worksheetData.push(['测试用例内容']);
        content.split('\n').forEach((line, index) => {
          if (line.trim()) {
            worksheetData.push([line.trim()]);
          }
        });
      }
      
      return worksheetData;
    }
  }
}
</script>

<style scoped>
.requirement-analysis {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  position: relative;
}

.page-header {
  text-align: center;
  margin-bottom: 40px;
}

.page-header h1 {
  font-size: 2.5rem;
  color: #2c3e50;
  margin-bottom: 10px;
}

.page-header p {
  color: #666;
  font-size: 1.1rem;
}

/* 输出模式设置区域 - 全局 */
.output-mode-section {
  margin-bottom: 30px;
}

.output-mode-card {
  background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(226, 232, 240, 0.8);
  transition: all 0.3s ease;
}

.output-mode-card:hover {
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.12);
}

.output-mode-card h3 {
  font-size: 1.3rem;
  color: #1a202c;
  margin: 0 0 8px 0;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.mode-section-desc {
  color: #64748b;
  font-size: 0.9rem;
  margin: 0 0 16px 0;
  line-height: 1.5;
}

/* 配置引导弹出窗口 */
.modal-overlay {
  position: fixed !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  width: 100vw !important;
  height: 100vh !important;
  background: rgba(15, 23, 42, 0.6) !important;
  backdrop-filter: blur(4px);
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  z-index: 9999 !important;
  padding: 20px;
  margin: 0 !important;
  opacity: 1 !important;
}

.guide-config-modal {
  background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%) !important;
  border-radius: 24px;
  padding: 36px;
  max-width: 850px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
  border: 1px solid rgba(226, 232, 240, 0.8);
  position: relative;
  flex-shrink: 0;
  margin: auto;
  opacity: 1 !important;
}

.guide-config-modal::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 5px;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  border-radius: 24px 24px 0 0;
}

.guide-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 28px;
}

.guide-icon {
  width: 56px;
  height: 56px;
  flex-shrink: 0;
  filter: drop-shadow(0 4px 8px rgba(245, 158, 11, 0.2));
}

.guide-title h2 {
  font-size: 1.6rem;
  color: #1a202c;
  margin: 0 0 6px 0;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.guide-title p {
  color: #64748b;
  font-size: 0.95rem;
  margin: 0;
  font-weight: 400;
}

.config-groups {
  margin-bottom: 24px;
}

.config-group {
  margin-bottom: 20px;
}

.group-label {
  font-size: 0.85rem;
  color: #94a3b8;
  margin-bottom: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.config-items-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 16px;
}

.config-item-inline {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  border-radius: 12px;
  border: 2px solid transparent;
  position: relative;
  overflow: hidden;
  font-weight: 500;
}

.config-item-inline::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  border-radius: 12px 0 0 12px;
}

.config-item-inline.optional {
  opacity: 0.75;
}

/* 根据状态设置背景色和样式 */
.config-item-inline.status-enabled {
  background: linear-gradient(135deg, rgba(236, 253, 245, 0.9) 0%, rgba(220, 252, 231, 0.6) 100%);
  border-color: rgba(34, 197, 94, 0.2);
  box-shadow: 0 4px 12px rgba(34, 197, 94, 0.1);
}

.config-item-inline.status-enabled::before {
  background: linear-gradient(180deg, #22c55e 0%, #16a34a 100%);
}

.config-item-inline.status-disabled {
  background: linear-gradient(135deg, rgba(254, 249, 195, 0.9) 0%, rgba(254, 240, 138, 0.6) 100%);
  border-color: rgba(234, 179, 8, 0.2);
  box-shadow: 0 4px 12px rgba(234, 179, 8, 0.1);
}

.config-item-inline.status-disabled::before {
  background: linear-gradient(180deg, #eab308 0%, #ca8a04 100%);
}

.config-item-inline.status-unconfigured {
  background: linear-gradient(135deg, rgba(254, 242, 242, 0.9) 0%, rgba(254, 226, 226, 0.6) 100%);
  border-color: rgba(239, 68, 68, 0.2);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.1);
}

.config-item-inline.status-unconfigured::before {
  background: linear-gradient(180deg, #ef4444 0%, #dc2626 100%);
}

.status-symbol {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  font-size: 20px;
}

.config-label {
  font-size: 0.95rem;
  color: #334155;
  font-weight: 600;
  flex-shrink: 0;
}

.config-name {
  font-size: 0.85rem;
  color: #64748b;
  margin-left: 4px;
  font-weight: 500;
}

.status-text {
  margin-left: auto;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 700;
  background: #ef4444;
  color: white;
  white-space: nowrap;
  box-shadow: 0 2px 6px rgba(239, 68, 68, 0.2);
}

.status-text.warning {
  background: #eab308;
  box-shadow: 0 2px 6px rgba(234, 179, 8, 0.2);
}

.guide-actions {
  display: flex !important;
  flex-direction: column !important;
  align-items: center !important;
  gap: 12px;
  margin-top: 30px;
  width: 100%;
}

.guide-actions button {
  flex: none !important;
  width: 240px !important;
  height: 50px !important;
  padding: 0 24px !important;
  border-radius: 12px;
  font-size: 0.95rem;
  font-weight: 600;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  text-align: center;
  white-space: nowrap;
  opacity: 1 !important;
  cursor: pointer;
  box-sizing: border-box !important;
}

.guide-actions .generate-manual-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
  color: white !important;
  border: 2px solid transparent !important;
  box-shadow: 0 2px 10px rgba(102, 126, 234, 0.3);
}

.guide-actions .skip-action {
  font-size: 0.85rem;
  color: #94a3b8;
  cursor: pointer;
  text-decoration: none;
  padding: 4px 8px;
  transition: color 0.3s;
}

.guide-actions .skip-action:hover {
  color: #64748b;
  text-decoration: underline;
}


.manual-input-card, .upload-card {
  background: white;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  border: 1px solid #e1e8ed;
  margin-bottom: 30px;
}

.manual-input-card h2, .upload-card h2 {
  color: #2c3e50;
  margin-bottom: 20px;
  font-size: 1.5rem;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #2c3e50;
}

/* 输出模式选择器 */
.output-mode-selector {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.mode-option {
  position: relative;
  cursor: pointer;
}

.mode-option input[type="radio"] {
  position: absolute;
  opacity: 0;
  width: 0;
  height: 0;
}

.mode-content {
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  padding: 16px;
  transition: all 0.3s ease;
  background: white;
}

.mode-option:hover .mode-content {
  border-color: #3b82f6;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1);
}

.mode-option.active .mode-content {
  border-color: #3b82f6;
  background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
  box-shadow: 0 4px 16px rgba(59, 130, 246, 0.2);
}

.mode-title {
  font-size: 1rem;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 6px;
}

.mode-desc {
  font-size: 0.85rem;
  color: #64748b;
  line-height: 1.4;
}

.mode-option.active .mode-title {
  color: #2563eb;
}

.mode-option.active .mode-desc {
  color: #475569;
}

.form-input, .form-select, .form-textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
  transition: border-color 0.3s ease;
}

.form-input:focus, .form-select:focus, .form-textarea:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

.form-textarea {
  resize: vertical;
  font-family: inherit;
}

.char-count {
  text-align: right;
  font-size: 0.85rem;
  color: #666;
  margin-top: 5px;
}

.required {
  color: #e74c3c;
}

.generate-manual-btn, .generate-btn {
  background: #27ae60;
  color: white;
  border: none;
  padding: 15px 30px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1.1rem;
  transition: background 0.3s ease;
  width: 100%;
  margin-top: 10px;
}

.generate-manual-btn:hover:not(:disabled), .generate-btn:hover:not(:disabled) {
  background: #219a52;
}

.generate-manual-btn:disabled, .generate-btn:disabled {
  background: #bdc3c7;
  cursor: not-allowed;
}

.divider {
  text-align: center;
  margin: 40px 0;
  position: relative;
}

.divider::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 1px;
  background: #ddd;
}

.divider span {
  background: white;
  padding: 0 20px;
  color: #666;
  font-size: 1rem;
}

.upload-area {
  border: 2px dashed #ddd;
  border-radius: 8px;
  padding: 40px;
  text-align: center;
  transition: border-color 0.3s ease;
  margin-bottom: 20px;
}

.upload-area.drag-over {
  border-color: #3498db;
  background: #f8f9fa;
}

.upload-placeholder {
  color: #666;
}

.upload-icon {
  font-size: 3rem;
  margin-bottom: 15px;
  display: block;
}

.upload-hint {
  color: #999;
  font-size: 0.9rem;
  margin-top: 5px;
}

.select-file-btn {
  background: #3498db;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  margin-top: 15px;
}

.file-selected {
  padding: 20px;
  background: #f8f9fa;
  border-radius: 6px;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.file-icon {
  font-size: 2rem;
}

.file-details {
  flex: 1;
}

.file-name {
  font-weight: 600;
  margin: 0;
}

.file-size {
  color: #666;
  font-size: 0.9rem;
  margin: 5px 0 0 0;
}

.remove-file {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.2rem;
}

.generation-progress {
  margin: 40px 0;
}

.progress-card {
  background: white;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  border: 1px solid #e1e8ed;
  text-align: center;
}

.progress-card h3 {
  color: #2c3e50;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  flex-wrap: wrap;
}

.current-mode-badge {
  display: inline-block;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 500;
  margin-left: 8px;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.progress-info {
  display: flex;
  justify-content: center;
  gap: 30px;
  margin-bottom: 30px;
  flex-wrap: wrap;
}

.progress-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.progress-item .label {
  font-size: 0.9rem;
  color: #666;
}

.progress-item .value {
  font-weight: 600;
  color: #2c3e50;
}

/* 流式内容显示区域 */
.stream-content-display {
  margin: 20px 0;
  border: 2px solid #e1e8ed;
  border-radius: 8px;
  overflow: hidden;
  background: #f8f9fa;
}

.stream-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #e9ecef;
  border-bottom: 1px solid #dee2e6;
}

.stream-title {
  font-weight: 600;
  color: #495057;
  font-size: 0.95rem;
}

.stream-status {
  font-size: 0.85rem;
  color: #6c757d;
  background: white;
  padding: 4px 10px;
  border-radius: 12px;
  border: 1px solid #dee2e6;
}

.stream-content {
  max-height: 400px;
  overflow-y: auto;
  padding: 16px;
  text-align: left;
  background: white;
  font-size: 0.9rem;
  line-height: 1.6;
  color: #2c3e50;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.stream-content::-webkit-scrollbar {
  width: 8px;
}

.stream-content::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.stream-content::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

.stream-content::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 最终版用例特殊样式 */
.stream-content.final-testcases {
  background: #f0f7ff;
  border-left: 4px solid #2196F3;
}

.stream-content.final-testcases::before {
  content: '📋 最终版本';
  display: block;
  font-weight: 600;
  color: #2196F3;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 2px solid #e3f2fd;
}

/* 流式输出指示器 */
.streaming-indicator {
  font-size: 0.85em;
  margin-left: 8px;
  color: #4CAF50;
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.stream-content h1,
.stream-content h2,
.stream-content h3,
.stream-content h4,
.stream-content h5,
.stream-content h6 {
  margin-top: 1em;
  margin-bottom: 0.5em;
  color: #2c3e50;
  font-weight: 600;
}

.stream-content code {
  background: #f1f3f5;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 0.85em;
}

.stream-content pre {
  background: #f1f3f5;
  padding: 12px;
  border-radius: 6px;
  overflow-x: auto;
  margin: 10px 0;
}

.stream-content pre code {
  background: none;
  padding: 0;
}

.progress-steps {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-bottom: 30px;
  flex-wrap: wrap;
}

.step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  opacity: 0.4;
  transition: opacity 0.3s ease;
}

.step.active {
  opacity: 1;
}

.step-number {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #ddd;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  color: white;
}

.step.active .step-number {
  background: #3498db;
}

.step-text {
  font-size: 0.9rem;
  color: #666;
}

.cancel-generation-btn {
  background: #e74c3c;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
}

.completion-actions {
  display: flex;
  gap: 12px;
  margin-top: 20px;
  flex-wrap: wrap;
}

.completion-actions button {
  flex: 1;
  min-width: 150px;
  padding: 12px 20px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.completion-actions .download-btn {
  background: #28a745;
  color: white;
  font-size: 1rem;
}

.completion-actions .download-btn:hover {
  background: #218838;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(40, 167, 69, 0.3);
}

.completion-actions .save-btn {
  background: #007bff;
  color: white;
  font-size: 1rem;
}

.completion-actions .save-btn:hover {
  background: #0056b3;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 123, 255, 0.3);
}

.completion-actions .new-generation-btn {
  background: #6c757d;
  color: white;
  font-size: 1rem;
}

.completion-actions .new-generation-btn:hover {
  background: #5a6268;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(108, 117, 125, 0.3);
}

.generation-result {
  margin: 40px 0;
}

.result-header {
  background: white;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  border: 1px solid #e1e8ed;
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 20px;
}

.result-header h2 {
  color: #27ae60;
  margin: 0;
}

.result-summary {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.summary-item {
  color: #666;
  font-size: 0.9rem;
}

.new-generation-btn {
  background: #3498db;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
}

.generated-testcases-section, .review-feedback-section, .final-testcases-section {
  background: white;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  border: 1px solid #e1e8ed;
  margin-bottom: 20px;
}

.generated-testcases-section h3, .review-feedback-section h3, .final-testcases-section h3 {
  color: #2c3e50;
  margin-bottom: 20px;
}

.testcase-content, .review-content {
  background: #f8f9fa;
  border-radius: 6px;
  padding: 20px;
  border-left: 4px solid #3498db;
}

.testcase-content pre, .review-content pre {
  white-space: pre-wrap;
  word-wrap: break-word;
  margin: 0;
  font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
  font-size: 0.9rem;
  line-height: 1.6;
}

@media (max-width: 768px) {
  .result-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .progress-info, .result-summary {
    flex-direction: column;
    gap: 10px;
  }
  
  .progress-steps {
    gap: 10px;
  }
}

.actions-section {
  display: flex;
  gap: 20px;
  justify-content: center;
  margin-top: 30px;
  flex-wrap: wrap;
}

.download-btn, .save-btn {
  padding: 12px 24px;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
}

.download-btn {
  background-color: #1abc9c;
  color: white;
}

.download-btn:hover {
  background-color: #16a085;
}

.save-btn {
  background-color: #3498db;
  color: white;
}

.save-btn:hover {
  background-color: #2980b9;
}

@media (max-width: 768px) {
  .actions-section {
    flex-direction: column;
    align-items: center;
  }

  .download-btn, .save-btn {
    width: 100%;
    max-width: 300px;
    justify-content: center;
  }
}
</style>

<style>
/* 全局样式：确保弹窗不受任何容器限制 */
.modal-overlay {
  position: fixed !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  width: 100vw !important;
  height: 100vh !important;
  max-width: none !important;
  max-height: none !important;
  background: rgba(15, 23, 42, 0.6) !important;
  backdrop-filter: blur(4px);
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  z-index: 9999 !important;
  padding: 20px;
  margin: 0 !important;
  opacity: 1 !important;
  box-sizing: border-box !important;
}

.guide-config-modal {
  background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%) !important;
  border-radius: 24px;
  padding: 36px;
  max-width: 850px !important;
  width: 100% !important;
  min-width: 300px !important;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
  border: 1px solid rgba(226, 232, 240, 0.8);
  position: relative;
  flex-shrink: 0;
  margin: auto;
  opacity: 1 !important;
  box-sizing: border-box !important;
}

/* 全局按钮样式 */
.guide-actions {
  display: flex !important;
  flex-direction: column !important;
  align-items: center !important;
  gap: 12px;
  margin-top: 30px;
  width: 100%;
}

.guide-actions button {
  flex: none !important;
  width: 240px !important;
  height: 50px !important;
  padding: 0 24px !important;
  border-radius: 12px;
  font-size: 0.95rem;
  font-weight: 600;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  text-align: center;
  white-space: nowrap;
  opacity: 1 !important;
  box-sizing: border-box !important;
  cursor: pointer;
}

.guide-actions .generate-manual-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
  color: white !important;
  border: 2px solid transparent !important;
  box-shadow: 0 2px 10px rgba(102, 126, 234, 0.3);
}

.guide-actions .skip-action {
  font-size: 0.85rem;
  color: #94a3b8;
  cursor: pointer;
  text-decoration: none;
  padding: 4px 8px;
  transition: color 0.3s;
}

.guide-actions .skip-action:hover {
  color: #64748b;
  text-decoration: underline;
}

/* ──────────── 需求文档生成区块 ──────────── */
.req-doc-section {
  width: 100%;
}

.req-doc-card {
  background: linear-gradient(135deg, #ffffff 0%, #f8faff 100%);
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  padding: 28px 32px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
}

.req-doc-header {
  margin-bottom: 20px;
}

.req-doc-header h2 {
  font-size: 1.3rem;
  color: #1a202c;
  margin: 0 0 6px 0;
  font-weight: 700;
}

.req-doc-desc {
  color: #64748b;
  font-size: 0.9rem;
  margin: 0;
}

.req-doc-actions {
  display: flex;
  gap: 12px;
  margin-top: 16px;
  flex-wrap: wrap;
}

.req-doc-btn {
  padding: 10px 22px;
  border-radius: 10px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
}

.req-doc-btn.primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.req-doc-btn.primary:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.45);
}

.req-doc-btn.secondary {
  background: #f1f5f9;
  color: #475569;
  border: 1px solid #e2e8f0;
}

.req-doc-btn.secondary:hover:not(:disabled) {
  background: #e2e8f0;
}

.req-doc-btn:disabled {
  opacity: 0.55;
  cursor: not-allowed;
  transform: none !important;
}

/* 编辑器区域 */
.req-doc-editor {
  margin-top: 16px;
}

.editor-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
  padding: 10px 14px;
  background: #f8faff;
  border: 1px solid #e2e8f0;
  border-radius: 10px 10px 0 0;
}

.editor-label {
  font-size: 0.9rem;
  font-weight: 600;
  color: #374151;
}

.editor-toolbar-actions {
  display: flex;
  gap: 8px;
}

.toolbar-btn {
  padding: 6px 14px;
  border-radius: 6px;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  border: 1px solid #e2e8f0;
  background: white;
  color: #475569;
  transition: all 0.15s;
}

.toolbar-btn:hover {
  background: #f1f5f9;
}

.toolbar-btn.danger {
  color: #dc2626;
  border-color: #fca5a5;
}

.toolbar-btn.danger:hover {
  background: #fef2f2;
}

.req-doc-textarea {
  width: 100%;
  box-sizing: border-box;
  border: 1px solid #e2e8f0;
  border-top: none;
  border-radius: 0 0 10px 10px;
  padding: 16px;
  font-family: 'Menlo', 'Monaco', 'Consolas', monospace;
  font-size: 0.88rem;
  line-height: 1.7;
  color: #1e293b;
  background: #fafbff;
  resize: vertical;
  outline: none;
  transition: border-color 0.2s;
}

.req-doc-textarea:focus {
  border-color: #667eea;
  background: #fff;
}

.req-doc-preview {
  border: 1px solid #e2e8f0;
  border-top: none;
  border-radius: 0 0 10px 10px;
  padding: 20px 24px;
  min-height: 280px;
  background: #fff;
  overflow-y: auto;
}

/* 底部行：项目选择 + 生成按钮 */
.req-doc-generate-row {
  display: flex;
  align-items: flex-end;
  gap: 16px;
  margin-top: 16px;
  flex-wrap: wrap;
}

.project-select-inline {
  flex: 1;
  min-width: 200px;
  margin: 0 !important;
}

.project-select-inline label {
  display: block;
  font-size: 0.85rem;
  color: #64748b;
  margin-bottom: 6px;
}

.use-req-doc-btn {
  flex-shrink: 0;
  padding: 10px 28px;
  font-size: 1rem;
}

/* 输入方式 Tab */
.rd-tabs {
  display: flex;
  gap: 4px;
  margin-bottom: 14px;
  border-bottom: 2px solid #e2e8f0;
  padding-bottom: 0;
}

.rd-tab {
  padding: 8px 20px;
  border: none;
  background: transparent;
  font-size: 0.9rem;
  font-weight: 600;
  color: #94a3b8;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  transition: all 0.15s;
  border-radius: 6px 6px 0 0;
}

.rd-tab.active {
  color: #667eea;
  border-bottom-color: #667eea;
  background: #f5f7ff;
}

.rd-tab:hover:not(.active) {
  color: #475569;
  background: #f8faff;
}

.rd-text-input {
  margin-top: 0;
}

/* 文件上传区 */
.rd-upload-zone {
  margin-bottom: 4px;
}

/* 双入口布局（文件 / 文件夹） */
.rd-upload-entries {
  display: flex;
  gap: 12px;
}

.rd-upload-entries .rd-drop-zone {
  flex: 1;
  min-width: 0;
}

.rd-folder-zone {
  border-color: #bfdbfe !important;
  background: #f0f9ff !important;
}

.rd-folder-zone:hover {
  border-color: #3b82f6 !important;
  background: #e0f2fe !important;
}

.rd-drop-zone {
  border: 2px dashed #c7d2fe;
  border-radius: 12px;
  padding: 32px 20px;
  text-align: center;
  cursor: pointer;
  background: #f8faff;
  transition: all 0.2s;
}

.rd-drop-zone:hover {
  border-color: #667eea;
  background: #f0f3ff;
}

.rd-drop-icon {
  font-size: 2.2rem;
  margin-bottom: 8px;
}

.rd-drop-title {
  font-size: 1rem;
  font-weight: 600;
  color: #374151;
  margin: 0 0 4px 0;
}

.rd-drop-hint {
  font-size: 0.82rem;
  color: #94a3b8;
  margin: 0;
}

/* 文件夹分组标题 */
.rd-folder-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  margin-top: 8px;
  background: #f0f9ff;
  border: 1px solid #bfdbfe;
  border-radius: 10px;
}

.rd-folder-icon {
  font-size: 1.4rem;
  flex-shrink: 0;
}

.rd-folder-name {
  font-size: 0.95rem;
  font-weight: 700;
  color: #1e40af;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.rd-folder-count {
  font-size: 0.8rem;
  color: #64748b;
  margin-left: auto;
  flex-shrink: 0;
}

.rd-folder-clear {
  flex-shrink: 0;
  border: none;
  background: none;
  color: #94a3b8;
  font-size: 1.1rem;
  cursor: pointer;
  padding: 2px 6px;
  border-radius: 4px;
  transition: all 0.15s;
}

.rd-folder-clear:hover {
  color: #ef4444;
  background: #fee2e2;
}

/* 文件夹内子文件缩进 */
.rd-file-sub {
  margin-left: 24px;
  background: #fafbfe;
}

/* 已选文件列表 */
.rd-file-list {
  margin-top: 12px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.rd-file-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  background: #f8faff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
}

.rd-file-icon {
  font-size: 1.4rem;
  flex-shrink: 0;
}

.rd-file-name {
  flex: 1;
  font-size: 0.9rem;
  color: #1e293b;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.rd-extract-status {
  font-size: 0.82rem;
  font-weight: 600;
  flex-shrink: 0;
}

.rd-extract-status.extracting {
  color: #f59e0b;
}

.rd-extract-status.done {
  color: #10b981;
}

.rd-extract-status.image-pdf {
  color: #8b5cf6;
  font-size: 0.8rem;
}

.rd-extract-status.error {
  color: #dc2626;
  font-size: 0.8rem;
  cursor: help;
}

.rd-file-clear {
  flex-shrink: 0;
  width: 26px;
  height: 26px;
  border-radius: 50%;
  border: 1px solid #e2e8f0;
  background: white;
  color: #94a3b8;
  cursor: pointer;
  font-size: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
}

.rd-file-clear:hover:not(:disabled) {
  background: #fef2f2;
  color: #dc2626;
  border-color: #fca5a5;
}

.rd-file-clear:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

/* ──────────── 历史文档面板 ──────────── */
.history-section {
  width: 100%;
  margin-bottom: 30px;
}

.history-card {
  background: linear-gradient(135deg, #ffffff 0%, #fafbfe 100%);
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  padding: 24px 28px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
}

.history-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.history-header h2 {
  font-size: 1.2rem;
  color: #1a202c;
  margin: 0;
  font-weight: 700;
  flex-shrink: 0;
}

.history-version-row {
  display: flex;
  align-items: center;
  gap: 0;
}

.history-count {
  font-size: 0.85rem;
  color: #94a3b8;
  background: #f1f5f9;
  padding: 4px 12px;
  border-radius: 20px;
  font-weight: 600;
}

.history-loading,
.history-empty,
.history-error {
  text-align: center;
  padding: 24px 16px;
  color: #94a3b8;
  font-size: 0.9rem;
}

.history-error {
  color: #ef4444;
}

.history-error a {
  color: #667eea;
  text-decoration: underline;
  cursor: pointer;
}

.history-empty {
  color: #94a3b8;
  line-height: 1.8;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.history-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 14px 18px;
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  transition: all 0.2s;
}

.history-item:hover {
  border-color: #c7d2fe;
  box-shadow: 0 2px 12px rgba(102, 126, 234, 0.08);
}

.history-item-main {
  flex: 1;
  min-width: 0;
}

.history-item-title {
  font-size: 0.95rem;
  font-weight: 600;
  color: #1e293b;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 4px;
}

.history-item-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 0.82rem;
  color: #94a3b8;
}

.history-source {
  color: #64748b;
}

.history-time {
  color: #94a3b8;
}

.history-item-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.history-btn {
  padding: 7px 16px;
  border-radius: 8px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  border: 1px solid;
  transition: all 0.2s;
  white-space: nowrap;
}

.history-btn.view {
  background: #f8faff;
  border-color: #e2e8f0;
  color: #475569;
}

.history-btn.view:hover {
  background: #eef2ff;
  border-color: #c7d2fe;
}

.history-btn.generate {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-color: transparent;
  color: white;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.history-btn.generate:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 14px rgba(102, 126, 234, 0.4);
}

.history-btn.del {
  background: #fff5f5;
  border-color: #fecaca;
  color: #ef4444;
}

.history-btn.del:hover {
  background: #fee2e2;
  border-color: #fca5a5;
  color: #dc2626;
}

.history-btn.edit {
  background: #fff7ed;
  border-color: #fed7aa;
  color: #c2410c;
}

.history-btn.edit:hover {
  background: #ffedd5;
  border-color: #fdba74;
  color: #9a3412;
}

/* ── 历史文档预览弹窗 ── */
.history-preview-modal {
  background: #fff;
  border-radius: 20px;
  padding: 32px;
  max-width: 820px;
  width: 100%;
  max-height: 85vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
  position: relative;
}

.preview-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e2e8f0;
}

.preview-header h3 {
  font-size: 1.25rem;
  color: #1a202c;
  margin: 0;
  font-weight: 700;
}

.preview-close {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: 1px solid #e2e8f0;
  background: white;
  color: #94a3b8;
  font-size: 1rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
}

.preview-close:hover {
  background: #fef2f2;
  color: #dc2626;
  border-color: #fca5a5;
}

.preview-body {
  padding: 20px;
  background: #f8faff;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  max-height: 50vh;
  overflow-y: auto;
  margin-bottom: 20px;
}

.preview-body :deep(h1),
.preview-body :deep(h2),
.preview-body :deep(h3) {
  color: #1a202c;
}

.preview-body :deep(p) {
  line-height: 1.7;
  color: #334155;
}

/* ── 编辑模式 ── */
.edit-title-input {
  flex: 1;
  padding: 8px 14px;
  margin-right: 12px;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 1.15rem;
  font-weight: 700;
  color: #1a202c;
  background: #fff;
  box-sizing: border-box;
}

.edit-title-input:focus {
  outline: none;
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.edit-body {
  margin-bottom: 20px;
}

.edit-textarea {
  width: 100%;
  min-height: 50vh;
  padding: 20px;
  border: 1px solid #cbd5e1;
  border-radius: 12px;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 0.9rem;
  line-height: 1.7;
  color: #1a202c;
  background: #fafbfc;
  resize: vertical;
  box-sizing: border-box;
}

.edit-textarea:focus {
  outline: none;
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.preview-actions {
  display: flex;
  justify-content: center;
}

/* ── 快速创建版本弹窗 ── */
.quick-version-modal,
.generate-confirm-modal {
  background: #fff;
  border-radius: 16px;
  padding: 28px 32px;
  max-width: 480px;
  width: 100%;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
  position: relative;
}

.generate-confirm-modal .form-group {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.generate-confirm-modal .form-group label {
  min-width: 70px;
}

/* ── 生成模式选择器 ── */
.generation-mode-selector {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.generation-mode-selector .mode-option {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  padding: 8px 8px;
  border: 2px solid #e2e8f0;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
  flex: 1;
  min-width: 70px;
  text-align: center;
}

.generation-mode-selector .mode-option:hover {
  border-color: #6366f1;
  background: #f5f3ff;
}

.generation-mode-selector .mode-option.active {
  border-color: #6366f1;
  background: #eef2ff;
  box-shadow: 0 0 0 2px rgba(99,102,241,0.15);
}

.generation-mode-selector .mode-radio {
  display: none;
}

.generation-mode-selector .mode-icon {
  font-size: 1.2rem;
  line-height: 1;
}

.generation-mode-selector .mode-name {
  font-size: 0.78rem;
  font-weight: 600;
  color: #1a202c;
  white-space: nowrap;
}

.generation-mode-selector .mode-desc {
  font-size: 0.68rem;
  color: #94a3b8;
  white-space: nowrap;
  line-height: 1.2;
}

.quick-version-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.quick-version-header h3 {
  font-size: 1.15rem;
  color: #1a202c;
  margin: 0;
  font-weight: 700;
}

.quick-version-body .form-group {
  margin-bottom: 16px;
}

.quick-version-body .form-group label {
  display: block;
  font-size: 0.85rem;
  color: #475569;
  margin-bottom: 6px;
  font-weight: 500;
}

.quick-version-body .form-group .required {
  color: #ef4444;
  margin-left: 2px;
}

.quick-version-body .form-input {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 0.9rem;
  background: #fff;
  transition: border-color 0.15s;
  box-sizing: border-box;
}

.quick-version-body .form-input:focus {
  outline: none;
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.quick-version-body .form-select {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 0.9rem;
  background: #fff;
  box-sizing: border-box;
}

.quick-version-body .checkbox-label {
  display: flex !important;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 0.85rem;
}

.quick-version-body .checkbox-label input[type="checkbox"] {
  width: 16px;
  height: 16px;
  accent-color: #6366f1;
}

.quick-version-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid #e2e8f0;
}

/* ── 版本选择器行（下拉 + 新建按钮）── */
.version-select-row {
  display: flex;
  gap: 6px;
  align-items: center;
}

.version-select-row .version-select {
  flex: 1;
}

.quick-create-ver-btn {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  border: 1px dashed #cbd5e1;
  background: #f8fafc;
  color: #6366f1;
  font-size: 1.1rem;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
  flex-shrink: 0;
  padding: 0;
  line-height: 1;
}

.quick-create-ver-btn:hover {
  border-style: solid;
  border-color: #6366f1;
  background: #eef2ff;
  transform: scale(1.05);
}

.project-select-inline .version-select-row {
  display: flex;
  gap: 6px;
  align-items: center;
}
</style>