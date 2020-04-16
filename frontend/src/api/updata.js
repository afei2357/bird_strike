import request from '@/utils/request'

export function getRecord(data) {
  return request({
    url: '/updata',
    method: 'get',
    params: data 
  })
}

export function postUpload(data) {
  return request({
    url: '/updata',
    method: 'post',
    data
  })
}

export function delRecord(id) {
  return request({
    url: `/updata/${id}`,
    method: 'delete',
  })
}
