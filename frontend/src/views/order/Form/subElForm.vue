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
import transQueryList from '@/utils/utils'
import { glistProduct } from '@/api/order'
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
    async queryProducts(queryString, callback) {
      var itemData = await glistProduct()
      console.log(itemData)
      itemData = itemData.infos
      var list = []
      for (var i in itemData){
        list.push({value:itemData[i], label:i})
      }
      // const list = transQueryList(queryString, itemData)
      console.log(list)
      callback(list)
    },
    querySearchType() { // 函数一时没有找到方法直接转递，采用字符传递方式，再用方法替代。
      this.config.fieldsConfig.forEach((item, index) => {
        if (item.querySearch === 'ghealthProduct') {
          item.querySearch = this.queryProducts
        }
      })
    }
  }
}

</script>
