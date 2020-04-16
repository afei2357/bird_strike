<template>
  <maincontent 
      :tableConfig="tableConfig"
      :getRecord="getRecord" 
      :deleteRecord="delRecord"
      />
</template>
<script>
  import { getRecord, delRecord} from '@/api/updata'
  import maincontent from '../main'
  export default {
    components: {
      maincontent
    },
    methods: {
      getRecord,
      delRecord
    },
    data() {
      return {
        tableConfig: [
          {
            name: 'data_num',
            label: '数据编码',
            prop: 'data_num',
            width: '200px'
          },
          {
            name: 'sample_id',
            label: '样本编码',
            prop: 'sample_id'
          },
          {
            name: 'creation_time',
            label: '创建时间',
            prop: 'creation_time',
            width: '200px'
          },
          {
            name: 'update_time',
            label: '数据更新时间',
            prop: 'update_time',
            width: '200px'
          },
          {
            name: 'rs_num',
            label: '位点数目',
            prop: 'rs_num'

          }
        ]
      }
    }
  }

</script>