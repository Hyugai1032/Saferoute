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
              <i class="fas fa-user-plus"></i>
            </div>
            <h1 class="logo-title">Create Your Account</h1>
            <p class="logo-subtitle">Join the Disaster Response Portal</p>
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
            <h2 class="form-title">Register</h2>
            <p class="form-subtitle">Fill in your details below</p>

            <form @submit.prevent="handleRegister">
              <div class="form-group">
                <label class="form-label">First Name</label>
                <div class="input-group">
                  <i class="fas fa-id-card input-icon"></i>
                  <input 
                    type="text"
                    class="form-input"
                    placeholder="Enter first name"
                    v-model="form.first_name"
                    required
                  >
                </div>
              </div>

              <div class="form-group">
                <label class="form-label">Last Name</label>
                <div class="input-group">
                  <i class="fas fa-id-card input-icon"></i>
                  <input 
                    type="text"
                    class="form-input"
                    placeholder="Enter last name"
                    v-model="form.last_name"
                    required
                  >
                </div>
              </div>

              <div class="form-group">
                <label class="form-label">Email</label>
                <div class="input-group">
                  <i class="fas fa-envelope input-icon"></i>
                  <input 
                    type="email"
                    class="form-input"
                    placeholder="Enter your email"
                    v-model="form.email"
                    required
                  >
                </div>
              </div>

              <div class="form-group">
                <label class="form-label">Contact Number</label>
                <div class="input-group">
                  <i class="fas fa-phone input-icon"></i>
                  <input 
                    type="text"
                    class="form-input"
                    placeholder="09123456789"
                    maxlength="11"
                    v-model="form.contact_number"
                  >
                </div>
              </div>

              <!-- Municipality -->
              <div class="form-group">
                <label class="form-label">Municipality</label>
                <div class="input-group">
                  <i class="fas fa-map-marker-alt input-icon"></i>

                  <select
                    class="form-input"
                    v-model="form.municipality"
                    required
                    :disabled="dropdownLoading.municipalities"
                  >
                    <option value="" disabled>
                      {{ dropdownLoading.municipalities ? "Loading..." : "Select Municipality" }}
                    </option>
                    <option
                      v-for="m in municipalities"
                      :key="m.id"
                      :value="m.id"
                    >
                      {{ m.name }}
                    </option>
                  </select>
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
                    v-model="form.password"
                    required
                  >
                  <button type="button" class="password-toggle" @click="togglePasswordVisibility">
                    <i :class="showPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
                  </button>
                </div>
              </div>

              <button class="login-btn" type="submit" :disabled="loading">
                <span v-if="!loading">
                  <i class="fas fa-user-plus"></i>
                  Register
                </span>
                <span v-else>
                  <i class="fas fa-spinner fa-spin"></i>
                  Creating Account...
                </span>
              </button>

              <p class="terms">
                Already have an account?
                <router-link to="login" class="terms-link">Sign in</router-link>
              </p>
            </form>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script>
import { register } from "@/services/authService"
import api from "@/services/api"; 
export default {
  name: "UserRegister",
  data() {
    return {
      form: {
        first_name: "",
        last_name: "",
        email: "",
        password: "",
        contact_number: "",
         municipality: ""  
      },
      municipalities: [],
      dropdownLoading: {
        municipalities: false
      },
      loading: false,
      showPassword: false,

      features: [
        {
          id: 1,
          icon: "fas fa-check-circle",
          title: "Quick Registration",
          description: "Create your account in minutes",
          color: "feature-primary"
        },
        {
          id: 2,
          icon: "fas fa-lock",
          title: "Secure Access",
          description: "Your data is always protected",
          color: "feature-danger"
        },
        {
          id: 3,
          icon: "fas fa-headset",
          title: "Support Ready",
          description: "We’re here to help anytime",
          color: "feature-success"
        }
      ]
    };
  },
  methods: {
    togglePasswordVisibility() {
      this.showPassword = !this.showPassword;
    },

    async handleRegister() {
      this.loading = true;

      try {
        const response = await register(this.form);

        alert("Registration successful! Please log in.");
        this.$router.push("/auth/login");

      } catch (error) {
        console.error("Register error:", error);
        alert(error?.error || JSON.stringify(error) || "Registration failed.");
      } finally {
        this.loading = false;
      }
    },

    async fetchMunicipalities() {
      this.dropdownLoading.municipalities = true;
      try {
        const res = await api.get("municipalities/", { params: { page_size: 9999 } });
        const data = res.data;

        this.municipalities = Array.isArray(data) ? data : (data.results || []);

        // optional: sort A-Z
        this.municipalities.sort((a, b) => (a.name || "").localeCompare(b.name || ""));
      } catch (err) {
        console.error("Failed to fetch municipalities:", err);
        this.municipalities = [];
      } finally {
        this.dropdownLoading.municipalities = false;
      }
    },
  },

    async mounted() {
      try {
        this.fetchMunicipalities();
      } catch (e) {
        console.error("Failed to load municipalities:", e);
      }

      const shapes = document.querySelectorAll(".floating-shape");
      shapes.forEach((shape, index) => {
        shape.style.animation = `float ${3 + index}s ease-in-out infinite`;
      });
    }
};
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

.form-input {
  background-color: #1f2937;
  color: #f9fafb;
  border: 1px solid #4b5563;
}

.form-input option {
  background-color: #1f2937;
  color: #f9fafb;
}
</style>