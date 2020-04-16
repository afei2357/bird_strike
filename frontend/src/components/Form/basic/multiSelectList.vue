<template>
  <el-form-item :label="label" :prop="prop">
    <el-select
            v-model="currentValue"
            @input="onInputEvent"
            multiple
            filterable
            remote
            :remote-method="querySearch"
            :placeholder="placeholder">
      <el-option
        v-for="item in options"
        :key="item.value"
        :label="item.label"
        :value="item.value">
      </el-option>
    </el-select>
  </el-form-item>
</template>

<script>
import formMixins from '@/mixins/form-model'
export default {
  name: 'MulSelectList',
  props: ['placeholder', 'itemData', 'prop', 'label', 'value', 'querySearch'],
  data() {
    return {
      currentValue: this.value,
      options: []
    }
  },
  mounted(){
    this.options = this.itemData
  },
  watch: {
    itemData(val) {
      this.options = val
    }
  },
  mixins: [formMixins]
}
</script>
