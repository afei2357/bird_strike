<template>
  <!--el-form label-position="left" ref="Form" :model="Form" label-width="100px" style="width: 500px; margin-left:50px;"-->

  <el-form :model="Form" :rules="rules" ref="Form" label-width="100px" style="margin-right:30px;margin-right:30px">
    <form-generator
                   :config="config"
                   :value="Form"
                   />
  </el-form>
</template>
<script type="text/javascript">
import FormGenerator from '@/components/Form/FormGenerator'
import { getRoles } from '@/api/role'

export default {
  name: 'SubElForm',
  components: { FormGenerator },
  inject: ['InterpMainApp'], // 从Main.vue中获取数据
  data() {
    return {
      config: this.InterpMainApp.subConfig,
      Form: this.InterpMainApp.formData,
      rules: this.InterpMainApp.rules
    }
  },
  created() {
    this.querySearchType()
  },
  methods: {
    async queryRoles(queryString, callback) {
      var itemData = await getRoles()
      itemData = itemData.data.items
      var list=[]
      for (const i of itemData){
        list.push({ value: i.name, label: i.slug})
      }
      callback(list)
    },
    querySearchType() { // 函数一时没有找到方法直接转递，采用字符传递方式，再用方法替代。
      this.config.fieldsConfig.forEach((item, index) => {
        if (item.querySearch === 'getRolesinfo') {
          item.querySearch = this.queryRoles
        }
      })
    }
  }
}

</script>
