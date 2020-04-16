import request from '@/utils/request'

export function login(data) {
  return request({
    url: '/login',
    method: 'post',
    data
  })
}

export function logout() {
  return request({
    url: '/user/logout',
    method: 'post'
  })
}

export function getUser(id) {
  return request({
    url: `/users/${id}`,
    method: 'get'
  })
}

export function getInfo(data) {
  return request({
    url: '/user/info',
    method: 'get',
    params: data
  })
}

export function postUsers(data) {
  return request({
    url: '/users',
    method: 'post',
    data
  })
}

export function putUsers(id,data) {
  return request({
    url: `/users/${id}`,
    method: 'put',
    data
  })
}

export function getRecord(data) {
  return request({
    url: '/users',
    method: 'get',
    params: data 
  })
}


export function getConfirm(token) {
  return request({
    url: `confirm/${token}`,
    method: 'get',
  })
}

export function resendConfirm(data) {
  return request({
    url: `/resend-confirm`,
    method: 'post',
    data
  })
}
