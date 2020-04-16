<template>
  <div class="app-container">
    <!--数据列表上方 开始-->
    <div class="filter-container">
            <!--新增-->
      <el-button class="filter-item" style="margin-left: 10px;" type="primary" icon="el-icon-edit" @click="handleCreate">新增</el-button>
    </div>
    <!--数据列表上方 结束-->

    <!--数据列表表单 开始-->
    <Table :data="tableList" :tableKey="tableConfig" :listLoading="listLoading">
      <el-table-column label="操作" width="220" align="center">
        <template slot-scope="scope">
          <el-button size="small" @click="handleUpdate(scope.$index, scope.row)">编辑</el-button>
        </template>
      </el-table-column>
    </Table>
    <!--数据列表表单 结束-->
    <!--页码 开始-->
    <pagination v-show="total>0" :total="total" :page.sync="listQuery.page" :limit.sync="listQuery.page_size"
      @pagination="getList" />
    <!--页码 结束-->
    
    <!--新增编辑表单 开始-->
    <addEditForm ref="addEditForm" :dialogStatus="dialogStatus" :dialogFormVisible="dialogVisible"  @getlist="getList()" @cancel="resetDialog()"></addEditForm>
    <!--新增编辑表单 结束-->


  </div>
</template>
<script>
  import Pagination from '@/components/Pagination' // Secondary package based on el-pagination
  import Table from '@/components/Table/basic'
  import addEditForm from './Form'
  import UploadExcel from '@/components/UploadExcel'
  import { postUpload } from '@/api/updata'

  export default {
    name: 'UpDataTable',
    components: {
      Pagination,
      Table,
      UploadExcel,
      addEditForm
    },
    props: {
      formData: {
        type: Object
      },
      subConfig: {
        type: Object
      },
      tableConfig: {
        type: Array
      },
      rules: {
        type: Object
      },
      createDataForm: {
        type: Function,
        default: null
      },
      updateDataForm: {
        type: Function,
        default: null
      },
      getRecord: {
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
          name: undefined
        },
        tableData: [],
        dialogVisible: false,
        dialogStatus: '',
        subFormInfo: this.formData
      }
    },
    created() {
      this.getList()
    },
    methods: {
      getList() {
        this.listLoading = true
        this.getRecord(this.listQuery).then(response => {
          var infos = response.infos
          this.tableList = infos.items
          this.total = response.infos._meta.total_items
          console.log(this.tableList)
          this.listLoading = false
        })
      },
      handleFilter() {
        this.listQuery.page = 1
        this.getList()
      },
      handleCreate() {
        this.dialogStatus = 'create'
        for (var name in this.subFormInfo) {
            this.subFormInfo[name] = ''
        }
        this.dialogVisible = true
      },
      handleUpdate(index, row) {
        this.dialogFormInfo = Object.assign({}, row) // copy obj
        for (var name in this.subFormInfo) {
          this.subFormInfo[name] = this.dialogFormInfo[name]
        }
        this.subFormInfo['id'] = this.dialogFormInfo['id']
        this.subFormInfo['role_name'] = this.dialogFormInfo['role_name']
        this.dialogStatus = 'update'
        this.dialogVisible = true
      },
      resetDialog() {
        this.dialogVisible = false // dialog关闭
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
