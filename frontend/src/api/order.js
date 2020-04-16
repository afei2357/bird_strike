import request from '@/utils/request'

export function getRecord(data) {
  return request({
    url: `/order`,
    method: 'get',
    params: data 
  })
}

export function postCreate(data) {
  return request({
    url: `/order`,
    method: 'post',
    data
  })
}

export function putUpdate(id, data) {
  return request({
    url: `/order/${id}`,
    method: 'put',
    data 
  })
}

export function delRecord(id) {
  return request({
    url: `/order/${id}`,
    method: 'delete',
  })
}

export function postRunRpt(id) {
  return request({
    url: `/order/run/${id}`,
    method: 'post'
  })
}

export function getDownFile(id, flag) {
  return request({
    url: `/order/download/${id}/${flag}`,
    method: 'get',
  })
}

export function glistProduct() {
  return request({
    url: `/order/products`,
    method: 'get'
  })
}

export function getTaskStat(id, task_id) {
  return request({
    url: `/order/run/${id}/${task_id}`,
    method: 'put'
  })
}
