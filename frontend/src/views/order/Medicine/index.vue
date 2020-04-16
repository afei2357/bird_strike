<template>
  <maincontent
      :tableConfig="tableConfig"
      :subConfig="subElConfig"
      :formData="formData"
      :rules="rules"
      :getRecord="getRecord" 
      :createDataForm="postCreate"
      :updateDataForm="putUpdate"
      :deleteRecord="delRecord"
      />
</template>
<script>
  import { getRecord, postCreate, putUpdate, delRecord} from '@/api/order'
  import maincontent from '../main'
  export default {
    components: {
      maincontent
    },
    methods: {
      getRecord,
      postCreate,
      putUpdate,
      delRecord
    },
    data() {
      return {
        tableConfig: [
          {
            name: 'order_num',
            label: '订单号',
            prop: 'order_num'
          }, 
          {
            name: 'name',
            label: '姓名',
            prop: 'name'
          },
          {
            name: 'sample_code',
            label: '样本编码',
            prop: 'sample_code'
          },
          {
            name: 'detection_items',
            label: '检测项目',
            prop: 'detection_items'
          },
          {
            name: 'hospital',
            label: '医院',
            prop: 'hospital'
          },
          {
            name: 'receive_date',
            label: '收样日期',
            prop: 'receive_date'
          },
          {
            name: 'report_date',
            label: '报告时间',
            prop: 'report_date'
          }
        ],
        // 主表单需要收集的form数据
        formData: {
          name: '',
          gender: '',
          sample_code: '',
          birthday: '',
          phone: '',
          hospital: '',
          department: '',
          clinical_bg: '',
          report_date: '',
          detection_items: ''
        },
        subElConfig: {
          fieldsConfig: [{
              name: 'name',
              label: '姓名',
              prop: 'name',
              fieldType: 'TextInput',
              placeholder: '请输入姓名',
              col: 12
            },
            {
              name: 'gender',
              label: '性别',
              prop: 'gender',
              fieldType: 'Radio',
              options: [{
                  label: '男',
                  value: '1'
                },
                {
                  label: '女',
                  value: '0'
                }]
            },
            {
              name: 'sample_code',
              label: '样本编号',
              prop: 'sample_code',
              fieldType: 'TextInput'
            },
            {
              name: 'birthday',
              label: '出生日期',
              prop: 'birthday',
              fieldType: 'DatePicker'
            },
            {
              name: 'phone',
              prop: 'phone',
              label: '手机号',
              fieldType: 'NumInput'
            },
            {
              name: 'detection_items',
              label: '检测项目',
              prop: 'detection_items',
              fieldType: 'autoComplete',
              querySearch: 'ghealthProduct'
            },
            {
              name: 'hospital',
              prop: 'hospital',
              label: '医院',
              fieldType: 'TextInput'
            },
            {
              name: 'department',
              prop: 'department',
              label: '科室',
              fieldType: 'TextInput'
            },
            {
              name: 'clinical_bg',
              prop: 'clinical_bg',
              label: '临床背景',
              fieldType: 'TextInput'               
            }
          ]
        },
        // 表单验证规则
        rules: {
          name: [
            { required: true, message: '请输入姓名', trigger: 'blur' },
            { min: 2, max: 5, message: '长度在 2 到 5 个字符', trigger: 'blur' }
          ],
          gender: [{ message: '必填项', required: 'true' }],
          sample_code: [{ message: '必填项', required: 'true' }],
          detection_items: [{ message: '必填项', required: 'true' }]
        }
      }
    }
  }
</script>
