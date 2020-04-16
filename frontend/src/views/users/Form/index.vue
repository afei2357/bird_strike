<template>
  <!--新增编辑表单 开始-->
  <el-dialog :title="textMap[dialogStatus]" :visible.sync="dialogVisible" @close="onCancel" customClass="customWidth">
   <!--添加基本信息开始-->
    <sub-el-form
                ref="subelform">
    </sub-el-form>
    <!--添加基本信息结束-->

    <div slot="footer" class="dialog-footer">
      <el-button @click="onCancel">关闭</el-button>
      <el-button type="primary" @click="dialogStatus==='create'?createData():updateData()">确认</el-button>
    </div>
  </el-dialog>
  <!--新增编辑表单 结束-->
</template>
<script type="text/javascript">
import SubElForm from './subElForm.vue'
import store from '@/store'
export default {
  components: { SubElForm },
  inject: ['InterpMainApp'],
  data() {
    return {
      mainName: this.InterpMainApp.mainName,
      textMap: {
        update: '编辑',
        create: '新建'
      },
      dialogVisible: this.dialogFormVisible
    }
  },
  props: {
    dialogStatus: {
      type: String
    },
    dialogFormVisible: {
      type: Boolean,
      default: false
    },
    conclustionEditForm: { // 结论表单
      type: Array
    }
  },
  watch: {
    dialogFormVisible(val) {
      this.dialogVisible = val
    }
  },
  methods: {
    onCancel() {
      this.$emit('cancel')
    },
    resetData(Form) {
      // 重置表单中的值
      for (var name in Form) {
        if (typeof (Form) === String) {
          Form[name] = ''
        } else {
          Form[name] = null
        }
      }
    },
    createData() {
      this.$refs.subelform.$refs.Form.validate(valid => {
        console.log(this.$refs.subelform.$refs.Form)
        if (valid) {
          var tempData = Object.assign({}, this.InterpMainApp.subFormInfo) // subelform从获取数据, 中赋值到data
          tempData['token'] = store.getters.token
          tempData['confirm_email_base_url'] = window.location.href.split("/", 4).join("/") + "/unconfirmed/?token=",
          console.log(JSON.stringify(tempData))

          this.InterpMainApp.createDataForm(JSON.stringify(tempData)).then(() => {
            this.$emit('getlist')
            this.$emit('cancel') // 调用父组件的cancer方法
            this.$notify({
              title: '成功',
              message: '创建成功,请及时验证邮箱',
              type: 'success',
              duration: 1000
            })
          })
        }
      })
    },
    updateData() {
      this.$refs.subelform.$refs.Form.validate(valid => {
        console.log(this.$refs.subelform.$refs.Form)
        if (valid) {
                var tempData = Object.assign({}, this.InterpMainApp.subFormInfo) // 从main中的InterpMainApp获取 表单数据
      this.InterpMainApp.updateDataForm(tempData.id, JSON.stringify(tempData)).then(() => {
          this.$emit('getlist')
          this.$emit('cancel') // 调用父组件的cancer方法
          this.$notify({
            title: '成功',
            message: '创建成功',
            type: 'success',
            duration: 1000
          })
        })

        }
      })
    }
  }
}
</script>
<style>
.customWidth {
  width: 40%;
}

</style>
