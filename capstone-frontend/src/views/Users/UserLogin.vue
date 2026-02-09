<!-- src/views/Users/UserLogin.vue -->
<template>
  <div class="auth-layout">
    <div class="login-container">
      <div class="login-card">
        <!-- Animated Background -->
        <div class="animated-bg">
          <div class="floating-shape shape-1"></div>
          <div class="floating-shape shape-2"></div>
          <div class="floating-shape shape-3"></div>
        </div>

        <!-- Left Section -->
        <div class="login-left">
          <div class="logo-section">
            <div class="logo-icon">
              <i class="fas fa-shield-alt"></i>
            </div>
            <h1 class="logo-title">Disaster Response Portal</h1>
            <p class="logo-subtitle">Stay safe, stay informed</p>
          </div>

          <div class="features-grid">
            <div class="feature-item" v-for="feature in features" :key="feature.id">
              <div class="feature-icon" :class="feature.color">
                <i :class="feature.icon"></i>
              </div>
              <div class="feature-content">
                <h3>{{ feature.title }}</h3>
                <p>{{ feature.description }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Right Section -->
        <div class="login-right">
          <div class="login-form">
            <h2 class="form-title">Welcome Back</h2>
            <p class="form-subtitle">Sign in to access your account</p>

            <form @submit.prevent="handleLogin">
              <div class="form-group">
                <label class="form-label">Email</label>
                <div class="input-group">
                  <i class="fas fa-user input-icon"></i>
                  <input 
                    type="email" 
                    class="form-input" 
                    placeholder="Enter your email"
                    v-model="credentials.email"
                    required
                  >
                </div>
              </div>

              <div class="form-group">
                <label class="form-label">Password</label>
                <div class="input-group">
                  <i class="fas fa-lock input-icon"></i>
                  <input 
                    :type="showPassword ? 'text' : 'password'"
                    class="form-input" 
                    placeholder="Enter your password"
                    v-model="credentials.password"
                    required
                  >
                  <button type="button" class="password-toggle" @click="togglePasswordVisibility">
                    <i :class="showPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
                  </button>
                </div>
              </div>

              <div class="form-options">
                <label class="checkbox-label">
                  <input type="checkbox" v-model="credentials.remember">
                  <span class="checkmark"></span>
                  Remember me
                </label>
                <a href="#" class="forgot-password">Forgot password?</a>
              </div>

              <button class="login-btn" type="submit" :disabled="loading">
                <span v-if="!loading">
                  <i class="fas fa-sign-in-alt"></i>
                  Sign In
                </span>
                <span v-else>
                  <i class="fas fa-spinner fa-spin"></i>
                  Signing In...
                </span>
              </button>

              <div style="text-align: center;">
                <p>Don't have an account? 
                  <router-link :to="{ name: 'UserRegister' }" class="forgot-password">
                      Register
                  </router-link>
                </p>
              </div>

              <div class="divider">
                <span>or continue with</span>
              </div>

              <div class="social-login">
                <button type="button" class="social-btn google">
                  <i class="fab fa-google"></i>
                  Google
                </button>
                <button type="button" class="social-btn microsoft">
                  <i class="fab fa-microsoft"></i>
                  Microsoft
                </button>
              </div>

              <p class="terms">
                By continuing, you agree to our 
                <a href="#" class="terms-link">Terms of Service</a> and 
                <a href="#" class="terms-link">Privacy Policy</a>
              </p>
            </form>
          </div>

          <!-- Demo Accounts Section -->
          <div class="demo-accounts">
            <h4>Quick Test Accounts</h4>
            <div class="demo-buttons">
              <button class="demo-btn user" @click="fillDemo('user')">
                <i class="fas fa-user"></i>
                User Account
              </button>
              <button class="demo-btn admin" @click="fillDemo('admin')">
                <i class="fas fa-cog"></i>
                Admin Account
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>

import { login, getUserProfile } from '../../services/authService';

</script>

<script>
export default {
  name: 'UserLogin',
  data() {
    return {
      credentials: {
        email: '',
        password: '',
        remember: false
      },
      showPassword: false,
      loading: false,
      features: [
        {
          id: 1,
          icon: 'fas fa-bell',
          title: 'Real-time Alerts',
          description: 'Instant emergency notifications',
          color: 'feature-primary'
        },
        {
          id: 2,
          icon: 'fas fa-map-marked-alt',
          title: 'Crisis Mapping',
          description: 'Live disaster tracking',
          color: 'feature-success'
        },
        {
          id: 3,
          icon: 'fas fa-users',
          title: 'Team Coordination',
          description: 'Seamless collaboration',
          color: 'feature-warning'
        },
        {
          id: 4,
          icon: 'fas fa-file-medical-alt',
          title: 'Report Management',
          description: 'Quick incident reporting',
          color: 'feature-danger'
        }
      ]
    }
  },
  methods: {
    togglePasswordVisibility() {
      this.showPassword = !this.showPassword
    },
    
    async handleLogin() {
      this.loading = true
      
      try {
        const credentials = {
          email: this.credentials.email,
          password: this.credentials.password
        };
        
        const authResponse = await login(credentials);
        
        // After successful login, fetch user profile to get role and other details
        const userResponse = await getUserProfile();  // Assume you add this function to authService.js
        
        const ADMIN_ROLES = ['PROVINCIAL_ADMIN', 'MUNICIPAL_ADMIN'];

        const STAFF_ROLES = ['EVAC_CENTER_STAFF'];

        const roleCode = userResponse.role || 'CITIZEN';

        let userType = 'citizen';

        if (ADMIN_ROLES.includes(roleCode)) {
          userType = 'admin';
        } else if (STAFF_ROLES.includes(roleCode)) {
          userType = 'staff';
        }

        // Store user session
        const userData = {
          userType,      // 'admin' | 'staff' | 'citizen'
          roleCode,      // exact backend role
          first_name: userResponse.first_name,
          last_name: userResponse.last_name,
          email: userResponse.email,
          loginTime: new Date().toISOString()
        };

        localStorage.setItem('userData', JSON.stringify(userData));
        localStorage.setItem('isAuthenticated', 'true');
        
        // Redirect based on role
        if (ADMIN_ROLES.includes(roleCode) || STAFF_ROLES.includes(roleCode)) {
          this.$router.push('/admin/dashboard');
        } else {
          this.$router.push('/user/dashboard');
        }
        
        this.$emit('login-success', userData);
      } catch (error) {
        console.error('Login error:', error);
        alert(error.message || 'Login failed. Please try again.');
      } finally {
        this.loading = false;
      }
    },
    
    fillDemo(type) {
      if (type === 'user') {
        this.credentials.email = 'user@disasterportal.com'
        this.credentials.password = 'user123'
      } else {
        this.credentials.email = 'admin@disasterportal.com'
        this.credentials.password = 'admin123'
      }
    }
  },
  
  mounted() {
    // Check if user is already logged in
    const isAuthenticated = localStorage.getItem('isAuthenticated')
    if (isAuthenticated) {
      const userData = JSON.parse(localStorage.getItem('userData') || '{}')
      if (userData.userType === 'admin' || userData.userType === 'staff') {
        this.$router.push('/admin/dashboard')
      } else {
        this.$router.push('/user/dashboard')
      }
    }
    
    // Add floating animations
    const shapes = document.querySelectorAll('.floating-shape')
    shapes.forEach((shape, index) => {
      shape.style.animation = `float ${3 + index}s ease-in-out infinite`
    })
  }
}
</script>

<style scoped>
.auth-layout {
  min-height: 100vh;
  background: linear-gradient(135deg, #1a365d 0%, #1a1a2e 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  position: relative;
  overflow: hidden;
}

.login-container {
  width: 100%;
  max-width: 1200px;
  animation: fadeIn 1s ease-out;
}

.login-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  overflow: hidden;
  display: grid;
  grid-template-columns: 1fr 1fr;
  min-height: 700px;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.2);
  position: relative;
}

