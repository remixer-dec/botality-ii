import Vue from 'vue'
import VueRouter from 'vue-router'
import Home from '@/views/Home.vue'
import Config from '@/views/Config.vue'
import NotFound from '@/views/NotFound.vue'

Vue.use(VueRouter)

export const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: Home
    // NOTE: you can also lazy-load the component
    // component: () => import("@/views/About.vue")
  },
  {
    path: '/config',
    name: 'Configuration',
    component: Config
  },
  {
    path: '/:path(.*)',
    name: 'NotFound',
    component: NotFound
  }
]

const router = new VueRouter({
  base: '/',
  mode: 'history',
  routes
})

export default router
