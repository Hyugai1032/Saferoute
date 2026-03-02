<!-- src/views/Users/UserProfile.vue -->
<template>
  <div class="user-profile">
    <!-- Profile Header with Animated Background -->
    <div class="profile-header">
      <div class="header-background">
        <div class="animated-shapes">
          <div v-for="i in 5" :key="i" class="shape" :style="getShapeStyle(i)"></div>
        </div>
      </div>

      <div class="header-content">
        <!-- Profile Avatar -->
        <div class="avatar-section">
          <div class="avatar-container">
            <img
              v-if="user.avatar"
              :src="user.avatar"
              alt="Profile"
              class="profile-avatar"
            >
            <div v-else class="profile-avatar default">
              {{ user.initials }}
            </div>

            <button class="avatar-edit-btn" @click="triggerAvatarUpload" title="Change avatar">
              <i class="icon-camera"></i>
            </button>

            <input
              type="file"
              ref="avatarInput"
              @change="handleAvatarUpload"
              accept="image/*"
              style="display: none"
            >
          </div>

          <div class="avatar-info">
            <h1 class="user-name">{{ user.name || "—" }}</h1>
            <p class="user-email">{{ user.email || "—" }}</p>

            <div class="chips">
              <span class="chip">
                <i class="icon-calendar"></i>
                Member since {{ user.joinDate || "—" }}
              </span>
              <span class="chip" v-if="user.municipality">
                <i class="icon-location"></i>
                {{ user.municipality }}
              </span>
              <span class="chip" v-if="user.roleLabel">
                <i class="icon-user"></i>
                {{ user.roleLabel }}
              </span>
            </div>

            <div class="header-actions">
              <button class="ghost-btn" @click="copyEmail" :disabled="!user.email" title="Copy email">
                <i class="icon-copy"></i>
                Copy Email
              </button>

              <button class="primary-btn small" @click="toggleEdit">
                <i class="icon-edit"></i>
                {{ editingPersonal ? "Save" : "Edit Profile" }}
              </button>
            </div>
          </div>
        </div>

        <!-- Mini Summary (kept, but not the old 3 big cards) -->
        <div class="mini-summary">
          <div class="summary-item" :class="{ glow: editingPersonal }">
            <div class="summary-title">Status</div>
            <div class="summary-value">
              <span class="dot" :class="editingPersonal ? 'warn' : 'ok'"></span>
              {{ editingPersonal ? "Editing" : "Up to date" }}
            </div>
          </div>

          <div class="summary-item">
            <div class="summary-title">Phone</div>
            <div class="summary-value">{{ personalForm.phone || "—" }}</div>
          </div>

          <div class="summary-item">
            <div class="summary-title">Emergency Contact</div>
            <div class="summary-value">
              {{ personalForm.emergencyContact.name || "—" }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Profile Content -->
    <div class="profile-content">
      <!-- Navigation Tabs (ONLY PERSONAL) -->
      <div class="profile-tabs">
        <button class="tab-btn active">
          <i class="icon-user"></i>
          Personal Info
        </button>
      </div>

      <div class="tab-content">
        <transition name="fade">
          <div class="tab-panel personal-info">
            <div class="panel-header">
              <h3>Personal Information</h3>

              <div class="panel-actions">
                <button
                  v-if="editingPersonal"
                  class="ghost-btn"
                  @click="cancelEdits"
                  :disabled="loading"
                >
                  Cancel
                </button>

                <button class="edit-btn" @click="toggleEdit" :disabled="loading">
                  <i class="icon-edit"></i>
                  {{ editingPersonal ? "Save Changes" : "Edit Information" }}
                </button>
              </div>
            </div>

            <form class="info-form" @submit.prevent="savePersonalInfo">
              <div class="form-grid">
                <div class="input-group">
                  <label>Full Name</label>
                  <input
                    type="text"
                    v-model="personalForm.name"
                    :readonly="!editingPersonal"
                    :class="{ editable: editingPersonal }"
                    placeholder="Your full name"
                  >
                </div>

                <div class="input-group">
                  <label>Email Address</label>
                  <input
                    type="email"
                    v-model="personalForm.email"
                    :readonly="true"
                    class="readonly"
                    title="Email is managed by your account"
                  >
                  <small class="hint">Email can’t be edited here.</small>
                </div>

                <div class="input-group">
                  <label>Phone Number</label>
                  <input
                    type="tel"
                    v-model="personalForm.phone"
                    :readonly="!editingPersonal"
                    :class="{ editable: editingPersonal }"
                    placeholder="09XXXXXXXXX"
                  >
                </div>

                <div class="input-group">
                  <label>Address</label>
                  <input
                    type="text"
                    v-model="personalForm.address"
                    :readonly="!editingPersonal"
                    :class="{ editable: editingPersonal }"
                    placeholder="(Optional) Your address"
                  >
                </div>

                <div class="input-group full-width">
                  <label>Emergency Contact</label>
                  <div class="emergency-contact">
                    <input
                      type="text"
                      v-model="personalForm.emergencyContact.name"
                      placeholder="Contact Name"
                      :readonly="!editingPersonal"
                      :class="{ editable: editingPersonal }"
                    >
                    <input
                      type="tel"
                      v-model="personalForm.emergencyContact.phone"
                      placeholder="Contact Phone"
                      :readonly="!editingPersonal"
                      :class="{ editable: editingPersonal }"
                    >
                    <input
                      type="text"
                      v-model="personalForm.emergencyContact.relationship"
                      placeholder="Relationship"
                      :readonly="!editingPersonal"
                      :class="{ editable: editingPersonal }"
                    >
                  </div>
                </div>
              </div>

              <div class="save-row" v-if="editingPersonal">
                <button class="primary-btn" type="submit" :disabled="loading">
                  <i class="icon-save"></i>
                  {{ loading ? "Saving..." : "Save Profile" }}
                </button>
              </div>
            </form>
          </div>
        </transition>
      </div>
    </div>

    <!-- Toast -->
    <transition name="fade">
      <div v-if="toast.show" class="toast" :class="toast.type">
        <div class="toast-title">{{ toast.title }}</div>
        <div class="toast-msg">{{ toast.message }}</div>
      </div>
    </transition>

    <!-- Loading Overlay -->
    <transition name="fade">
<div v-if="loadingProfile" class="loading-overlay">
        <div class="loading-spinner"></div>
        <p>{{ loadingOverlayText }}</p>
      </div>
    </transition>
  </div>
</template>

<script>
import api from "@/services/api";

export default {
  name: "UserProfile",
  data() {
    return {
      editingPersonal: false,
      loading: false,          // for saving
      loadingProfile: true,    // for initial load

      loadingOverlay: false,
      loadingOverlayText: "Loading profile...",

      toast: { show: false, type: "success", title: "", message: "" },
      toastTimer: null,

      user: {
        name: "",
        email: "",
        initials: "",
        joinDate: "",
        avatar: null,
        municipality: "",
        roleLabel: "",
      },

      // keep a copy so cancel works
      personalOriginal: null,

      personalForm: {
        name: "",
        email: "",
        phone: "",
        address: "",
        emergencyContact: {
          name: "",
          phone: "",
          relationship: "",
        },
      },
    };
  },

  async mounted() {
    // ✅ Proper lifecycle hook (NOT inside methods)
    try {
      await this.loadProfile();
      // only call if you really have this endpoint:
      // await this.loadMyReports();
    } catch (e) {
      console.error("Profile mount failed:", e);
    } finally {
      this.loadingProfile = false; // ✅ prevents endless loading
    }
    },

  methods: {
    // ---------- UI helpers ----------
    getShapeStyle(index) {
      const sizes = [80, 120, 100, 150, 90];
      const delays = [0, 1, 2, 0.5, 1.5];
      return {
        width: `${sizes[index - 1]}px`,
        height: `${sizes[index - 1]}px`,
        animationDelay: `${delays[index - 1]}s`,
      };
    },

    showToast(type, title, message) {
      if (this.toastTimer) clearTimeout(this.toastTimer);
      this.toast = { show: true, type, title, message };
      this.toastTimer = setTimeout(() => (this.toast.show = false), 2500);
    },

    makeInitials(fullName) {
      return (fullName || "")
        .split(" ")
        .filter(Boolean)
        .slice(0, 2)
        .map((w) => w[0].toUpperCase())
        .join("");
    },

    formatJoinDate(dateStr) {
      if (!dateStr) return "";
      const d = new Date(dateStr);
      if (isNaN(d.getTime())) return "";
      return d.toLocaleString("en-US", { month: "short", year: "numeric" });
    },

    prettifyRole(role) {
      const map = {
        CITIZEN: "Citizen",
        PROVINCIAL_ADMIN: "Provincial Admin",
        MUNICIPAL_ADMIN: "Municipal Admin",
        RESPONSE_TEAM: "Response Team",
        EVAC_CENTER_STAFF: "Evac Center Staff",
      };
      return map[role] || role || "";
    },

    // ---------- Data ----------
async loadProfile() {
  try {
    const res = await api.get("user/profile/");
    const u = res?.data || {};

    const fullName = `${u.first_name || ""} ${u.last_name || ""}`.trim();

    // header data
    this.user.name = fullName || "User";
    this.user.email = u.email || "";
    this.user.initials = this.makeInitials(this.user.name);

    // ✅ use created_at (not date_joined)
    this.user.joinDate = this.formatJoinDate(u.created_at || u.createdAt);

    // ✅ inputs (what your textfields bind to)
    this.personalForm.name = this.user.name;
    this.personalForm.email = this.user.email;
    this.personalForm.phone = u.contact_number || u.contactNumber || "";

  } catch (err) {
    console.error("Profile load failed:", err?.response?.data || err);
  }
},

    // ---------- Avatar (preview only) ----------
    triggerAvatarUpload() {
      this.$refs.avatarInput?.click();
    },

    handleAvatarUpload(event) {
      const file = event.target.files?.[0];
      if (!file) return;

      const reader = new FileReader();
      reader.onload = (e) => {
        this.user.avatar = e.target.result;
        this.showToast("success", "Avatar updated", "Preview saved on this device.");
      };
      reader.readAsDataURL(file);
    },

    // ---------- Editing ----------
    toggleEdit() {
      if (this.editingPersonal) {
        this.savePersonalInfo();
      } else {
        // snapshot before editing
        this.personalOriginal = JSON.parse(JSON.stringify(this.personalForm));
        this.editingPersonal = true;
        // tiny delight
        this.showToast("success", "Edit mode", "You can update your info now.");
      }
    },

    cancelEdits() {
      if (this.personalOriginal) {
        this.personalForm = JSON.parse(JSON.stringify(this.personalOriginal));
      }
      this.editingPersonal = false;
      this.showToast("success", "Cancelled", "Changes were discarded.");
    },

    async savePersonalInfo() {
      if (this.loading) return;
      this.loading = true;

      try {
        // Minimal safe payload: only fields you likely have on CustomUser
        // You said you don't want to affect other aspects—so we only PATCH what we control.
        const payload = {
          contact_number: this.personalForm.phone || "",
          // If you later add these fields in backend, uncomment:
          // address: this.personalForm.address || "",
          // emergency_contact_name: this.personalForm.emergencyContact.name || "",
          // emergency_contact_phone: this.personalForm.emergencyContact.phone || "",
          // emergency_contact_relationship: this.personalForm.emergencyContact.relationship || "",
        };

        // If you don't have PATCH endpoint yet, this will fail but the UI will not break.
        // Add a simple endpoint later: user/profile/ PATCH.
        await api.patch("user/profile/", payload);

        // reflect header
        this.user.name = this.personalForm.name || this.user.name;

        this.editingPersonal = false;
        this.personalOriginal = JSON.parse(JSON.stringify(this.personalForm));
        this.showToast("success", "Saved", "Your profile has been updated.");
      } catch (e) {
        console.error("Save failed:", e?.response?.data || e);
        this.showToast("error", "Save failed", "Please check your endpoint or fields.");
      } finally {
        this.loading = false;
      }
    },

    async copyEmail() {
      try {
        await navigator.clipboard.writeText(this.user.email || "");
        this.showToast("success", "Copied", "Email copied to clipboard.");
      } catch (e) {
        this.showToast("error", "Copy failed", "Your browser blocked clipboard access.");
      }
    },
  },
};
</script>

<style scoped>
.user-profile {
  min-height: 100vh;
  background: radial-gradient(1000px 600px at 20% 10%, rgba(0, 150, 255, 0.15), transparent 60%),
              radial-gradient(900px 500px at 80% 30%, rgba(120, 70, 255, 0.12), transparent 55%),
              linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);
  color: white;
}

