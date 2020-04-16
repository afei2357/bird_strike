<template>
  <el-table v-loading="listLoading" :data="data" border fit highlight-current-row style="width: 100%;">
    <el-table-column
           v-for="item in tableKey"
           :key="item.name"
           :label="item.label"
           :prop="item.prop"
           :width="item.width || '120px'"
           :align="item.align || 'center'"
           >
      <template slot-scope="scope">
        <span>{{ scope.row[item.name] }}</span>
      </template>
    </el-table-column>
     <slot> </slot>
  </el-table>
</template>
<script type="text/javascript">
export default {
  name: 'Table',
  props: ['data', 'tableKey', 'listLoading']
}
</script>

 <style >
  /*实现表格头数据换行*/
  .el-table .cell {
      text-align: center;
      white-space: pre-wrap;/*保留换行符*/
  }
 </style>
