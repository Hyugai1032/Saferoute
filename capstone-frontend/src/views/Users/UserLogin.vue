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
          <!-- LOGIN VIEW -->
          <div class="login-form" v-if="authView === 'login'">
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
                <a href="#" class="forgot-password" @click.prevent="goToForgotPassword">Forgot password?</a>
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
            </form>
          </div>

          <!-- FORGOT PASSWORD: STEP 1 - REQUEST OTP -->
          <div class="login-form" v-else-if="authView === 'forgot-request'">
            <button type="button" class="back-btn" @click="goToLogin">
              <i class="fas fa-arrow-left"></i> Back to sign in
            </button>

            <h2 class="form-title">Forgot Password</h2>
            <p class="form-subtitle">Enter your email and we'll send you a code to reset your password</p>

            <p v-if="forgotError" class="form-error">{{ forgotError }}</p>

            <form @submit.prevent="handleRequestOtp">
              <div class="form-group">
                <label class="form-label">Email</label>
                <div class="input-group">
                  <i class="fas fa-user input-icon"></i>
                  <input
                    type="email"
                    class="form-input"
                    placeholder="Enter your email"
                    v-model="forgotForm.email"
                    required
                  >
                </div>
              </div>

              <button class="login-btn" type="submit" :disabled="forgotLoading">
                <span v-if="!forgotLoading">
                  <i class="fas fa-paper-plane"></i>
                  Send Code
                </span>
                <span v-else>
                  <i class="fas fa-spinner fa-spin"></i>
                  Sending...
                </span>
              </button>
            </form>
          </div>

          <!-- FORGOT PASSWORD: STEP 2 - ENTER OTP + NEW PASSWORD -->
          <div class="login-form" v-else-if="authView === 'forgot-reset'">
            <button type="button" class="back-btn" @click="goToForgotPassword">
              <i class="fas fa-arrow-left"></i> Use a different email
            </button>

            <h2 class="form-title">Enter Code</h2>
            <p class="form-subtitle">
              We sent a 6-digit code to <strong>{{ forgotForm.email }}</strong>
            </p>

            <p v-if="forgotError" class="form-error">{{ forgotError }}</p>
            <p v-if="forgotSuccess" class="form-success">{{ forgotSuccess }}</p>

            <form @submit.prevent="handleResetPassword">
              <div class="form-group">
                <label class="form-label">Verification Code</label>
                <div class="input-group">
                  <i class="fas fa-key input-icon"></i>
                  <input
                    type="text"
                    inputmode="numeric"
                    maxlength="6"
                    autocomplete="one-time-code"
                    class="form-input otp-input"
                    placeholder="6-digit code"
                    v-model="forgotForm.otp"
                    required
                  >
                </div>
              </div>

              <div class="form-group">
                <label class="form-label">New Password</label>
                <div class="input-group">
                  <i class="fas fa-lock input-icon"></i>
                  <input
                    :type="showPassword ? 'text' : 'password'"
                    class="form-input"
                    placeholder="Enter new password"
                    v-model="forgotForm.newPassword"
                    minlength="8"
                    required
                  >
                  <button type="button" class="password-toggle" @click="togglePasswordVisibility">
                    <i :class="showPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
                  </button>
                </div>
              </div>

              <div class="form-group">
                <label class="form-label">Confirm New Password</label>
                <div class="input-group">
                  <i class="fas fa-lock input-icon"></i>
                  <input
                    :type="showPassword ? 'text' : 'password'"
                    class="form-input"
                    placeholder="Confirm new password"
                    v-model="forgotForm.confirmPassword"
                    minlength="8"
                    required
                  >
                </div>
              </div>

              <button class="login-btn" type="submit" :disabled="forgotLoading">
                <span v-if="!forgotLoading">
                  <i class="fas fa-check"></i>
                  Reset Password
                </span>
                <span v-else>
                  <i class="fas fa-spinner fa-spin"></i>
                  Resetting...
                </span>
              </button>

              <div style="text-align: center;">
                <p>
                  Didn't get a code?
                  <a
                    href="#"
                    class="forgot-password"
                    :class="{ disabled: resendCooldown > 0 }"
                    @click.prevent="resendCooldown === 0 && handleRequestOtp()"
                  >
                    {{ resendCooldown > 0 ? `Resend in ${resendCooldown}s` : 'Resend code' }}
                  </a>
                </p>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>

