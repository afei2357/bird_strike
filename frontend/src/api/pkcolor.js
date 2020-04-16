import request from '@/utils/request'


export function postColor(mainName,data) {
  return request({
    url: `/pkcolor/${mainName}`,
    method: 'post',
    data
  })
}


export function getColor(mainName) {
  return request({
    url: `/pkcolor/${mainName}`,
    method: 'get'
  })
}
  