/* Header */
.profile-header {
  position: relative;
  padding: 44px 20px 26px;
  background: rgba(15, 15, 20, 0.88);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  overflow: hidden;
}

.header-background {
  position: absolute;
  inset: 0;
  z-index: 0;
}

.animated-shapes {
  position: relative;
  width: 100%;
  height: 100%;
}

.shape {
  position: absolute;
  background: radial-gradient(circle, rgba(0, 150, 255, 0.12) 0%, transparent 70%);
  border-radius: 50%;
  animation: float 6s ease-in-out infinite;
  filter: blur(0.2px);
}

.shape:nth-child(1) { top: 10%; left: 5%; }
.shape:nth-child(2) { top: 20%; right: 10%; }
.shape:nth-child(3) { bottom: 30%; left: 15%; }
.shape:nth-child(4) { bottom: 20%; right: 5%; }
.shape:nth-child(5) { top: 50%; left: 50%; transform: translate(-50%, -50%); }

@keyframes float {
  0%, 100% { transform: translateY(0) scale(1); }
  50% { transform: translateY(-18px) scale(1.08); }
}

.header-content {
  position: relative;
  z-index: 1;
  max-width: 1100px;
  margin: 0 auto;
}

.avatar-section {
  display: grid;
  grid-template-columns: 1fr;
  gap: 18px;
}

