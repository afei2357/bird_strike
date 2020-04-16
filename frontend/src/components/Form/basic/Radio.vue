<template>
  <el-form-item :label="label" :prop="prop">
    <el-radio-group v-model="currentValue" @input="onInputEvent">
    <el-radio
        v-for="item in options"
        :key="item.value"
        :label="item.label"
        >
      </el-radio>

    </el-radio-group>
  </el-form-item>
</template>

<script>
import formMixins from '@/mixins/form-model'
export default {
  name: 'Radio',
  props: ['options', 'prop', 'label', 'value'],
  data() {
    return {
      currentValue: this.value
    }
  },
  mixins: [formMixins]
}
</script>
<style scoped>
.el-form-item {margin-bottom: 1px;} 
</style>