import request from '@/utils/request'

export function uploadImageFiles(mainName, data) {
    return request({
      url: `/upcover/${mainName}`,
      method: 'post',
      data
    })
  }

  export function getImageFiles(mainName) {
    return request({
      url: `/upcover/${mainName}`,
      method: 'get'
    })
  }


  export function deleteImageReport(id) {
    return request({
      url: `/upcover/${id}`,
      method: 'delete'
    })
  }
  