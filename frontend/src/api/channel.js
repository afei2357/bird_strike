import request from '@/utils/request'

export function getRecord(data) {
  return request({
    url: '/channel',
    method: 'get',
    params: data 
  })
}

export function getChannel(data) {
  return request({
    url: '/channel',
    method: 'get',
    params: data 
  })
}


export function postCreate(data) {
  return request({
    url: '/channel',
    method: 'post',
    data
  })
}

export function putUpdate(id, data) {
  return request({
    url: `/channel/${id}`,
    method: 'put',
    data 
  })
}

export function delRecord(id) {
  return request({
    url: `/channel/${id}`,
    method: 'delete',
  })
}
