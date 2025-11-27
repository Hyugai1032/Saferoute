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
            <button class="avatar-edit-btn" @click="triggerAvatarUpload">
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
            <h1 class="user-name">{{ user.name }}</h1>
            <p class="user-email">{{ user.email }}</p>
            <div class="member-since">
              <i class="icon-calendar"></i>
              Member since {{ user.joinDate }}
            </div>
          </div>
        </div>

        <!-- Quick Stats -->
        <div class="profile-stats">
          <div class="stat-card">
            <div class="stat-icon">
              <i class="icon-reports"></i>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ user.stats.reports }}</div>
              <div class="stat-label">Reports Submitted</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">
              <i class="icon-verified"></i>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ user.stats.verified }}</div>
              <div class="stat-label">Verified</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">
              <i class="icon-resolved"></i>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ user.stats.resolved }}</div>
              <div class="stat-label">Resolved</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Profile Content -->
    <div class="profile-content">
      <!-- Navigation Tabs -->
      <div class="profile-tabs">
        <button 
          v-for="tab in tabs" 
          :key="tab.id"
          :class="['tab-btn', { active: activeTab === tab.id }]"
          @click="activeTab = tab.id"
        >
          <i :class="tab.icon"></i>
          {{ tab.name }}
          <span v-if="tab.count" class="tab-count">{{ tab.count }}</span>
        </button>
      </div>

      <!-- Tab Content -->
      <div class="tab-content">
        <!-- Personal Information -->
        <transition name="fade">
          <div v-if="activeTab === 'personal'" class="tab-panel personal-info">
            <div class="panel-header">
              <h3>Personal Information</h3>
              <button class="edit-btn" @click="editPersonalInfo">
                <i class="icon-edit"></i>
                {{ editingPersonal ? 'Save Changes' : 'Edit Information' }}
              </button>
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
                  >
                </div>
                <div class="input-group">
                  <label>Email Address</label>
                  <input 
                    type="email" 
                    v-model="personalForm.email"
                    :readonly="!editingPersonal"
                    :class="{ editable: editingPersonal }"
                  >
                </div>
                <div class="input-group">
                  <label>Phone Number</label>
                  <input 
                    type="tel" 
                    v-model="personalForm.phone"
                    :readonly="!editingPersonal"
                    :class="{ editable: editingPersonal }"
                  >
                </div>
                <div class="input-group">
                  <label>Address</label>
                  <input 
                    type="text" 
                    v-model="personalForm.address"
                    :readonly="!editingPersonal"
                    :class="{ editable: editingPersonal }"
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
            </form>
          </div>
        </transition>

        <!-- Report History -->
        <transition name="fade">
          <div v-if="activeTab === 'reports'" class="tab-panel report-history">
            <div class="panel-header">
              <h3>Report History</h3>
              <div class="history-filters">
                <select v-model="reportFilter" class="filter-select">
                  <option value="all">All Reports</option>
                  <option value="pending">Pending</option>
                  <option value="verified">Verified</option>
                  <option value="resolved">Resolved</option>
                </select>
              </div>
            </div>
            
            <div class="reports-list">
              <div 
                v-for="report in filteredReports" 
                :key="report.id"
                :class="['report-card', report.status]"
              >
                <div class="report-header">
                  <div class="report-type">
                    <i :class="report.icon"></i>
                    {{ report.type }}
                  </div>
                  <div class="report-status" :class="report.status">
                    {{ report.status }}
                  </div>
                </div>
                <div class="report-content">
                  <h4>{{ report.title }}</h4>
                  <p>{{ report.description }}</p>
                  <div class="report-meta">
                    <span class="report-location">
                      <i class="icon-location"></i>
                      {{ report.location }}
                    </span>
                    <span class="report-date">
                      <i class="icon-calendar"></i>
                      {{ report.date }}
                    </span>
                  </div>
                </div>
                <div class="report-actions">
                  <button class="action-btn" @click="viewReport(report)">
                    <i class="icon-view"></i>
                    View
                  </button>
                  <button 
                    v-if="report.status === 'pending'" 
                    class="action-btn"
                    @click="editReport(report)"
                  >
                    <i class="icon-edit"></i>
                    Edit
                  </button>
                  <button 
                    v-if="report.status === 'pending'" 
                    class="action-btn danger"
                    @click="deleteReport(report)"
                  >
                    <i class="icon-delete"></i>
                    Delete
                  </button>
                </div>
              </div>
              
              <!-- Empty State -->
              <div v-if="filteredReports.length === 0" class="empty-state">
                <i class="icon-empty-reports"></i>
                <h4>No reports found</h4>
                <p>You haven't submitted any {{ reportFilter !== 'all' ? reportFilter : '' }} reports yet</p>
                <button class="primary-btn" @click="$router.push('/user/report')">
                  <i class="icon-add"></i>
                  Submit Your First Report
                </button>
              </div>
            </div>
          </div>
        </transition>

        <!-- Notification Settings -->
        <transition name="fade">
          <div v-if="activeTab === 'notifications'" class="tab-panel notification-settings">
            <div class="panel-header">
              <h3>Notification Preferences</h3>
              <button class="save-btn" @click="saveNotificationSettings">
                <i class="icon-save"></i>
                Save Settings
              </button>
            </div>
            
            <div class="notification-categories">
              <div class="category-group">
                <h4>Alert Types</h4>
                <div class="preference-list">
                  <div 
                    v-for="pref in notificationPreferences" 
                    :key="pref.id"
                    class="preference-item"
                  >
                    <div class="preference-info">
                      <i :class="pref.icon"></i>
                      <div>
                        <div class="preference-title">{{ pref.title }}</div>
                        <div class="preference-desc">{{ pref.description }}</div>
                      </div>
                    </div>
                    <label class="switch">
                      <input type="checkbox" v-model="pref.enabled">
                      <span class="slider"></span>
                    </label>
                  </div>
                </div>
              </div>
              
              <div class="category-group">
                <h4>Delivery Methods</h4>
                <div class="delivery-methods">
                  <div class="method-item">
                    <div class="method-info">
                      <i class="icon-push"></i>
                      <div>
                        <div class="method-title">Push Notifications</div>
                        <div class="method-desc">Receive alerts on this device</div>
                      </div>
                    </div>
                    <label class="switch">
                      <input type="checkbox" v-model="deliveryMethods.push">
                      <span class="slider"></span>
                    </label>
                  </div>
                  <div class="method-item">
                    <div class="method-info">
                      <i class="icon-email"></i>
                      <div>
                        <div class="method-title">Email Notifications</div>
                        <div class="method-desc">Receive alerts via email</div>
                      </div>
                    </div>
                    <label class="switch">
                      <input type="checkbox" v-model="deliveryMethods.email">
                      <span class="slider"></span>
                    </label>
                  </div>
                  <div class="method-item">
                    <div class="method-info">
                      <i class="icon-sms"></i>
                      <div>
                        <div class="method-title">SMS Alerts</div>
                        <div class="method-desc">Receive critical alerts via SMS</div>
                      </div>
                    </div>
                    <label class="switch">
                      <input type="checkbox" v-model="deliveryMethods.sms">
                      <span class="slider"></span>
                    </label>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </transition>

        <!-- Account Settings -->
        <transition name="fade">
          <div v-if="activeTab === 'account'" class="tab-panel account-settings">
            <div class="panel-header">
              <h3>Account Security</h3>
            </div>
            
            <div class="security-settings">
              <div class="security-item">
                <div class="security-info">
                  <i class="icon-password"></i>
                  <div>
                    <div class="security-title">Password</div>
                    <div class="security-desc">Last changed 30 days ago</div>
                  </div>
                </div>
                <button class="action-btn" @click="changePassword">
                  Change Password
                </button>
              </div>
              
              <div class="security-item">
                <div class="security-info">
                  <i class="icon-2fa"></i>
                  <div>
                    <div class="security-title">Two-Factor Authentication</div>
                    <div class="security-desc">Add an extra layer of security</div>
                  </div>
                </div>
                <label class="switch">
                  <input type="checkbox" v-model="securitySettings.twoFactor">
                  <span class="slider"></span>
                </label>
              </div>
              
              <div class="security-item">
                <div class="security-info">
                  <i class="icon-sessions"></i>
                  <div>
                    <div class="security-title">Active Sessions</div>
                    <div class="security-desc">Manage your logged-in devices</div>
                  </div>
                </div>
                <button class="action-btn" @click="viewSessions">
                  View Sessions
                </button>
              </div>
            </div>
            
            <div class="danger-zone">
              <h4>Danger Zone</h4>
              <div class="danger-actions">
                <button class="danger-btn" @click="exportData">
                  <i class="icon-export"></i>
                  Export My Data
                </button>
                <button class="danger-btn critical" @click="deleteAccount">
                  <i class="icon-delete"></i>
                  Delete Account
                </button>
              </div>
            </div>
          </div>
        </transition>
      </div>
    </div>

    <!-- Loading Overlay -->
    <transition name="fade">
      <div v-if="loading" class="loading-overlay">
        <div class="loading-spinner"></div>
        <p>Saving changes...</p>
      </div>
    </transition>
  </div>