import { login, getUserProfile, requestPasswordResetOtp, resetPasswordWithOtp } from '../../services/authService';

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

      // Forgot password / OTP reset flow
      authView: 'login', // 'login' | 'forgot-request' | 'forgot-reset'
      forgotForm: {
        email: '',
        otp: '',
        newPassword: '',
        confirmPassword: ''
      },
      forgotLoading: false,
      forgotError: '',
      forgotSuccess: '',
      resendCooldown: 0,
      resendTimerHandle: null,
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

    goToForgotPassword() {
      this.forgotError = ''
      this.forgotSuccess = ''
      this.forgotForm.otp = ''
      this.forgotForm.newPassword = ''
      this.forgotForm.confirmPassword = ''
      this.clearResendCooldown()
      this.authView = 'forgot-request'
    },

    goToLogin() {
      this.forgotError = ''
      this.forgotSuccess = ''
      this.clearResendCooldown()
      this.authView = 'login'
    },

    clearResendCooldown() {
      if (this.resendTimerHandle) {
        clearInterval(this.resendTimerHandle)
        this.resendTimerHandle = null
      }
      this.resendCooldown = 0
    },

    startResendCooldown(seconds = 60) {
      this.clearResendCooldown()
      this.resendCooldown = seconds
      this.resendTimerHandle = setInterval(() => {
        this.resendCooldown -= 1
        if (this.resendCooldown <= 0) {
          this.clearResendCooldown()
        }
      }, 1000)
    },

    // Backend errors thrown by authService are plain objects, not Error instances,
    // and can come back in a few shapes:
    //   { message: '...' } / { error: '...' } / { detail: '...' }
    //   { otp_code: '...' } or { new_password: ['...'] }  (DRF field-level errors)
    getErrorMessage(error, fallback) {
      if (!error) return fallback
      if (typeof error === 'string') return error
      if (error.message) return error.message
      if (error.detail) return error.detail
      if (error.error) return error.error

      const firstKey = Object.keys(error)[0]
      if (firstKey) {
        const value = error[firstKey]
        if (Array.isArray(value) && value.length) return value[0]
        if (typeof value === 'string') return value
      }

      return fallback
    },

    async handleRequestOtp() {
      if (!this.forgotForm.email) {
        this.forgotError = 'Please enter your email address.'
        return
      }

      this.forgotError = ''
      this.forgotSuccess = ''
      this.forgotLoading = true

      try {
        await requestPasswordResetOtp(this.forgotForm.email)
        this.forgotSuccess = 'If an account exists for that email, a code has been sent.'
        this.authView = 'forgot-reset'
        this.startResendCooldown(60) // matches backend OTP_RESEND_COOLDOWN_SECONDS
      } catch (error) {
        console.error('Request OTP error:', error)
        // Avoid confirming/denying whether an email exists
        this.forgotError = this.getErrorMessage(error, 'Something went wrong. Please try again.')
      } finally {
        this.forgotLoading = false
      }
    },

    async handleResetPassword() {
      this.forgotError = ''
      this.forgotSuccess = ''

      if (!/^\d{6}$/.test(this.forgotForm.otp)) {
        this.forgotError = 'Please enter the 6-digit code.'
        return
      }

      if (this.forgotForm.newPassword.length < 8) {
        this.forgotError = 'Password must be at least 8 characters.'
        return
      }

      if (this.forgotForm.newPassword !== this.forgotForm.confirmPassword) {
        this.forgotError = 'Passwords do not match.'
        return
      }

      this.forgotLoading = true

      try {
        await resetPasswordWithOtp({
          email: this.forgotForm.email,
          otp: this.forgotForm.otp,
          newPassword: this.forgotForm.newPassword
        })

        // Pre-fill login form and hand back to sign-in
        this.credentials.email = this.forgotForm.email
        this.credentials.password = ''
        this.clearResendCooldown()
        this.authView = 'login'
        this.forgotSuccess = ''
        alert('Your password has been reset. Please sign in with your new password.')
      } catch (error) {
        console.error('Reset password error:', error)
        this.forgotError = this.getErrorMessage(error, 'Could not reset password. Please check the code and try again.')
      } finally {
        this.forgotLoading = false
      }
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
        if (ADMIN_ROLES.includes(roleCode)) {
          this.$router.push("/admin/dashboard");
        } else if (STAFF_ROLES.includes(roleCode)) {
          this.$router.push("/staff/dashboard");
        } else {
          this.$router.push("/user/dashboard");
        }
        
        this.$emit('login-success', userData);
      } catch (error) {
        console.error('Login error:', error);
        alert(this.getErrorMessage(error, 'Login failed. Please try again.'));
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
  },

  beforeUnmount() {
    this.clearResendCooldown()
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
  padding: 24px;
  position: relative;
  overflow: hidden;
}