.animated-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  overflow: hidden;
}

.floating-shape {
  position: absolute;
  border-radius: 50%;
  background: linear-gradient(45deg, var(--accent), transparent);
  opacity: 0.1;
}

.shape-1 {
  width: 200px;
  height: 200px;
  top: -50px;
  left: -50px;
}

.shape-2 {
  width: 150px;
  height: 150px;
  bottom: 100px;
  right: 100px;
}

.shape-3 {
  width: 100px;
  height: 100px;
  top: 50%;
  right: 200px;
}

@keyframes float {
  0%, 100% { transform: translateY(0) rotate(0deg); }
  50% { transform: translateY(-20px) rotate(180deg); }
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.login-left {
  padding: 50px;
  background: linear-gradient(135deg, rgba(26, 54, 93, 0.9) 0%, rgba(26, 26, 46, 0.9) 100%);
  display: flex;
  flex-direction: column;
  justify-content: center;
  position: relative;
}

.logo-section {
  text-align: center;
  margin-bottom: 60px;
}

.logo-icon {
  font-size: 4rem;
  color: var(--accent);
  margin-bottom: 20px;
  animation: pulse 2s infinite;
}

.logo-title {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 10px;
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.logo-subtitle {
  color: var(--text-light);
  font-size: 1.1rem;
}

.features-grid {
  display: grid;
  gap: 25px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 15px;
  transition: all 0.3s ease;
  border: 1px solid transparent;
}

.feature-item:hover {
  transform: translateX(10px);
  border-color: rgba(255, 255, 255, 0.2);
  background: rgba(255, 255, 255, 0.1);
}

.feature-icon {
  width: 60px;
  height: 60px;
  border-radius: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
}

.feature-primary { background: rgba(49, 130, 206, 0.2); color: var(--accent); }
.feature-success { background: rgba(56, 161, 105, 0.2); color: var(--success); }
.feature-warning { background: rgba(221, 107, 32, 0.2); color: var(--warning); }
.feature-danger { background: rgba(229, 62, 62, 0.2); color: var(--danger); }

.feature-content h3 {
  font-size: 1.2rem;
  margin-bottom: 5px;
  color: white;
}

.feature-content p {
  color: var(--text-light);
  font-size: 0.9rem;
}

.login-right {
  padding: 50px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  background: rgba(255, 255, 255, 0.05);
}

.login-form {
  max-width: 400px;
  margin: 0 auto;
  width: 100%;
}

.form-title {
  font-size: 2.2rem;
  margin-bottom: 10px;
  color: white;
  text-align: center;
}

.form-subtitle {
  color: var(--text-light);
  text-align: center;
  margin-bottom: 30px;
}

.form-group {
  margin-bottom: 25px;
}

.form-label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: white;
}

.input-group {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 15px;
  color: var(--text-light);
  z-index: 2;
}

.form-input {
  width: 100%;
  padding: 15px 15px 15px 45px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: rgba(255, 255, 255, 0.1);
  color: white;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.form-input:focus {
  outline: none;
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(49, 130, 206, 0.3);
  background: rgba(255, 255, 255, 0.15);
}

.password-toggle {
  position: absolute;
  right: 15px;
  background: none;
  border: none;
  color: var(--text-light);
  cursor: pointer;
  z-index: 2;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  color: var(--text-light);
}

.checkbox-label input {
  display: none;
}

.checkmark {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 4px;
  position: relative;
  transition: all 0.3s ease;
}

.checkbox-label input:checked + .checkmark {
  background: var(--accent);
  border-color: var(--accent);
}

.checkbox-label input:checked + .checkmark::after {
  content: '✓';
  position: absolute;
  color: white;
  font-size: 12px;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.forgot-password {
  color: var(--accent);
  text-decoration: none;
  transition: color 0.3s ease;
}

.forgot-password:hover {
  color: #63b3ed;
}

.login-btn {
  width: 100%;
  padding: 15px;
  background: var(--accent);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-bottom: 25px;
}

.login-btn:hover:not(:disabled) {
  background: #2b6cb0;
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(49, 130, 206, 0.3);
}

.login-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.divider {
  text-align: center;
  margin: 25px 0;
  color: var(--text-light);
  position: relative;
}

.divider::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 1px;
  background: rgba(255, 255, 255, 0.2);
}

.divider span {
  background: rgba(255, 255, 255, 0.05);
  padding: 0 15px;
}

.social-login {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
  margin-bottom: 25px;
}

.social-btn {
  padding: 12px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.social-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
}

.terms {
  text-align: center;
  color: var(--text-light);
  font-size: 0.9rem;
  line-height: 1.5;
}

.terms-link {
  color: var(--accent);
  text-decoration: none;
}

.demo-accounts {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.demo-accounts h4 {
  text-align: center;
  margin-bottom: 15px;
  color: var(--text-light);
  font-weight: 500;
}

.demo-buttons {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.demo-btn {
  padding: 12px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.demo-btn.user {
  background: rgba(56, 161, 105, 0.2);
  color: var(--success);
  border: 1px solid rgba(56, 161, 105, 0.3);
}

.demo-btn.admin {
  background: rgba(221, 107, 32, 0.2);
  color: var(--warning);
  border: 1px solid rgba(221, 107, 32, 0.3);
}

.demo-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
}

/* Responsive Design */
@media (max-width: 968px) {
  .login-card {
    grid-template-columns: 1fr;
  }
  
  .login-left {
    display: none;
  }
}

@media (max-width: 480px) {
  .login-right {
    padding: 30px 20px;
  }
  
  .social-login {
    grid-template-columns: 1fr;
  }
  
  .demo-buttons {
    grid-template-columns: 1fr;
  }
}
</style>