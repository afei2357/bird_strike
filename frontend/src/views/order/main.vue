<template>
  <div class="app-container">
    <!--数据列表上方 开始-->
    <upload-excel :on-success="handleSuccess" :before-upload="beforeUpload" />
    <div class="filter-container">
      <!--搜索-->
      <el-input placeholder="订单号" v-model="listQuery.order_num" style="width: 160px;" class="filter-item" @keyup.enter.native="handleFilter" />
      <el-input placeholder="姓名" v-model="listQuery.name" style="width: 160px;" class="filter-item" @keyup.enter.native="handleFilter" />
      <el-input placeholder="样本编号" v-model="listQuery.sample_code" style="width: 160px;" class="filter-item" @keyup.enter.native="handleFilter" />
      <el-input placeholder="订单状态" v-model="listQuery.orderstate" style="width: 160px;" class="filter-item" @keyup.enter.native="handleFilter" />
      <!--el-select v-model="listQuery.sort" style="width: 140px" class="filter-item" @change="handleFilter">
        <el-option v-for="item in sortOptions" :key="item.key" :label="item.label" :value="item.key" /-->
      </el-select>
      <el-button class="filter-item" type="primary" icon="el-icon-search" @click="handleFilter">查询</el-button>
      <!--新增-->
      <el-button class="filter-item" style="margin-left: 10px;" type="primary" icon="el-icon-edit" @click="handleCreate">新增</el-button>
    </div>
    <!--数据列表上方 结束-->
    <!--数据列表表单 开始-->
    <Table :data="tableList" :tableKey="tableConfig" :listLoading="listLoading">
       <el-table-column label="订单状态" width="120" align="center">
         <template slot-scope="scope">
           <el-button size="small" :type="miStatusColor(scope.row.orderstate)">{{scope.row.orderstate}}</el-button>
         </template>
      </el-table-column>
      
      <el-table-column label="操作" width="240" align="center">
          <template slot-scope="scope">
            <el-button size="mini" @click="handleUpdate(scope.$index, scope.row)">编辑</el-button>
            <el-button type="danger" size="mini" @click="handleDel(scope.$index, scope.row)">删除</el-button>
            <el-button v-if="!scope.row.receive_date && isrole" size="mini" type="primary" @click="handleReceiveStatus(scope.row)">确认收样
            </el-button>
            <el-button
              :disabled="!(scope.row.updata_id) || scope.row.jobstate === 'PENDING' || scope.row.jobstate === 'RUNNING'"
              type="primary" size="mini" @click="jobrun(scope.$index, scope.row)">生成报告</el-button>
            <el-button v-if="isrole" :disabled="!(scope.row.docx_path) || scope.row.jobstate !== 'SUCCESS' " type="success" size="mini"
              @click="downloadFile(scope.$index, scope.row, 'docx')">下载docx</el-button>
            <el-button :disabled="!(scope.row.pdf_path) || scope.row.jobstate !== 'SUCCESS' " type="success" size="mini"
              @click="downloadFile(scope.$index, scope.row, 'pdf')">下载PDF</el-button>
            <el-button  v-if="scope.row.jobstate === 'PENDING' || scope.row.jobstate === 'RUNNING'" type="info" size="mini" >{{scope.row.jobstate}}</el-button>
            <el-button  v-if="scope.row.jobstate === 'FAIL'" type="danger" size="mini" >{{scope.row.jobstate}}</el-button>
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
  import addEditForm from './Form'
  import Table from '@/components/Table/basic'
  import store from '@/store'
  import UploadExcel from '@/components/UploadExcel'
  import { postRunRpt, getDownFile, getTaskStat } from '@/api/order'

  export default {
    name: 'OrderTable',
    components: {
      Pagination,
      Table,
      addEditForm,
      UploadExcel
    },
    props: {
      tableConfig: {
        type: Array
      },
      formData: {
        type: Object
      },
      subConfig: {
        type: Object
      },
      rules: {
        type: Object
      },
      getRecord: {
        type: Function,
        default: null
      },
      createDataForm: {
        type: Function,
        default: null
      },
      updateDataForm: {
        type: Function,
        default: null
      },
      deleteRecord: {
        type:Function,
        default: null
      },
      getProducts: {
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
          name: undefined,
          order_num: undefined,
          channel_name: undefined,
          orderstate: undefined
        },
        sortOptions: [{ label: 'ID Ascending', key: '+id' }, { label: 'ID Descending', key: '-id' }],
        subFormInfo: this.formData,
        dialogVisible: false,
        dialogStatus: '',
        isstate: '',
        isrole: false,
        miStatusColor: function(val){
            if(val == '未到样'){
                return 'info'
            }else if(val == '检测中'){
                return 'primary'
            }else if(val == '解读中'){
                return 'warning'
            }else if(val == '报告完成'){
                return 'success'
            }else if(val == '报告失败'){
                return 'danger'
            }else {
                return 'info'
            }
        }
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
          message: 'Please do not upload files larger than 1m in size.',
          type: 'warning'
        })
        return false
      },
      async handleSuccess({
        results,
        header
      }) {
        this.tableData = results
        console.log(this.tableData)
        this.tableHeader = header
        for (var i in this.tableData){
          if (this.tableData[i]['birthday']){
            this.tableData[i]['birthday'] = this.formatDate(this.tableData[i]['birthday'])
          }
          if (this.tableData[i]['receive_date']){
            this.tableData[i]['receive_date'] = this.formatDate(this.tableData[i]['receive_date'])
          }
          await this.createDataForm(JSON.stringify(this.tableData[i])).then(() => {
            this.$notify({
            title: '成功',
            message: '创建成功',
            type: 'success',
            duration: 1000
          })
          this.getList(1)
        })
        }
      },
      handleReceiveStatus(row) {
        console.log(row)
        var data_form = {}
        data_form['receive_date'] = new Date()
        console.log(data_form)
        this.updateDataForm(row.id, JSON.stringify(data_form)).then(() => {
            this.$notify({
            message: '确认到样成功',
            type: 'success',
            duration: 1000
          })
          this.getList(1)      
        })
      },
      resetDialog() {
        this.dialogVisible = false // dialog关闭
        // this.$refs.addEditForm.resetTable() // 调用Form中的重置数据 ，重置table可编辑表单
        // this.subFormInfo = this.formData // 调用index传递过来的formData 重置表单
        // this.getList()
      },
      getList() {
        this.listLoading = true
        this.getRecord(this.listQuery).then(response => {
          var infos = response.infos
          this.tableList = infos.items
          console.log(this.tableList)
          this.total = response.infos._meta.total_items
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
        this.subFormInfo.id = this.dialogFormInfo.id
        this.dialogStatus = 'update'
        this.dialogVisible = true
      },
      formatDate(date){
        // 年月日格式化 
        var seperator1 = "-"
        var month = date.getMonth() + 1;
        var strDate = date.getDate()
        if (month >= 1 && month <= 9) {
            month = "0" + month
        }
        if (strDate >= 0 && strDate <= 9) {
            strDate = "0" + strDate
        }
        var formatdate = date.getFullYear() + seperator1 + month + seperator1 + strDate
        return formatdate
      },
     //时间
    getNowFormatDate: function(){
        var date = new Date()
        var currentdate = this.formatDate(date)
        var seperator2 = ":"
        var currentdate = currentdate +
            ":" + date.getHours() + seperator2 + date.getMinutes() +
            seperator2 + date.getSeconds()
        return currentdate
    },
      //下载
      downloadFile(index, row, resflag) {
          this.$confirm("确定要要下载该文件吗？", "提示", {
                  type: "warning"
              })
              .then(() => {
                  getDownFile(row.id, resflag).then(res => {
                      if (res.code !== 200) {
                          this.$message({
                              message: res.msg,
                              type: "warning"
                          });
                      } else {
                          this.$message({
                              message: res.msg,
                              type: "success"
                          });
                          const link = document.createElement('a')
                          link.href = res.url
                          var suffix = res.url.split('/').pop()
                          var suffix = suffix.split('.').pop()
                          var currentdate = this.getNowFormatDate()
                          link.setAttribute('download', row.name + '_' + row.sample_code + '_' +
                              row.detection_items + '_' + currentdate + '.' + suffix)
                          document.body.appendChild(link)
                          console.log(link)
                          link.click()
                      }
                  })
              })
      },
      async handleDel(index, row) {
        if (confirm('确定要删除吗？')) {
          const info = await this.deleteRecord(row.id)
          if (info.code === 200) {
            this.$message('订单:' + ';删除' + '成功')
          }
          this.getList(1)
        }
      },
      jobstat(index, row, task_id){
        getTaskStat(row.id, task_id).then(response=>{
          let {code, msg} = response;
          row.jobstate = msg
          if (msg === 'PENDING' || msg === 'RUNNING'){
            
            setTimeout(()=>{
              this.jobstat(index, row, task_id)
              },4000)
          }else{
            this.$message({
                message: task_id + ':' + msg,
                type: "success"
            });
            this.getList(1)
            return
          }
        })
      },
      jobrun(index, row) {
            this.$confirm("确认生成该报告吗?", "提示", {
                    type: "warning" 
                })
                .then(() => { 
                    postRunRpt(row.id).then(res => {
                      let { msg, code,task_id } = res;
                      this.$message({
                          message: msg,
                          type: "success"
                      });
                      this.jobstat(index, row, task_id)
                    });
                })
                .catch(() => {});
        },
      }
  }

</script>