.login-container {
  width: 100%;
  max-width: 1120px; /* Slightly wider card balance */
  animation: fadeIn 0.8s ease-out;
}

.login-card {
  position: relative;
  display: grid;
  grid-template-columns: 1fr 1fr;
  min-height: auto;
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
  overflow: hidden;
  /* Eliminates sub-pixel blur bleeding */
  background: rgba(255, 255, 255, 0.08);
}

/* Dedicated blur layer that stays strictly within bounds */
.login-card::before {
  content: '';
  position: absolute;
  inset: 0;
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  z-index: 0;
  border-radius: 20px;
}

/* Elevate internal layout above the blur layer */
.login-left,
.login-right,
.animated-bg {
  position: relative;
  z-index: 1;
}

.login-left {
  padding: 42px 44px;
  background: linear-gradient(135deg, rgba(26, 54, 93, 0.9) 0%, rgba(26, 26, 46, 0.9) 100%);
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.login-right {
  padding: 42px 44px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  background: rgba(255, 255, 255, 0.05);
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
  background: linear-gradient(45deg, var(--accent, #3182ce), transparent);
  opacity: 0.1;
}

.shape-1 {
  width: 180px;
  height: 180px;
  top: -40px;
  left: -40px;
}

.shape-2 {
  width: 140px;
  height: 140px;
  bottom: 80px;
  right: 80px;
}

.shape-3 {
  width: 90px;
  height: 90px;
  top: 50%;
  right: 150px;
}

@keyframes float {
  0%, 100% { transform: translateY(0) rotate(0deg); }
  50% { transform: translateY(-15px) rotate(180deg); }
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(15px); }
  to { opacity: 1; transform: translateY(0); }
}

.login-left {
  padding: 42px 44px; /* More breathing room */
  background: linear-gradient(135deg, rgba(26, 54, 93, 0.9) 0%, rgba(26, 26, 46, 0.9) 100%);
  display: flex;
  flex-direction: column;
  justify-content: center;
  position: relative;
}

.logo-section {
  text-align: center;
  margin-bottom: 36px;
}

.logo-icon {
  font-size: 3.5rem;
  color: var(--accent, #3182ce);
  margin-bottom: 14px;
}

.logo-title {
  font-size: 2.1rem;
  font-weight: 700;
  margin-bottom: 6px;
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.logo-subtitle {
  color: var(--text-light, #a0aec0);
  font-size: 1rem;
}

.features-grid {
  display: grid;
  gap: 18px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 18px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  transition: all 0.3s ease;
  border: 1px solid transparent;
}

.feature-item:hover {
  transform: translateX(6px);
  border-color: rgba(255, 255, 255, 0.2);
  background: rgba(255, 255, 255, 0.1);
}

.feature-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.3rem;
  flex-shrink: 0;
}

.feature-primary { background: rgba(49, 130, 206, 0.2); color: var(--accent, #3182ce); }
.feature-success { background: rgba(56, 161, 105, 0.2); color: var(--success, #38a169); }
.feature-warning { background: rgba(221, 107, 32, 0.2); color: var(--warning, #dd6b20); }
.feature-danger { background: rgba(229, 62, 62, 0.2); color: var(--danger, #e53e3e); }

.feature-content h3 {
  font-size: 1.1rem;
  margin-bottom: 3px;
  color: white;
}

.feature-content p {
  color: var(--text-light, #a0aec0);
  font-size: 0.85rem;
}

.login-right {
  padding: 42px 44px;
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
  font-size: 1.95rem;
  margin-bottom: 6px;
  color: white;
  text-align: center;
}

.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: none;
  border: none;
  color: var(--text-light, #a0aec0);
  cursor: pointer;
  font-size: 0.88rem;
  margin-bottom: 16px;
  padding: 0;
  transition: color 0.25s ease;
}

.back-btn:hover {
  color: white;
}

.otp-input {
  letter-spacing: 6px;
  font-weight: 600;
}

.form-error {
  background: rgba(229, 62, 62, 0.15);
  border: 1px solid rgba(229, 62, 62, 0.3);
  color: #feb2b2;
  border-radius: 8px;
  padding: 10px 14px;
  font-size: 0.85rem;
  margin-bottom: 16px;
  text-align: center;
}

.form-success {
  background: rgba(56, 161, 105, 0.15);
  border: 1px solid rgba(56, 161, 105, 0.3);
  color: #9ae6b4;
  border-radius: 8px;
  padding: 10px 14px;
  font-size: 0.85rem;
  margin-bottom: 16px;
  text-align: center;
}

.forgot-password.disabled {
  color: var(--text-light, #a0aec0);
  cursor: not-allowed;
  opacity: 0.6;
  pointer-events: none;
}

.form-subtitle {
  color: var(--text-light, #a0aec0);
  text-align: center;
  margin-bottom: 24px;
  font-size: 0.92rem;
}

.form-group {
  margin-bottom: 18px;
}

.form-label {
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
  color: white;
  font-size: 0.9rem;
}

.input-group {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 15px;
  color: var(--text-light, #a0aec0);
  z-index: 2;
  font-size: 0.95rem;
}

/* Restored comfortable input height */
.form-input {
  width: 100%;
  padding: 12px 16px 12px 44px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: rgba(255, 255, 255, 0.1);
  color: white;
  font-size: 0.95rem;
  transition: all 0.25s ease;
}

.form-input:focus {
  outline: none;
  border-color: var(--accent, #3182ce);
  box-shadow: 0 0 0 3px rgba(49, 130, 206, 0.3);
  background: rgba(255, 255, 255, 0.15);
}

.password-toggle {
  position: absolute;
  right: 15px;
  background: none;
  border: none;
  color: var(--text-light, #a0aec0);
  cursor: pointer;
  z-index: 2;
  font-size: 0.95rem;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
  margin-bottom: 22px;
  font-size: 0.88rem;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: var(--text-light, #a0aec0);
}

.checkbox-label input {
  display: none;
}

.checkmark {
  width: 17px;
  height: 17px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 4px;
  position: relative;
  transition: all 0.25s ease;
}

.checkbox-label input:checked + .checkmark {
  background: var(--accent, #3182ce);
  border-color: var(--accent, #3182ce);
}

.checkbox-label input:checked + .checkmark::after {
  content: '✓';
  position: absolute;
  color: white;
  font-size: 11px;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.forgot-password {
  color: var(--accent, #3182ce);
  text-decoration: none;
  transition: color 0.25s ease;
}

.forgot-password:hover {
  color: #63b3ed;
}

.login-btn {
  width: 100%;
  padding: 12px;
  background: var(--accent, #3182ce);
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.25s ease;
  margin-bottom: 20px;
}

.login-btn:hover:not(:disabled) {
  background: #2b6cb0;
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(49, 130, 206, 0.3);
}

.login-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.terms {
  text-align: center;
  color: var(--text-light, #a0aec0);
  font-size: 0.85rem;
  line-height: 1.4;
}

.terms-link {
  color: var(--accent, #3182ce);
  text-decoration: none;
}

.demo-accounts {
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.demo-accounts h4 {
  text-align: center;
  margin-bottom: 12px;
  color: var(--text-light, #a0aec0);
  font-weight: 500;
  font-size: 0.85rem;
}

.demo-buttons {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.demo-btn {
  padding: 10px 14px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.88rem;
  transition: all 0.25s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.demo-btn.user {
  background: rgba(56, 161, 105, 0.2);
  color: var(--success, #38a169);
  border: 1px solid rgba(56, 161, 105, 0.3);
}

.demo-btn.admin {
  background: rgba(221, 107, 32, 0.2);
  color: var(--warning, #dd6b20);
  border: 1px solid rgba(221, 107, 32, 0.3);
}

.demo-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
}

/* Responsive Scaling */
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
    padding: 28px 20px;
  }
}
</style>