</template>

<script>
export default {
  name: 'UserProfile',
  data() {
    return {
      activeTab: 'personal',
      editingPersonal: false,
      loading: false,
      reportFilter: 'all',
      user: {
        name: 'John Doe',
        email: 'john.doe@example.com',
        initials: 'JD',
        joinDate: 'Jan 2024',
        avatar: null,
        stats: {
          reports: 12,
          verified: 8,
          resolved: 5
        }
      },
      personalForm: {
        name: 'John Doe',
        email: 'john.doe@example.com',
        phone: '+1 (555) 123-4567',
        address: '123 Main Street, Downtown',
        emergencyContact: {
          name: 'Jane Doe',
          phone: '+1 (555) 987-6543',
          relationship: 'Spouse'
        }
      },
      tabs: [
        { id: 'personal', name: 'Personal Info', icon: 'icon-user', count: null },
        { id: 'reports', name: 'Report History', icon: 'icon-history', count: 12 },
        { id: 'notifications', name: 'Notifications', icon: 'icon-bell', count: null },
        { id: 'account', name: 'Account', icon: 'icon-security', count: null }
      ],
      reports: [
        {
          id: 1,
          type: 'Flood',
          icon: 'icon-flood',
          title: 'Flooded Intersection',
          description: 'Heavy flooding at Main St and 5th Ave intersection',
          location: 'Main Street',
          date: '2024-11-15',
          status: 'verified'
        },
        {
          id: 2,
          type: 'Fallen Tree',
          icon: 'icon-tree',
          title: 'Large Tree Blocking Road',
          description: 'Tree fell during storm, blocking entire roadway',
          location: 'Oak Avenue',
          date: '2024-11-14',
          status: 'resolved'
        },
        {
          id: 3,
          type: 'Power Outage',
          icon: 'icon-power',
          title: 'Street Lights Out',
          description: 'Multiple street lights not working in residential area',
          location: 'Maple Street',
          date: '2024-11-13',
          status: 'pending'
        }
      ],
      notificationPreferences: [
        {
          id: 'emergency',
          title: 'Emergency Alerts',
          description: 'Critical alerts requiring immediate action',
          icon: 'icon-emergency',
          enabled: true
        },
        {
          id: 'weather',
          title: 'Weather Warnings',
          description: 'Severe weather alerts and updates',
          icon: 'icon-weather',
          enabled: true
        },
        {
          id: 'traffic',
          title: 'Traffic Updates',
          description: 'Road closures and traffic disruptions',
          icon: 'icon-traffic',
          enabled: false
        },
        {
          id: 'safety',
          title: 'Safety Advisories',
          description: 'General safety information and tips',
          icon: 'icon-safety',
          enabled: true
        }
      ],
      deliveryMethods: {
        push: true,
        email: true,
        sms: false
      },
      securitySettings: {
        twoFactor: false
      }
    }
  },
  computed: {
    filteredReports() {
      if (this.reportFilter === 'all') return this.reports
      return this.reports.filter(report => report.status === this.reportFilter)
    }
  },
  methods: {
    getShapeStyle(index) {
      const sizes = [80, 120, 100, 150, 90]
      const delays = [0, 1, 2, 0.5, 1.5]
      return {
        width: `${sizes[index - 1]}px`,
        height: `${sizes[index - 1]}px`,
        animationDelay: `${delays[index - 1]}s`
      }
    },
    triggerAvatarUpload() {
      this.$refs.avatarInput.click()
    },
    handleAvatarUpload(event) {
      const file = event.target.files[0]
      if (file) {
        // In a real app, you would upload the file to a server
        const reader = new FileReader()
        reader.onload = (e) => {
          this.user.avatar = e.target.result
        }
        reader.readAsDataURL(file)
      }
    },
    editPersonalInfo() {
      if (this.editingPersonal) {
        this.savePersonalInfo()
      } else {
        this.editingPersonal = true
      }
    },
    async savePersonalInfo() {
      this.loading = true
      try {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1500))
        this.user.name = this.personalForm.name
        this.user.email = this.personalForm.email
        this.editingPersonal = false
        // Show success message
        this.$notify({
          title: 'Profile Updated',
          message: 'Your personal information has been updated successfully.',
          type: 'success'
        })
      } catch (error) {
        console.error('Error saving profile:', error)
      } finally {
        this.loading = false
      }
    },
    viewReport(report) {
      console.log('Viewing report:', report)
      // Navigate to report detail view
    },
    editReport(report) {
      console.log('Editing report:', report)
      // Navigate to report editing
    },
    deleteReport(report) {
      if (confirm('Are you sure you want to delete this report?')) {
        this.reports = this.reports.filter(r => r.id !== report.id)
      }
    },
    async saveNotificationSettings() {
      this.loading = true
      try {
        await new Promise(resolve => setTimeout(resolve, 1000))
        this.$notify({
          title: 'Settings Saved',
          message: 'Your notification preferences have been updated.',
          type: 'success'
        })
      } catch (error) {
        console.error('Error saving settings:', error)
      } finally {
        this.loading = false
      }
    },
    changePassword() {
      // Implement password change flow
      console.log('Changing password...')
    },
    viewSessions() {
      // Implement session management
      console.log('Viewing sessions...')
    },
    exportData() {
      // Implement data export
      console.log('Exporting data...')
    },
    deleteAccount() {
      if (confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
        console.log('Deleting account...')
      }
    }
  }
}
</script>

