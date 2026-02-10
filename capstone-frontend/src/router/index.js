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

//Staff Components
import StaffLayout from "../views/Staff/StaffLayout.vue";
import StaffDashboard from "../views/Staff/StaffDashboard.vue";
import StaffLogs from "../views/Staff/StaffLogs.vue";

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
    meta: { requiresAuth: true, role: ['admin', 'staff'] },
    children: [
      { path: 'dashboard', name: 'Dashboard', component: Dashboard },
      { path: 'hazard_report', name: 'Hazard Reports', component: HazardReport},
      { path: 'analytics', name: 'Analytics', component: Analytics },
      { path: 'centers', name: 'EvacuationCenters', component: EvacuationCenters },
      { path: 'map', name: 'GISMap', component: GISMap },
      { path: 'users', name: 'UserMgmt', component: UserMgnt },
      { path: 'logs', name: 'Evacuation Logs', component: StaffLogs }
    ]
  },

  //STAFF ROUTES
  {
    path: "/staff",
    component: StaffLayout,
    meta: { requiresAuth: true, role: "staff" },
    children: [
      { path: "dashboard", name: "StaffDashboard", component: StaffDashboard },
      { path: "centers", name: "StaffCenters", component: EvacuationCenters },
      { path: "logs", name: "StaffLogs", component: StaffLogs },
      { path: "map", name: "StaffMap", component: GISMap },
    ],
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
  const userType = userData.userType // 'admin' | 'staff' | 'citizen'

  if (to.meta.requiresAuth && !isAuthenticated) {
    return next('/auth/login')
  }

  // prevent going back to login when already logged in
  if (to.path === "/auth/login" && isAuthenticated) {
    return next(
      userData.userType === "admin" ? "/admin/dashboard"
      : userData.userType === "staff" ? "/staff/dashboard"
      : "/user/dashboard"
    );
  }

  if (to.meta.requiresAuth && isAuthenticated) {
    const required = to.meta.role // string or array

    if (required) {
      const allowed = Array.isArray(required) ? required : [required]
      if (!allowed.includes(userType)) {
        return next(
          (userType === 'admin' || userType === 'staff') ? '/admin/dashboard' : '/user/dashboard'
        )
      }
    }
  }

  next()
})

export default router
