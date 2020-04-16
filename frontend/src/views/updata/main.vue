<template>
  <div class="app-container">
    <!--数据列表上方 开始-->
    <el-form  v-if="isrole">
    <upload-excel :on-success="handleSuccess" :before-upload="beforeUpload" />
  </el-form>
    <div class="filter-container">
      <el-input placeholder="数据编码" v-model="listQuery.data_num" style="width: 160px;" class="filter-item" @keyup.enter.native="handleFilter" />
      <el-input placeholder="样本编码" v-model="listQuery.sample_code" style="width: 160px;" class="filter-item" @keyup.enter.native="handleFilter" />
      <el-button class="filter-item" type="primary" icon="el-icon-search" @click="handleFilter">查询</el-button>
    </div>
    <!--数据列表上方 结束-->
    <!--数据列表表单 开始-->
    <Table :data="tableList" :tableKey="tableConfig" :listLoading="listLoading">
      <el-table-column label="操作" width="220" align="center"  v-if="isrole">
        <template slot-scope="scope">
          <el-button type="danger" size="small" @click="handleDel(scope.$index, scope.row)">删除</el-button>
          <el-button
          <el-button :disabled="!(scope.row.results2) || scope.row.flag =='noData' " type="primary" size="small"
            @click="downloadFile(scope.$index, scope.row, 'xlxs')">下载数据</el-button>
          <!--el-button :disabled="!(scope.row.web_results) || scope.row.flag =='noData' " type="primary" size="small" @click="goToReportView(scope.row)">查看报告</el-button-->
        </template>
      </el-table-column>
    </Table>
    <!--数据列表表单 结束-->
    <!--页码 开始-->
    <pagination v-show="total>0" :total="total" :page.sync="listQuery.page" :limit.sync="listQuery.page_size"
      @pagination="getList" />
    <!--页码 结束-->
  </div>
</template>
<script>
  import Pagination from '@/components/Pagination' // Secondary package based on el-pagination
  import Table from '@/components/Table/basic'
  import UploadExcel from '@/components/UploadExcel'
  import { postUpload } from '@/api/updata'
  import store from '@/store'
  import { getChannel } from '@/api/channel'

  export default {
    name: 'UpDataTable',
    components: {
      Pagination,
      Table,
      UploadExcel
    },
    props: {
      tableConfig: {
        type: Array
      },
      getRecord: {
        type: Function,
        default: null
      },
      deleteRecord: {
        type: Function,
        default: null
      }
    },
    provide() {
      return {
        InterpMainApp: this
      }
    },
    data() {
      return {
        tableList: null,
        total: 0,
        listLoading: true,
        listQuery: {
          page: 1,
          page_size: 10,
          sort: '+id',
          sample_code: undefined,
          data_num: undefined
        },
        tableData: [],
        isrole: false
      }
    },
    created() {
      this.getList()
    },
    mounted() {
      if(store.getters.roles.indexOf("超级管理员") > -1 || store.getters.roles.indexOf("项目管理") > -1){
        this.isrole = true
      }
    },
    methods: {
      beforeUpload(file) {
        const isLt1M = file.size / 1024 / 1024 < 1
        if (isLt1M) {
          return true
        } 
        this.$message({
          message: 'Please choose channel and do not upload files larger than 1m in size.',
          type: 'warning'
        })
        return false
      },
      async handleSuccess({
        results,
        header
      }) {
        this.tableData = results
        this.tableHeader = header
        let res = await postUpload(JSON.stringify({'header': this.tableHeader, 'data': this.tableData}))
        if (res.code == '200'){
          this.$message('数据上传存入成功')
        }
        this.getList(1)
      },
      getList() {
        this.listLoading = true
        this.getRecord(this.listQuery).then(response => {
          var infos = response.infos
          this.tableList = infos.items
          console.log(this.tableList)
          this.total = response.infos._meta.total_items
          console.log(this.tableList)
          this.listLoading = false
        })
      },
      handleFilter() {
      this.listQuery.page = 1
      this.getList()
      },
      async handleDel(index, row) {
        if (confirm('确定要删除吗？')) {
          const info = await this.deleteRecord(row.id)
          if (info.code === 200) {
            this.$message('订单:' + ';删除' + '成功')
          }
          this.getList(1)
        }
      }
    }
}

</script>