<style scoped>
.user-profile {
  min-height: 100vh;
  background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);
  color: white;
}

.profile-header {
  position: relative;
  padding: 40px 20px;
  background: rgba(15, 15, 20, 0.9);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  overflow: hidden;
}

.header-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
}

.animated-shapes {
  position: relative;
  width: 100%;
  height: 100%;
}

.shape {
  position: absolute;
  background: radial-gradient(circle, rgba(0, 150, 255, 0.1) 0%, transparent 70%);
  border-radius: 50%;
  animation: float 6s ease-in-out infinite;
}

.shape:nth-child(1) { top: 10%; left: 5%; }
.shape:nth-child(2) { top: 20%; right: 10%; }
.shape:nth-child(3) { bottom: 30%; left: 15%; }
.shape:nth-child(4) { bottom: 20%; right: 5%; }
.shape:nth-child(5) { top: 50%; left: 50%; transform: translate(-50%, -50%); }

@keyframes float {
  0%, 100% { transform: translateY(0) scale(1); }
  50% { transform: translateY(-20px) scale(1.1); }
}

.header-content {
  position: relative;
  z-index: 1;
  max-width: 1200px;
  margin: 0 auto;
}

.avatar-section {
  display: flex;
  align-items: center;
  gap: 30px;
  margin-bottom: 40px;
}

