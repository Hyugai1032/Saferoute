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
      { path: "", redirect: "/user/dashboard" },
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
    meta: { requiresAuth: true, role: ['admin'] },
    children: [
      { path: "", redirect: "/admin/dashboard" },
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
      { path: "", redirect: "/staff/dashboard" }, 
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
  const isAuthenticated = localStorage.getItem("isAuthenticated") === "true";
  const userData = JSON.parse(localStorage.getItem("userData") || "{}");
  const userType = userData.userType || "citizen"; // default

  const isAuthRoute = to.path.startsWith("/auth/");
  const needsAuth = to.matched.some(r => r.meta?.requiresAuth); // handles children properly

  // 1) if route needs auth but not logged in -> login
  if (needsAuth && !isAuthenticated) {
    return next("/auth/login");
  }

  // 2) if already logged in and trying to go auth pages -> redirect to proper dashboard
  if (isAuthenticated && isAuthRoute) {
    const target =
      userType === "admin" ? "/admin/dashboard"
      : userType === "staff" ? "/staff/dashboard"
      : "/user/dashboard";

    // prevent redirect loop
    if (to.path !== target) return next(target);
    return next();
  }

  // 3) role-based restriction (only when logged in)
  const requiredRole = to.meta?.role;
  if (isAuthenticated && requiredRole) {
    const allowed = Array.isArray(requiredRole) ? requiredRole : [requiredRole];
    if (!allowed.includes(userType)) {
      const fallback =
        (userType === "admin" || userType === "staff") ? "/admin/dashboard" : "/user/dashboard";

      if (to.path !== fallback) return next(fallback);
      return next(); // ✅ add this
    }
  }

  return next();
});

export default router
