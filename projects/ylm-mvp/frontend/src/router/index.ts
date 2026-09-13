import { createRouter, createWebHashHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'home',
    component: HomeView
  },
  {
    path: '/exercises',
    name: 'exercises',
    component: () => import('../views/ExerciseListView.vue')
  },
  {
    path: '/exercises/:id/practice',
    name: 'practice',
    component: () => import('../views/PracticeView.vue')
  },
  {
    path: '/submissions/:id/report',
    name: 'report',
    component: () => import('../views/ReportView.vue')
  },
  {
    path: '/history',
    name: 'history',
    component: () => import('../views/HistoryView.vue')
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

export default router
