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
                    :disabled="emailVerified"
                    @input="onEmailChanged"
                    required
                  >
                  <button
                    type="button"
                    class="otp-inline-btn"
                    :disabled="!isEmailValid || emailVerified || otpCooldown > 0 || sendingOtp"
                    @click="sendOtp"
                  >
                    <span v-if="emailVerified"><i class="fas fa-check"></i> Verified</span>
                    <span v-else-if="sendingOtp">Sending...</span>
                    <span v-else-if="otpCooldown > 0">Resend in {{ otpCooldown }}s</span>
                    <span v-else-if="otpSent">Resend code</span>
                    <span v-else>Send code</span>
                  </button>
                </div>
                <p v-if="otpError" class="captcha-error">{{ otpError }}</p>
              </div>

              <div class="form-group" v-if="otpSent && !emailVerified">
                <label class="form-label">Verification Code</label>
                <div class="input-group">
                  <i class="fas fa-key input-icon"></i>
                  <input
                    type="text"
                    class="form-input"
                    placeholder="6-digit code"
                    maxlength="6"
                    inputmode="numeric"
                    v-model="otpCode"
                  >
                  <button
                    type="button"
                    class="otp-inline-btn"
                    :disabled="otpCode.length !== 6 || verifyingOtp"
                    @click="verifyOtp"
                  >
                    <span v-if="verifyingOtp">Checking...</span>
                    <span v-else>Verify</span>
                  </button>
                </div>
                <p class="otp-hint">We sent a code to {{ form.email }}. It expires in 10 minutes.</p>
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

              <div class="form-group captcha-group">
                <div ref="captchaEl" class="g-recaptcha"></div>
                <p v-if="captchaError" class="captcha-error">{{ captchaError }}</p>
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

      // reCAPTCHA
      captchaToken: "",
      captchaError: "",
      captchaWidgetId: null,

      // Email OTP verification
      otpSent: false,
      otpCode: "",
      otpError: "",
      sendingOtp: false,
      verifyingOtp: false,
      emailVerified: false,
      otpCooldown: 0,
      otpCooldownTimer: null,

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

  computed: {
    isEmailValid() {
      return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(this.form.email.trim());
    }
  },
 
  mounted() {
    try {
      this.fetchMunicipalities();
    } catch (e) {
      console.error("Failed to load municipalities:", e);
    }

    this.loadRecaptcha();

    const shapes = document.querySelectorAll(".floating-shape");
    shapes.forEach((shape, index) => {
      shape.style.animation = `float ${3 + index}s ease-in-out infinite`;
    });
  },

  beforeUnmount() {
    if (this.otpCooldownTimer) {
      clearInterval(this.otpCooldownTimer);
    }
  },
 
  methods: {
    togglePasswordVisibility() {
      this.showPassword = !this.showPassword;
    },

    onEmailChanged() {
      // If the user edits the email after verifying/sending, the old OTP no longer applies.
      if (this.otpSent || this.emailVerified) {
        this.otpSent = false;
        this.emailVerified = false;
        this.otpCode = "";
        this.otpError = "";
      }
    },

    startOtpCooldown(seconds) {
      this.otpCooldown = seconds;
      if (this.otpCooldownTimer) clearInterval(this.otpCooldownTimer);
      this.otpCooldownTimer = setInterval(() => {
        this.otpCooldown -= 1;
        if (this.otpCooldown <= 0) {
          clearInterval(this.otpCooldownTimer);
          this.otpCooldownTimer = null;
        }
      }, 1000);
    },

    async sendOtp() {
      this.otpError = "";
      if (!this.isEmailValid) {
        this.otpError = "Enter a valid email address first.";
        return;
      }

      this.sendingOtp = true;
      try {
        await api.post("/auth/register/send-otp/", { email: this.form.email.trim().toLowerCase() });
        this.otpSent = true;
        this.otpCode = "";
        this.startOtpCooldown(60);
      } catch (error) {
        const data = error?.response?.data;
        this.otpError = data?.email || data?.detail || "Failed to send verification code.";
      } finally {
        this.sendingOtp = false;
      }
    },

    async verifyOtp() {
      this.otpError = "";
      this.verifyingOtp = true;
      try {
        await api.post("/auth/register/verify-otp/", {
          email: this.form.email.trim().toLowerCase(),
          otp_code: this.otpCode,
        });
        this.emailVerified = true;
        if (this.otpCooldownTimer) {
          clearInterval(this.otpCooldownTimer);
          this.otpCooldownTimer = null;
        }
        this.otpCooldown = 0;
      } catch (error) {
        const data = error?.response?.data;
        this.otpError = data?.otp_code || data?.detail || "Verification failed.";
      } finally {
        this.verifyingOtp = false;
      }
    },

    async handleRegister() {
      this.captchaError = "";

      if (!this.emailVerified) {
        this.otpError = "Please verify your email before registering.";
        return;
      }

      if (!this.captchaToken) {
        this.captchaError = "Please complete the captcha before registering.";
        return;
      }

      this.loading = true;

      try {
        const response = await register({
          ...this.form,
          captcha_token: this.captchaToken,
        });

        alert("Registration successful! Please log in.");
        this.$router.push("/auth/login");

      } catch (error) {
        console.error("Register error:", error);
        alert(error?.error || error?.captcha_token || error?.email || JSON.stringify(error) || "Registration failed.");
        // Captcha tokens are single-use; force the user to re-solve it after any failed attempt.
        this.resetCaptcha();
      } finally {
        this.loading = false;
      }
    },

    loadRecaptcha() {
      const siteKey = import.meta.env.VITE_RECAPTCHA_SITE_KEY;
      if (!siteKey) {
        console.error("VITE_RECAPTCHA_SITE_KEY is not set; captcha will not render.");
        this.captchaError = "Captcha is unavailable right now. Please try again later.";
        return;
      }

      const renderWidget = () => {
        if (window.grecaptcha && this.$refs.captchaEl) {
          this.captchaWidgetId = window.grecaptcha.render(this.$refs.captchaEl, {
            sitekey: siteKey,
            theme: "dark",
            callback: (token) => {
              this.captchaToken = token;
              this.captchaError = "";
            },
            "expired-callback": () => {
              this.captchaToken = "";
            },
            "error-callback": () => {
              this.captchaToken = "";
              this.captchaError = "Captcha failed to load. Please refresh and try again.";
            },
          });
        }
      };

      if (window.grecaptcha && window.grecaptcha.render) {
        renderWidget();
        return;
      }

      const existingScript = document.getElementById("recaptcha-script");
      if (!existingScript) {
        window.onRecaptchaLoad = renderWidget;
        const script = document.createElement("script");
        script.id = "recaptcha-script";
        script.src = "https://www.google.com/recaptcha/api.js?onload=onRecaptchaLoad&render=explicit";
        script.async = true;
        script.defer = true;
        document.head.appendChild(script);
      } else {
        window.onRecaptchaLoad = renderWidget;
      }
    },

    resetCaptcha() {
      this.captchaToken = "";
      if (window.grecaptcha && this.captchaWidgetId !== null) {
        window.grecaptcha.reset(this.captchaWidgetId);
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

};
</script>

<style scoped>
.auth-layout {
  min-height: 100vh;
  background: linear-gradient(135deg, #1a365d 0%, #1a1a2e 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
  position: relative;
  overflow: hidden;
}

.login-container {
  width: 100%;
  max-width: 1050px; /* Compressed card width */
  animation: fadeIn 0.8s ease-out;
}

.login-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  overflow: hidden;
  display: grid;
  grid-template-columns: 1fr 1fr;
  min-height: auto; /* Allow auto height based on contents */
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
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
  background: linear-gradient(45deg, var(--accent, #3182ce), transparent);
  opacity: 0.1;
}

.shape-1 {
  width: 160px;
  height: 160px;
  top: -40px;
  left: -40px;
}

.shape-2 {
  width: 120px;
  height: 120px;
  bottom: 80px;
  right: 80px;
}

.shape-3 {
  width: 80px;
  height: 80px;
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
  padding: 32px 36px;
  background: linear-gradient(135deg, rgba(26, 54, 93, 0.9) 0%, rgba(26, 26, 46, 0.9) 100%);
  display: flex;
  flex-direction: column;
  justify-content: center;
  position: relative;
}

.logo-section {
  text-align: center;
  margin-bottom: 30px;
}

.logo-icon {
  font-size: 3rem;
  color: var(--accent, #3182ce);
  margin-bottom: 12px;
}

.logo-title {
  font-size: 1.85rem;
  font-weight: 700;
  margin-bottom: 6px;
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.logo-subtitle {
  color: var(--text-light, #a0aec0);
  font-size: 0.95rem;
}

.features-grid {
  display: grid;
  gap: 16px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 16px;
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
  width: 44px;
  height: 44px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  flex-shrink: 0;
}

.feature-primary { background: rgba(49, 130, 206, 0.2); color: var(--accent, #3182ce); }
.feature-success { background: rgba(56, 161, 105, 0.2); color: var(--success, #38a169); }
.feature-warning { background: rgba(221, 107, 32, 0.2); color: var(--warning, #dd6b20); }
.feature-danger { background: rgba(229, 62, 62, 0.2); color: var(--danger, #e53e3e); }

.feature-content h3 {
  font-size: 1.05rem;
  margin-bottom: 2px;
  color: white;
}

.feature-content p {
  color: var(--text-light, #a0aec0);
  font-size: 0.82rem;
}

.login-right {
  padding: 32px 36px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  background: rgba(255, 255, 255, 0.05);
}

.login-form {
  max-width: 380px;
  margin: 0 auto;
  width: 100%;
}

.form-title {
  font-size: 1.75rem;
  margin-bottom: 4px;
  color: white;
  text-align: center;
}

.form-subtitle {
  color: var(--text-light, #a0aec0);
  text-align: center;
  margin-bottom: 18px;
  font-size: 0.88rem;
}

/* Reduced spacing between form controls */
.form-group {
  margin-bottom: 12px;
}

.form-label {
  display: block;
  margin-bottom: 4px;
  font-weight: 500;
  color: white;
  font-size: 0.85rem;
}

.input-group {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 14px;
  color: var(--text-light, #a0aec0);
  z-index: 2;
  font-size: 0.9rem;
}

/* Slimmer input height & tighter padding */
.form-input {
  width: 100%;
  padding: 9px 12px 9px 40px;
  border-radius: 8px;
  border: 1px solid #4b5563;
  background-color: #1f2937;
  color: #f9fafb;
  font-size: 0.9rem;
  transition: all 0.25s ease;
}

.input-group .form-input {
  padding-right: 95px;
}

.form-input option {
  background-color: #1f2937;
  color: #f9fafb;
}

.form-input:focus {
  outline: none;
  border-color: var(--accent, #3182ce);
  box-shadow: 0 0 0 3px rgba(49, 130, 206, 0.3);
  background: rgba(255, 255, 255, 0.15);
}

.otp-inline-btn {
  position: absolute;
  right: 5px;
  top: 50%;
  transform: translateY(-50%);
  z-index: 3;
  padding: 5px 10px;
  border-radius: 6px;
  border: none;
  background: var(--accent, #3182ce);
  color: #ffffff;
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s ease;
}

.otp-inline-btn:hover:not(:disabled) {
  background: #2b6cb0;
}

.otp-inline-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.otp-hint {
  font-size: 0.75rem;
  color: var(--text-light, #a0aec0);
  margin-top: 4px;
}

.password-toggle {
  position: absolute;
  right: 12px;
  background: none;
  border: none;
  color: var(--text-light, #a0aec0);
  cursor: pointer;
  z-index: 2;
  font-size: 0.9rem;
}

/* reCAPTCHA Tight Alignment */
.captcha-group {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  margin: 12px 0;
}

.g-recaptcha {
  display: inline-block;
  background: transparent !important;
  border-radius: 4px;
  box-shadow: none !important;
  border: none !important;
  line-height: 0;
}

.g-recaptcha > div {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  margin: 0 auto;
}

.g-recaptcha iframe {
  background-color: #222222 !important;
  border-radius: 4px !important;
  border: none !important;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
}

.captcha-error {
  color: var(--danger, #e53e3e);
  font-size: 0.8rem;
  margin-top: 4px;
  text-align: center;
}

.login-btn {
  width: 100%;
  padding: 11px;
  background: var(--accent, #3182ce);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.25s ease;
  margin-top: 8px; /* Extra offset gap from captcha */
  margin-bottom: 16px;
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
  font-size: 0.82rem;
  line-height: 1.4;
}

.terms-link {
  color: var(--accent, #3182ce);
  text-decoration: none;
  font-weight: 500;
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
    padding: 24px 16px;
  }
  
  .g-recaptcha {
    transform: scale(0.85);
    transform-origin: center center;
    margin: -6px 0;
  }
}
</style>