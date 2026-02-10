import { createRouter, createWebHistory } from 'vue-router'

// Admin Components
import AdminLayout from '../views/AdminLayout.vue'
import Dashboard from '../views/Dashboard.vue'
import Analytics from '../views/Analytics.vue'
import EvacuationCenters from '../views/EvacuationCenters.vue'
import GISMap from '../views/GISMap.vue'
import UserMgnt from '../views/Users/UserMgnt.vue'
import HazardReport from '../views/HazardReport.vue'

// User Components
import UserLayout from '../views/Users/UserLayout.vue'
import UserLogin from '@/views/Users/UserLogin.vue'
import UserRegister from '../views/Users/UserRegister.vue'
import UserDashboard from '../views/Users/UserDashboard.vue'
import UserHazardReport from '../views/Users/UserHazardReport.vue'
import UserMap from '../views/Users/UserMap.vue'
import UserAlerts from '../views/Users/UserAlerts.vue'
import UserProfile from '../views/Users/UserProfile.vue'

const routes = [
  {
    path: '/',
    redirect: '/auth/login'
  },

  // USER ROUTES
  {
    path: '/auth/login',
    name: 'UserLogin',
    component: UserLogin
  },
  {
    path: '/auth/register',
    name: 'UserRegister',
    component: UserRegister
  },
  {
    path: '/user',
    component: UserLayout,
    meta: { requiresAuth: true, role: 'citizen' },
    children: [
      { path: 'dashboard', name: 'UserDashboard', component: UserDashboard },
      { path: 'report', name: 'UserHazardReport', component: UserHazardReport },
      { path: 'map', name: 'UserMap', component: UserMap },
      { path: 'alerts', name: 'UserAlerts', component: UserAlerts },
      { path: 'profile', name: 'UserProfile', component: UserProfile }
    ]
  },

  // ADMIN ROUTES
  {
    path: '/admin',
    component: AdminLayout,
    meta: { requiresAuth: true, role: 'admin' },
    children: [
      { path: 'dashboard', name: 'Dashboard', component: Dashboard },
      { path: 'hazard_report', name: 'Hazard Reports', component: HazardReport},
      { path: 'analytics', name: 'Analytics', component: Analytics },
      { path: 'centers', name: 'EvacuationCenters', component: EvacuationCenters },
      { path: 'map', name: 'GISMap', component: GISMap },
      { path: 'users', name: 'UserMgmt', component: UserMgnt }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// AUTH + ROLE GUARD
router.beforeEach((to, from, next) => {
  const isAuthenticated = localStorage.getItem('isAuthenticated') === 'true'
  const userData = JSON.parse(localStorage.getItem('userData') || '{}')

  // Requires login
  if (to.meta.requiresAuth && !isAuthenticated) {
    return next('/auth/login')
  }

  // Already logged in → prevent entering login page
  if (to.path === '/auth/login' && isAuthenticated) {
    return next(userData.role === 'admin' ? '/admin/dashboard' : '/user/dashboard')
  }

  // Role protection
  if (to.meta.requiresAuth && isAuthenticated) {
    const userRole = userData.role
    const requiredRole = to.meta.role

    if (requiredRole && userRole !== requiredRole) {
  const fallback = userRole === 'admin' ? '/admin/dashboard' : '/user/dashboard'
  if (to.path !== fallback) return next(fallback)
  return next()
}
  }

  next()
})

export default router
