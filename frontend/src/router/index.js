import Vue from 'vue'
import VueRouter from 'vue-router'
import locale from '../locale'
import Home from '@/views/Home.vue'
import Config from '@/views/Config.vue'
import Chat from '@/views/Chat.vue'
import ModelManager from '@/views/ModelManager.vue'
import NotFound from '@/views/NotFound.vue'

import dashboard from '~icons/humbleicons/dashboard'
import cog from '~icons/humbleicons/cog'
import downloadAlt from '~icons/humbleicons/download-alt'
import chats from '~icons/humbleicons/chats'

Vue.use(VueRouter)
export const routes = [
  {
    path: '/',
    basePath: '/',
    name: locale.dashboard,
    component: Home,
    icon: dashboard
    // NOTE: you can also lazy-load the component
    // component: () => import("@/views/About.vue")
  },
  {
    path: '/config',
    basePath: '/config',
    name: locale.configuration,
    component: Config,
    icon: cog
  },
  {
    path: '/models/:catType?/:subType?',
    props: true,
    basePath: '/models',
    name: locale.model_manager,
    component: ModelManager,
    icon: downloadAlt
  },
  {
    path: '/chat',
    basePath: '/chat',
    name: locale.chat,
    component: Chat,
    icon: chats
  },
  {
    _hide: true,
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
