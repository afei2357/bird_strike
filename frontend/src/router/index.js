import Vue from 'vue'
import Router from 'vue-router'

Vue.use(Router)

/* Layout */
import Layout from '@/layout'

/**
 * Note: sub-menu only appear when route children.length >= 1
 * Detail see: https://panjiachen.github.io/vue-element-admin-site/guide/essentials/router-and-nav.html
 *
 * hidden: true                   if set true, item will not show in the sidebar(default is false)
 * alwaysShow: true               if set true, will always show the root menu
 *                                if not set alwaysShow, when item has more than one children route,
 *                                it will becomes nested mode, otherwise not show the root menu
 * redirect: noRedirect           if set noRedirect will no redirect in the breadcrumb
 * name:'router-name'             the name is used by <keep-alive> (must set!!!)
 * meta : {
    roles: ['admin','editor']    control the page roles (you can set multiple roles)
    title: 'title'               the name show in sidebar and breadcrumb (recommend set)
    icon: 'svg-name'             the icon show in the sidebar
    breadcrumb: false            if set false, the item will hidden in breadcrumb(default is true)
    activeMenu: '/example/list'  if set path, the sidebar will highlight the path you set
  }
 */

/**
 * constantRoutes
 * a base page that does not have permission requirements
 * all roles can be accessed
 */
export const constantRoutes = [
  {
    path: '/login',
    component: () => import('@/views/auth/login'),
    hidden: true
  },
  {
    path: '/register',
    component: () => import('@/views/auth/register'),
    hidden: true
  },
  {
    path: '/unconfirmed',
    component: () => import('@/views/auth/Unconfirmed'),
    hidden: true
  },
/*  {
    path: '/resetpasswd',
    component: () => import('@/views/auth/resetpasswd'),
    hidden: true
  },*/
  {
    path: '/404',
    component: () => import('@/views/404'),
    hidden: true
  },
  {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    children: [{
      path: 'dashboard',
      name: 'Dashboard',
      component: () => import('@/views/dashboard/index'),
      meta: { title: '仪表盘', icon: 'dashboard' }
    }]
  },
  {
    path: '/order',
    component: Layout,
    redirect: '/order/health',
    name: '订单中心',
    meta: { title: '订单中心', icon: '订单' },
    children: [
      {
        path: 'medicine',
        name: 'Medicines',
        component: () => import('@/views/order/Medicine/index'),
        meta: { title: '订单中心', icon: 'table' }
      }
    ]
  },
  {
    path: '/updata',
    component: Layout,
    redirect: '/updata/medicine',
    name: '数据中心',
    meta: { title: '数据中心', icon: 'form' },
    children: [
      {
        path: 'snps',
        name: 'Snps',
        component: () => import('@/views/updata/Medicine/index'),
        meta: { title: '数据中心', icon: 'table' }
      }
    ]
  }
]

export const asyncRoutes = [
  {
    path: '/users',
    component: Layout,
    redirect: '/users',
    name: 'Users',
    children: [{
      path: '/users',
      name: 'Users',
      component: () => import('@/views/users/index'),
      meta: {
        title: '用户管理',
        icon: '用户',
        roles: ['渠道管理员', '超级管理员'] // you can set roles in root nav
      }
    }]
  },

  // 404 page must be placed at the end !!!
  { path: '*', redirect: '/404', hidden: true }
]

const createRouter = () => new Router({
  // mode: 'history', // require service support
  scrollBehavior: () => ({ y: 0 }),
  routes: constantRoutes
})

const router = createRouter()

// Detail see: https://github.com/vuejs/vue-router/issues/1234#issuecomment-357941465
export function resetRouter() {
  const newRouter = createRouter()
  router.matcher = newRouter.matcher // reset router
}

export default router
