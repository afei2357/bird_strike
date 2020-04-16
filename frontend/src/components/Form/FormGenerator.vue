<template>
  <div>
    <el-col v-for="(field, index) in config.fieldsConfig" :key="index">
      <component
      :key="index"
                  :is="field.fieldType"
                  :label="field.label"
                  :prop="field.prop"
                  :placeholder="field.placeholder"
                  :value="formData[field.name]"
                  :multiple="field.multiple"
                  :itemData="itemData"
                  @input="updateForm"
                  v-bind="field"
                  :options="field.options"
                  :ref="field.name"
                  :trigerFocus="field.trigerFocus"
                  :autosize="field.autosize"
      >
      </component>
    </el-col>
  </div>
</template>
<script>
import autoComplete from './basic/autoComplete'
import TextInput from './basic/TextInput'
import NumInput from './basic/NumInput'
import SelectList from './basic/SelectList'
import multiSelectList from './basic/multiSelectList'
import CasCader from './basic/cascader.vue'
import Radio from './basic/Radio.vue'
import DatePicker from './basic/DatePicker.vue'
export default {
  name: 'FormGenerator',
  components: { autoComplete, TextInput, SelectList, multiSelectList, NumInput, CasCader, Radio, DatePicker },
  props: ['config', 'value', 'itemData'],
  data() {
    return {
      formData: this.value
    }
  },
  watch: {
    value(val) {
      this.formData = val
    }
  },
  methods: {
    updateForm(fieldName, value) {
      this.formData[fieldName] = value
    },
    submit() {
      this.$emit('submit')
    },
    reset() {
      for (var name in this.formData) {
        if (typeof (this.formData) === String) {
          this.formData[name] = ''
        } else {
          this.formData[name] = null
        }
      }
    }
  }
}
</script>
