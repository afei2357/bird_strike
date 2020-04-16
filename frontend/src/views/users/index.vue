<template>
  <maincontent 
      :mainName="mainName"
      :subConfig="subElConfig"
      :rules="rules"
      :formData="formData"
      :tableConfig="tableConfig"
      :getRecord="getRecord" 
      :createDataForm="postUsers"
      :updateDataForm="putUsers"
      />
</template>
<script>
  import { getRecord, postUsers, putUsers } from '@/api/user'
  import { validatAlphabets } from '@/utils/validate_form'
  import maincontent from './main'
  export default {
    components: {
      maincontent
    },
    methods: {
      getRecord,
      postUsers,
      putUsers
    },
    data() {
      return {
        mainName: 'users',
        tableConfig: [
          {
            name: 'name',
            label: '联系人',
            prop: 'name'
          },
          {
            name: 'username',
            label: '用户名',
            prop: 'username'
          },
          {
            name: 'channel',
            label: '部门',
            prop: 'channel'
          },
          {
            name: 'role_name',
            label: '角色',
            prop: 'role_name'
          },
          { 
            name: 'orders',
            label: '订单数',
            prop: 'orders'
          },
          {
            name: 'email',
            label: 'Email',
            prop: 'email'
          },
          {
            name: 'confirmed',
            label: 'Email确认',
            prop: 'confirmed'
          },
          {
            name: 'member_since',
            label: '用户创建时间',
            prop: 'member_since',
            width: '200px'
          },
          {
            name: 'last_seen',
            label: '上次登录时间',
            prop: 'last_seen'
          }
        ],
         // 主表单需要收集的form数据
        formData: {
          username: '',
          name: '',
          email: '',
          role_name: '',
          password: ''
        },
        subElConfig: {
          fieldsConfig: [
            {
              name: 'name',
              label: '姓名',
              prop: 'name',
              fieldType: 'TextInput',
              placeholder: '请输入姓名'
            },
            {
              name: 'username',
              label: '用户名',
              prop: 'username',
              fieldType: 'TextInput',
              placeholder: '请输入用户名'
            },
            {
              name: 'role_name',
              label: '角色名',
              prop: 'role_name',
              fieldType: 'autoComplete',
              querySearch: 'getRolesinfo'
            },
            {
              name: 'email',
              label: '电子邮箱',
              prop: 'email',
              fieldType: 'TextInput',
              placeholder: '请输入邮箱'
            },
            {
              name: 'password',
              label: '密码',
              prop: 'password',
              fieldType: 'TextInput',
              placeholder: '请输入密码'
            }
          ]
        },
        // 表单验证规则
        rules: {
          name: [
            { required: true, message: '请输入姓名', trigger: 'blur' },
            { min: 2, max: 5, message: '长度在 2 到 5 个字符', trigger: 'blur' }
          ],
          username: [
            { required: true, message: '请输入用户名', trigger: 'blur' },
            { min: 3, max: 10, message: '长度在 3 到 10 个字符', trigger: 'blur' }
          ],
          email: [
            { required: true, message: '请输入正确邮箱', trigger: 'blur' },
            { pattern:/^([a-zA-Z0-9]+[-_\.]?)+@[a-zA-Z0-9]+\.[a-z]+$/, trigger: 'blur' }
          ],
          password: [
            { required: true, message: '', trigger: 'blur' },
            { min: 6, pattern:/^[_a-zA-Z0-9]+$/, message:'密码6位以上，仅由英文字母，数字以及下划线组成', trigger: 'blur' }
          ]
        }
    }
  }
}

</script>