<template>
  <el-form-item :prop="prop" :label="label">
    <el-input
             type="text"
             :name="name"
             v-model="currentValue"
             :placeholder="placeholder"
             @input="onInputEvent"
             >
    </el-input>
  </el-form-item>
</template>
<script>
import formMixins from '@/mixins/form-model'
export default {
  name: 'TextInput',
  props: ['placeholder', 'label', 'prop', 'name', 'value', 'rules'],
  mixins: [formMixins],
  data() {
    return {
      currentValue: this.value
    }
  }
}
</script>
<style scoped>
</style>