.avatar-container {
  position: relative;
}

.profile-avatar {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: linear-gradient(135deg, #0096ff, #0066cc);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36px;
  font-weight: 700;
  color: white;
  border: 4px solid rgba(255, 255, 255, 0.2);
}

.profile-avatar.default {
  background: linear-gradient(135deg, #0096ff, #0066cc);
}

.avatar-edit-btn {
  position: absolute;
  bottom: 5px;
  right: 5px;
  width: 36px;
  height: 36px;
  background: #0096ff;
  border: none;
  border-radius: 50%;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.avatar-edit-btn:hover {
  transform: scale(1.1);
  box-shadow: 0 5px 15px rgba(0, 150, 255, 0.4);
}

.avatar-info h1 {
  font-size: 32px;
  margin-bottom: 5px;
  background: linear-gradient(90deg, #ffffff, #0096ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.avatar-info .user-email {
  color: #888;
  font-size: 16px;
  margin-bottom: 10px;
}

.member-since {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #666;
  font-size: 14px;
}

.profile-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.stat-card {
  background: rgba(40, 40, 50, 0.8);
  border-radius: 15px;
  padding: 25px;
  display: flex;
  align-items: center;
  gap: 20px;
  transition: all 0.3s ease;
  border: 1px solid rgba(100, 100, 120, 0.2);
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.3);
  border-color: #0096ff;
}

.stat-icon {
  width: 60px;
  height: 60px;
  background: rgba(0, 150, 255, 0.2);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.stat-info .stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #0096ff;
  margin-bottom: 5px;
}

.stat-info .stat-label {
  color: #888;
  font-size: 14px;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.profile-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
}

.profile-tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 40px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding-bottom: 10px;
  overflow-x: auto;
}

.tab-btn {
  background: transparent;
  border: none;
  color: #888;
  padding: 15px 25px;
  border-radius: 10px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 10px;
  transition: all 0.3s ease;
  white-space: nowrap;
  font-size: 14px;
  position: relative;
}

.tab-btn.active {
  background: rgba(0, 150, 255, 0.2);
  color: #0096ff;
}

.tab-btn:hover:not(.active) {
  background: rgba(255, 255, 255, 0.05);
  color: #ddd;
}

.tab-count {
  background: rgba(0, 150, 255, 0.3);
  color: #0096ff;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 600;
}

.tab-content {
  min-height: 400px;
}

.tab-panel {
  animation: fadeIn 0.5s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.panel-header h3 {
  color: white;
  font-size: 24px;
  margin: 0;
}

.edit-btn,
.save-btn {
  background: rgba(0, 150, 255, 0.2);
  border: 1px solid #0096ff;
  color: #0096ff;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
  font-size: 14px;
}

.edit-btn:hover,
.save-btn:hover {
  background: #0096ff;
  color: white;
}

.info-form {
  background: rgba(30, 30, 40, 0.8);
  border-radius: 15px;
  padding: 30px;
  border: 1px solid rgba(100, 100, 120, 0.2);
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.input-group {
  display: flex;
  flex-direction: column;
}

.input-group.full-width {
  grid-column: 1 / -1;
}

.input-group label {
  color: #ddd;
  font-size: 14px;
  margin-bottom: 8px;
  font-weight: 500;
}

.input-group input {
  padding: 15px;
  background: rgba(40, 40, 50, 0.8);
  border: 1px solid rgba(100, 100, 120, 0.3);
  border-radius: 10px;
  color: white;
  font-size: 16px;
  transition: all 0.3s ease;
}

.input-group input:focus {
  outline: none;
  border-color: #0096ff;
  box-shadow: 0 0 0 2px rgba(0, 150, 255, 0.2);
}

.input-group input.editable {
  background: rgba(50, 50, 60, 0.8);
  border-color: #0096ff;
}

.emergency-contact {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.reports-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.report-card {
  background: rgba(30, 30, 40, 0.8);
  border-radius: 15px;
  padding: 25px;
  border-left: 4px solid #0096ff;
  transition: all 0.3s ease;
}

.report-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.report-card.verified {
  border-left-color: #00cc66;
}

.report-card.resolved {
  border-left-color: #0096ff;
}

.report-card.pending {
  border-left-color: #ffaa00;
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.report-type {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #0096ff;
  font-weight: 600;
  font-size: 14px;
}

.report-status {
  padding: 6px 12px;
  border-radius: 15px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
}

.report-status.pending {
  background: rgba(255, 170, 0, 0.2);
  color: #ffaa00;
}

.report-status.verified {
  background: rgba(0, 204, 102, 0.2);
  color: #00cc66;
}

.report-status.resolved {
  background: rgba(0, 150, 255, 0.2);
  color: #0096ff;
}

.report-content h4 {
  color: white;
  margin-bottom: 10px;
  font-size: 18px;
}

.report-content p {
  color: #aaa;
  margin-bottom: 15px;
  line-height: 1.5;
}

.report-meta {
  display: flex;
  gap: 20px;
  font-size: 14px;
  color: #666;
}

.report-meta span {
  display: flex;
  align-items: center;
  gap: 6px;
}

.report-actions {
  display: flex;
  gap: 10px;
  margin-top: 15px;
}

.action-btn {
  background: rgba(60, 60, 70, 0.8);
  border: 1px solid rgba(100, 100, 120, 0.3);
  color: #ddd;
  padding: 8px 16px;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.3s ease;
  font-size: 12px;
}

.action-btn:hover {
  background: rgba(0, 150, 255, 0.2);
  border-color: #0096ff;
  color: #0096ff;
}

.action-btn.danger {
  border-color: #ff6b6b;
  color: #ff6b6b;
}

.action-btn.danger:hover {
  background: rgba(255, 107, 107, 0.2);
}

.primary-btn {
  background: linear-gradient(135deg, #0096ff, #0066cc);
  border: none;
  color: white;
  padding: 12px 24px;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
  font-weight: 600;
}

.primary-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(0, 150, 255, 0.3);
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #666;
}

.empty-state i {
  font-size: 64px;
  margin-bottom: 20px;
  display: block;
  opacity: 0.5;
}

.empty-state h4 {
  color: #888;
  margin-bottom: 10px;
}

.empty-state p {
  margin-bottom: 20px;
}

.notification-categories {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.category-group h4 {
  color: white;
  margin-bottom: 20px;
  font-size: 18px;
  border-bottom: 2px solid rgba(0, 150, 255, 0.3);
  padding-bottom: 10px;
}

.preference-list,
.delivery-methods,
.security-settings {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.preference-item,
.method-item,
.security-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: rgba(40, 40, 50, 0.8);
  border-radius: 12px;
  border: 1px solid rgba(100, 100, 120, 0.2);
}

.preference-info,
.method-info,
.security-info {
  display: flex;
  align-items: center;
  gap: 15px;
  flex: 1;
}

.preference-info i,
.method-info i,
.security-info i {
  width: 40px;
  height: 40px;
  background: rgba(0, 150, 255, 0.2);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  flex-shrink: 0;
}

.preference-title,
.method-title,
.security-title {
  color: white;
  font-weight: 600;
  margin-bottom: 4px;
}

.preference-desc,
.method-desc,
.security-desc {
  color: #888;
  font-size: 14px;
}

.switch {
  position: relative;
  display: inline-block;
  width: 50px;
  height: 24px;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #444;
  transition: .4s;
  border-radius: 24px;
}

.slider:before {
  position: absolute;
  content: "";
  height: 16px;
  width: 16px;
  left: 4px;
  bottom: 4px;
  background-color: white;
  transition: .4s;
  border-radius: 50%;
}

input:checked + .slider {
  background-color: #0096ff;
}

input:checked + .slider:before {
  transform: translateX(26px);
}

.danger-zone {
  margin-top: 40px;
  padding: 30px;
  background: rgba(255, 68, 68, 0.05);
  border: 1px solid rgba(255, 68, 68, 0.2);
  border-radius: 15px;
}

.danger-zone h4 {
  color: #ff4444;
  margin-bottom: 20px;
  font-size: 18px;
}

.danger-actions {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.danger-btn {
  background: rgba(60, 60, 70, 0.8);
  border: 1px solid rgba(100, 100, 120, 0.3);
  color: #ddd;
  padding: 12px 20px;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
}

.danger-btn:hover {
  background: rgba(255, 68, 68, 0.1);
  border-color: #ff4444;
  color: #ff4444;
}

.danger-btn.critical {
  background: rgba(255, 68, 68, 0.1);
  border-color: #ff4444;
  color: #ff4444;
}

.danger-btn.critical:hover {
  background: #ff4444;
  color: white;
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(10px);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  color: white;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-top: 4px solid #0096ff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Responsive Design */
@media (max-width: 768px) {
  .profile-header {
    padding: 30px 15px;
  }
  
  .avatar-section {
    flex-direction: column;
    text-align: center;
    gap: 20px;
  }
  
  .profile-stats {
    grid-template-columns: 1fr;
  }
  
  .profile-tabs {
    flex-wrap: wrap;
  }
  
  .tab-btn {
    flex: 1;
    min-width: 140px;
    justify-content: center;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .emergency-contact {
    grid-template-columns: 1fr;
  }
  
  .report-meta {
    flex-direction: column;
    gap: 10px;
  }
  
  .report-actions {
    flex-wrap: wrap;
  }
  
  .danger-actions {
    flex-direction: column;
  }
}

@media (max-width: 480px) {
  .panel-header {
    flex-direction: column;
    gap: 15px;
    align-items: flex-start;
  }
  
  .preference-item,
  .method-item,
  .security-item {
    flex-direction: column;
    gap: 15px;
    align-items: flex-start;
  }
}

/* Icon placeholders */
.icon-camera::before { content: "📷"; }
.icon-calendar::before { content: "📅"; }
.icon-reports::before { content: "📝"; }
.icon-verified::before { content: "✅"; }
.icon-resolved::before { content: "🏁"; }
.icon-user::before { content: "👤"; }
.icon-history::before { content: "📋"; }
.icon-bell::before { content: "🔔"; }
.icon-security::before { content: "🔒"; }
.icon-edit::before { content: "✏️"; }
.icon-location::before { content: "📍"; }
.icon-view::before { content: "👁️"; }
.icon-delete::before { content: "🗑️"; }
.icon-add::before { content: "➕"; }
.icon-save::before { content: "💾"; }
.icon-emergency::before { content: "🚨"; }
.icon-weather::before { content: "🌤️"; }
.icon-traffic::before { content: "🚧"; }
.icon-safety::before { content: "🛡️"; }
.icon-push::before { content: "📱"; }
.icon-email::before { content: "📧"; }
.icon-sms::before { content: "💬"; }
.icon-password::before { content: "🔑"; }
.icon-2fa::before { content: "⚡"; }
.icon-sessions::before { content: "💻"; }
.icon-export::before { content: "📤"; }
.icon-flood::before { content: "🌊"; }
.icon-tree::before { content: "🌳"; }
.icon-power::before { content: "⚡"; }
.icon-empty-reports::before { content: "📭"; }
</style>