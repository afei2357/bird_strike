<template>
<el-form-item :label="label" :prop="prop">
  <div>
    <el-date-picker 
                   v-model="currentValue" 
                   type="date"
                   placeholder="选择日期"
                   :picker-options="pickerOptions"
                   format="yyyy 年 MM 月 dd 日"
                   value-format="yyyy-MM-dd"
                   @input="onInputEvent">
    </el-date-picker>
  </div>
</el-form-item>
</template>
<script>
  import formMixins from '@/mixins/form-model'
  export default {
    name: 'Radio',
    props: ['options', 'prop', 'label', 'value'],
    data() {
      return {
        currentValue: this.value,
        pickerOptions: {
          disabledDate(time) {
            return time.getTime() > Date.now();
          },
          shortcuts: [{
            text: '今天',
            onClick(picker) {
              picker.$emit('pick', new Date());
            }
          }, {
            text: '昨天',
            onClick(picker) {
              const date = new Date();
              date.setTime(date.getTime() - 3600 * 1000 * 24);
              picker.$emit('pick', date);
            }
          }, {
            text: '一周前',
            onClick(picker) {
              const date = new Date();
              date.setTime(date.getTime() - 3600 * 1000 * 24 * 7);
              picker.$emit('pick', date);
            }
          }]
        }
      }
    },
    mixins: [formMixins]
  }

</script>
