import request from '@/utils/request'
let  remote = 'http://47.100.178.254:7000'
//let remote = 'http://47.107.181.212:7000'

export function glistProduct() {
    return request({
      url: `${remote}/product/list_product`,
      method: 'get',
    })
  }

  export function getRecord(data) {
    return request({
      url: '/products',
      method: 'get',
      params: data 
    })
  }

  export function postUpdate(data) {
    return request({
      url: '/products',
      method: 'post',
      data
    })
  }
  