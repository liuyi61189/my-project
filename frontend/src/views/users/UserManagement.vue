<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">用户管理</h1>
      <el-button type="primary" @click="openCreateDialog">
        <el-icon><Plus /></el-icon>
        新建用户
      </el-button>
    </div>

    <div class="card-container">
      <!-- 搜索栏 -->
      <div class="filter-bar">
        <el-input
          v-model="searchText"
          placeholder="搜索用户名或邮箱"
          clearable
          style="width: 280px"
          @input="handleSearch"
        >
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
      </div>

      <el-table :data="users" v-loading="loading" style="width: 100%">
        <el-table-column prop="username" label="用户名" width="140" />
        <el-table-column prop="email" label="邮箱" min-width="200" />
        <el-table-column prop="department" label="部门" width="120" />
        <el-table-column prop="position" label="职位" width="120" />
        <el-table-column prop="is_active" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="date_joined" label="注册时间" width="180">
          <template #default="{ row }">{{ formatDate(row.date_joined) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEditDialog(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteUser(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="total"
          layout="total, prev, pager, next"
          @current-change="fetchUsers"
        />
      </div>
    </div>

    <!-- 新建/编辑用户弹窗 -->
    <el-dialog
      v-model="showDialog"
      :title="isEdit ? '编辑用户' : '新建用户'"
      width="520px"
      destroy-on-close
      @close="resetForm"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" :disabled="isEdit" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item v-if="!isEdit" label="密码" prop="password">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" show-password />
        </el-form-item>
        <el-form-item v-if="!isEdit" label="确认密码" prop="password_confirm">
          <el-input v-model="form.password_confirm" type="password" placeholder="请确认密码" show-password />
        </el-form-item>
        <el-form-item label="姓名">
          <el-input v-model="form.first_name" placeholder="姓" style="width:48%;margin-right:4%" />
          <el-input v-model="form.last_name" placeholder="名" style="width:48%" />
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="form.phone" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item label="部门">
          <el-input v-model="form.department" placeholder="请输入部门" />
        </el-form-item>
        <el-form-item label="职位">
          <el-input v-model="form.position" placeholder="请输入职位" />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="form.is_active" active-text="启用" inactive-text="禁用" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          {{ isEdit ? '保存' : '创建' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus } from '@element-plus/icons-vue'
import api from '@/utils/api'
import dayjs from 'dayjs'

const loading = ref(false)
const submitting = ref(false)
const showDialog = ref(false)
const isEdit = ref(false)
const formRef = ref(null)

const users = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const searchText = ref('')

const form = reactive({
  id: null,
  username: '',
  email: '',
  password: '',
  password_confirm: '',
  first_name: '',
  last_name: '',
  phone: '',
  department: '',
  position: '',
  is_active: true
})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '3-50个字符', trigger: 'blur' }
  ],
  email: [
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' }
  ],
  password_confirm: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (_rule, value, callback) => {
        if (value !== form.password) {
          callback(new Error('两次密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

const fetchUsers = async () => {
  loading.value = true
  try {
    const params = { page: currentPage.value }
    if (searchText.value) params.search = searchText.value
    const res = await api.get('/auth/users/', { params })
    users.value = res.data.results || res.data || []
    total.value = res.data.count || 0
  } catch {
    ElMessage.error('获取用户列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  fetchUsers()
}

const openCreateDialog = () => {
  isEdit.value = false
  showDialog.value = true
}

const openEditDialog = (row) => {
  isEdit.value = true
  form.id = row.id
  form.username = row.username
  form.email = row.email || ''
  form.first_name = row.first_name || ''
  form.last_name = row.last_name || ''
  form.phone = row.phone || ''
  form.department = row.department || ''
  form.position = row.position || ''
  form.is_active = row.is_active
  form.password = ''
  form.password_confirm = ''
  showDialog.value = true
}

const resetForm = () => {
  Object.assign(form, {
    id: null, username: '', email: '', password: '', password_confirm: '',
    first_name: '', last_name: '', phone: '', department: '', position: '',
    is_active: true
  })
  formRef.value?.resetFields()
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    submitting.value = true
    try {
      if (isEdit.value) {
        // 编辑时不传密码
        const { password, password_confirm, ...payload } = form
        await api.put(`/auth/users/${form.id}/`, payload)
        ElMessage.success('用户更新成功')
      } else {
        await api.post('/auth/users/', form)
        ElMessage.success('用户创建成功')
      }
      showDialog.value = false
      resetForm()
      fetchUsers()
    } catch (e) {
      const msg = e.response?.data
      if (typeof msg === 'object') {
        // Django 字段校验错误
        const firstKey = Object.keys(msg)[0]
        ElMessage.error(msg[firstKey]?.[0] || '操作失败')
      } else {
        ElMessage.error(msg || '操作失败')
      }
    } finally {
      submitting.value = false
    }
  })
}

const deleteUser = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除用户「${row.username}」吗？此操作不可撤销。`, '警告', {
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await api.delete(`/auth/users/${row.id}/`)
    ElMessage.success('用户已删除')
    fetchUsers()
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const formatDate = (d) => dayjs(d).format('YYYY-MM-DD HH:mm')

onMounted(fetchUsers)
</script>

<style lang="scss" scoped>
.filter-bar {
  margin-bottom: 16px;
}
.pagination-container {
  margin-top: 16px;
  display: flex;
  justify-content: center;
}
</style>