.avatar-container {
  position: relative;
  width: 120px;
}

.profile-avatar {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: linear-gradient(135deg, #0096ff, #0066cc);
  display: grid;
  place-items: center;
  font-size: 36px;
  font-weight: 800;
  color: white;
  border: 4px solid rgba(255, 255, 255, 0.18);
  box-shadow: 0 18px 40px rgba(0, 0, 0, 0.35);
  user-select: none;
}

.profile-avatar.default {
  background: linear-gradient(135deg, #0096ff, #0066cc);
}

.avatar-edit-btn {
  position: absolute;
  bottom: 6px;
  right: -6px;
  width: 38px;
  height: 38px;
  background: rgba(0, 150, 255, 0.95);
  border: none;
  border-radius: 50%;
  color: white;
  cursor: pointer;
  display: grid;
  place-items: center;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.avatar-edit-btn:hover {
  transform: translateY(-1px) scale(1.06);
  box-shadow: 0 10px 22px rgba(0, 150, 255, 0.35);
}

.avatar-info {
  display: grid;
  gap: 10px;
}

.user-name {
  font-size: 34px;
  margin: 0;
  background: linear-gradient(90deg, #ffffff, #0096ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.user-email {
  color: #9aa0a6;
  font-size: 15px;
  margin: 0;
}

.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.chip {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 7px 12px;
  border-radius: 999px;
  background: rgba(40, 40, 55, 0.55);
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: #c8cbd0;
  font-size: 13px;
}

.header-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-top: 4px;
}

/* Mini summary */
.mini-summary {
  margin-top: 22px;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.summary-item {
  background: rgba(35, 35, 48, 0.55);
  border: 1px solid rgba(100, 100, 120, 0.18);
  border-radius: 14px;
  padding: 14px 14px;
  transition: transform 0.2s ease, border-color 0.2s ease;
}

.summary-item:hover {
  transform: translateY(-2px);
  border-color: rgba(0, 150, 255, 0.45);
}

.summary-item.glow {
  border-color: rgba(255, 170, 0, 0.45);
}

.summary-title {
  color: #9aa0a6;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 6px;
}

.summary-value {
  font-size: 14px;
  color: #e7eaee;
  display: flex;
  align-items: center;
  gap: 8px;
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #00cc66;
}
.dot.warn { background: #ffaa00; }
.dot.ok { background: #00cc66; }

/* Content */
.profile-content {
  max-width: 1100px;
  margin: 0 auto;
  padding: 34px 20px 50px;
}

.profile-tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 22px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  padding-bottom: 10px;
}

.tab-btn {
  background: rgba(0, 150, 255, 0.16);
  border: 1px solid rgba(0, 150, 255, 0.35);
  color: #8fd0ff;
  padding: 12px 16px;
  border-radius: 12px;
  cursor: default;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
}

.tab-content {
  min-height: 320px;
}

.tab-panel {
  animation: fadeIn 0.45s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(14px); }
  to { opacity: 1; transform: translateY(0); }
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 18px;
  padding-bottom: 14px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.panel-header h3 {
  color: white;
  font-size: 22px;
  margin: 0;
}

.panel-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

/* Form */
.info-form {
  background: rgba(30, 30, 40, 0.78);
  border-radius: 18px;
  padding: 26px;
  border: 1px solid rgba(100, 100, 120, 0.18);
  box-shadow: 0 20px 60px rgba(0,0,0,0.25);
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.input-group.full-width {
  grid-column: 1 / -1;
}

.input-group label {
  color: #d6d9de;
  font-size: 13px;
  font-weight: 600;
}

.input-group input {
  padding: 14px 14px;
  background: rgba(40, 40, 50, 0.78);
  border: 1px solid rgba(100, 100, 120, 0.28);
  border-radius: 12px;
  color: white;
  font-size: 15px;
  transition: border-color 0.2s ease, box-shadow 0.2s ease, transform 0.08s ease;
}

.input-group input:focus {
  outline: none;
  border-color: rgba(0, 150, 255, 0.75);
  box-shadow: 0 0 0 3px rgba(0, 150, 255, 0.18);
}

.input-group input:active {
  transform: scale(0.995);
}

.input-group input.editable {
  background: rgba(52, 52, 68, 0.82);
  border-color: rgba(0, 150, 255, 0.55);
}

.input-group input.readonly {
  opacity: 0.9;
  cursor: not-allowed;
}

.hint {
  color: #8a9098;
  font-size: 12px;
}

.emergency-contact {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.save-row {
  display: flex;
  justify-content: flex-end;
  margin-top: 18px;
}

/* Buttons */
.edit-btn {
  background: rgba(0, 150, 255, 0.18);
  border: 1px solid rgba(0, 150, 255, 0.6);
  color: #8fd0ff;
  padding: 10px 14px;
  border-radius: 10px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: transform 0.16s ease, background 0.2s ease, box-shadow 0.2s ease;
  font-size: 14px;
  font-weight: 600;
}

.edit-btn:hover {
  background: rgba(0, 150, 255, 0.32);
  box-shadow: 0 10px 22px rgba(0, 150, 255, 0.18);
  transform: translateY(-1px);
}

.primary-btn {
  background: linear-gradient(135deg, #0096ff, #0066cc);
  border: none;
  color: white;
  padding: 12px 16px;
  border-radius: 12px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: transform 0.16s ease, box-shadow 0.2s ease;
  font-weight: 700;
}

.primary-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 16px 30px rgba(0, 150, 255, 0.25);
}

.primary-btn.small {
  padding: 10px 14px;
  border-radius: 10px;
  font-size: 14px;
}

.ghost-btn {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #d5d9de;
  padding: 10px 14px;
  border-radius: 10px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: border-color 0.2s ease, background 0.2s ease, transform 0.16s ease;
  font-weight: 600;
}

.ghost-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.06);
  border-color: rgba(0, 150, 255, 0.3);
  transform: translateY(-1px);
}

.ghost-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Toast */
.toast {
  position: fixed;
  right: 18px;
  bottom: 18px;
  width: min(360px, calc(100% - 36px));
  background: rgba(20, 20, 28, 0.92);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-left: 4px solid rgba(0, 150, 255, 0.9);
  border-radius: 14px;
  padding: 12px 14px;
  z-index: 1200;
  box-shadow: 0 20px 60px rgba(0,0,0,0.35);
}

.toast.success { border-left-color: rgba(0, 204, 102, 0.95); }
.toast.error { border-left-color: rgba(255, 107, 107, 0.95); }

.toast-title {
  font-weight: 800;
  margin-bottom: 4px;
}

.toast-msg {
  color: #b8bcc2;
  font-size: 13px;
}

/* Loading overlay */
.loading-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.78);
  backdrop-filter: blur(10px);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 1100;
  color: white;
}

.loading-spinner {
  width: 54px;
  height: 54px;
  border: 4px solid rgba(255, 255, 255, 0.22);
  border-top: 4px solid rgba(0, 150, 255, 0.95);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 14px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Transitions */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.22s ease, transform 0.22s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
  transform: translateY(10px);
}

/* Responsive */
@media (max-width: 900px) {
  .mini-summary {
    grid-template-columns: 1fr;
  }
  .form-grid {
    grid-template-columns: 1fr;
  }
  .emergency-contact {
    grid-template-columns: 1fr;
  }
  .avatar-section {
    gap: 14px;
  }
}

/* Icon placeholders */
.icon-camera::before { content: "📷"; }
.icon-calendar::before { content: "📅"; }
.icon-user::before { content: "👤"; }
.icon-edit::before { content: "✏️"; }
.icon-save::before { content: "💾"; }
.icon-location::before { content: "📍"; }
.icon-copy::before { content: "📋"; }
</style>