<!-- src/views/Users/UserAlerts.vue -->
<template>
  <div class="user-alerts">
    <!-- Animated Header -->
    <div class="alerts-header">
      <div class="header-background">
        <div class="floating-alerts">
          <div v-for="i in 3" :key="i" class="floating-alert" :style="getFloatingStyle(i)"></div>
        </div>
      </div>
      <div class="header-content">
        <h1 class="alerts-title">Alerts & Advisories</h1>
        <p class="alerts-subtitle">Stay informed with real-time emergency updates</p>
        <div class="alert-stats">
          <div class="stat-item">
            <div class="stat-value">{{ activeAlerts }}</div>
            <div class="stat-label">Active Alerts</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ criticalAlerts }}</div>
            <div class="stat-label">Critical</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ todayAlerts }}</div>
            <div class="stat-label">Today</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="alerts-content">
      <!-- Notification Preferences -->
      <div class="preferences-card">
        <div class="preferences-header">
          <h3>Notification Preferences</h3>
          <button class="toggle-btn" @click="togglePreferences">
            <i class="icon-settings"></i>
            Settings
          </button>
        </div>
        <transition-expand>
          <div v-if="showPreferences" class="preferences-content">
            <div class="preference-item">
              <label>Push Notifications</label>
              <label class="switch">
                <input type="checkbox" v-model="preferences.push">
                <span class="slider"></span>
              </label>
            </div>
            <div class="preference-item">
              <label>Email Alerts</label>
              <label class="switch">
                <input type="checkbox" v-model="preferences.email">
                <span class="slider"></span>
              </label>
            </div>
            <div class="preference-item">
              <label>SMS Notifications</label>
              <label class="switch">
                <input type="checkbox" v-model="preferences.sms">
                <span class="slider"></span>
              </label>
            </div>
            <div class="preference-item">
              <label>Critical Alerts Only</label>
              <label class="switch">
                <input type="checkbox" v-model="preferences.criticalOnly">
                <span class="slider"></span>
              </label>
            </div>
          </div>
        </transition-expand>
      </div>

      <!-- Alert Filters -->
      <div class="filters-section">
        <div class="filter-tabs">
          <button 
            v-for="tab in filterTabs" 
            :key="tab.id"
            :class="['filter-tab', { active: activeFilter === tab.id }]"
            @click="activeFilter = tab.id"
          >
            <i :class="tab.icon"></i>
            {{ tab.name }}
            <span class="tab-count">{{ getFilterCount(tab.id) }}</span>
          </button>
        </div>
        <div class="search-box">
          <i class="icon-search"></i>
          <input 
            type="text" 
            v-model="searchQuery"
            placeholder="Search alerts..."
            class="search-input"
          >
        </div>
      </div>

      <!-- Alerts List -->
      <div class="alerts-list">
        <transition-group name="alert-item" tag="div">
          <div 
            v-for="alert in filteredAlerts" 
            :key="alert.id"
            :class="['alert-card', alert.priority, { unread: !alert.read }]"
            @click="selectAlert(alert)"
          >
            <div class="alert-icon">
              <i :class="alert.icon"></i>
              <div v-if="!alert.read" class="unread-indicator"></div>
            </div>
            <div class="alert-content">
              <div class="alert-header">
                <h4 class="alert-title">{{ alert.title }}</h4>
                <span class="alert-time">{{ alert.time }}</span>
              </div>
              <p class="alert-message">{{ alert.message }}</p>
              <div class="alert-meta">
                <span class="alert-source">{{ alert.source }}</span>
                <span class="alert-location">
                  <i class="icon-location"></i>
                  {{ alert.location }}
                </span>
              </div>
            </div>
            <div class="alert-actions">
              <button class="action-btn" @click.stop="toggleRead(alert)">
                <i :class="alert.read ? 'icon-unread' : 'icon-read'"></i>
              </button>
              <button class="action-btn" @click.stop="shareAlert(alert)">
                <i class="icon-share"></i>
              </button>
            </div>
          </div>
        </transition-group>
        
        <!-- Empty State -->
        <div v-if="filteredAlerts.length === 0" class="empty-state">
          <i class="icon-empty"></i>
          <h3>No alerts found</h3>
          <p>There are no {{ activeFilter }} alerts matching your search</p>
        </div>
      </div>
    </div>

    <!-- Selected Alert Modal -->
    <transition name="modal">
      <div v-if="selectedAlert" class="alert-modal">
        <div class="modal-backdrop" @click="selectedAlert = null"></div>
        <div class="modal-content">
          <div class="modal-header" :class="selectedAlert.priority">
            <div class="modal-title">
              <i :class="selectedAlert.icon"></i>
              <h2>{{ selectedAlert.title }}</h2>
            </div>
            <button class="close-btn" @click="selectedAlert = null">×</button>
          </div>
          <div class="modal-body">
            <div class="alert-details">
              <div class="detail-row">
                <span class="detail-label">Issued By:</span>
                <span class="detail-value">{{ selectedAlert.source }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">Location:</span>
                <span class="detail-value">{{ selectedAlert.location }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">Time:</span>
                <span class="detail-value">{{ selectedAlert.fullTime }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">Priority:</span>
                <span class="detail-value priority-badge" :class="selectedAlert.priority">
                  {{ selectedAlert.priority }}
                </span>
              </div>
            </div>
            <div class="alert-full-message">
              <h4>Full Message</h4>
              <p>{{ selectedAlert.fullMessage }}</p>
            </div>
            <div v-if="selectedAlert.instructions" class="alert-instructions">
              <h4>Recommended Actions</h4>
              <ul>
                <li v-for="(instruction, index) in selectedAlert.instructions" :key="index">
                  {{ instruction }}
                </li>
              </ul>
            </div>
            <div v-if="selectedAlert.affectedAreas" class="affected-areas">
              <h4>Affected Areas</h4>
              <div class="areas-list">
                <span 
                  v-for="area in selectedAlert.affectedAreas" 
                  :key="area"
                  class="area-tag"
                >
                  {{ area }}
                </span>
              </div>
            </div>
          </div>
          <div class="modal-actions">
            <button class="action-btn primary" @click="markAsRead(selectedAlert)">
              <i class="icon-read"></i>
              Mark as Read
            </button>
            <button class="action-btn" @click="shareAlert(selectedAlert)">
              <i class="icon-share"></i>
              Share Alert
            </button>
            <button class="action-btn" @click="saveAlert(selectedAlert)">
              <i class="icon-save"></i>
              Save
            </button>
          </div>
        </div>
      </div>
    </transition>

    <!-- Emergency Quick Actions -->
    <div class="emergency-actions">
      <button class="emergency-btn critical" @click="sendEmergencyAlert">
        <i class="icon-emergency"></i>
        Emergency Alert
      </button>
      <button class="emergency-btn" @click="refreshAlerts" :disabled="refreshing">
        <i class="icon-refresh" :class="{ spinning: refreshing }"></i>
        {{ refreshing ? 'Refreshing...' : 'Refresh' }}
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'UserAlerts',
  data() {
    return {
      activeFilter: 'all',
      searchQuery: '',
      showPreferences: false,
      selectedAlert: null,
      refreshing: false,
      activeAlerts: 8,
      criticalAlerts: 3,
      todayAlerts: 5,
      preferences: {
        push: true,
        email: true,
        sms: false,
        criticalOnly: false
      },
      filterTabs: [
        { id: 'all', name: 'All Alerts', icon: 'icon-all' },
        { id: 'critical', name: 'Critical', icon: 'icon-critical' },
        { id: 'weather', name: 'Weather', icon: 'icon-weather' },
        { id: 'safety', name: 'Safety', icon: 'icon-safety' },
        { id: 'traffic', name: 'Traffic', icon: 'icon-traffic' }
      ],
      alerts: [
        {
          id: 1,
          title: 'Flash Flood Warning',
          message: 'Heavy rainfall expected in your area for the next 3 hours',
          fullMessage: 'The National Weather Service has issued a Flash Flood Warning for your area. Heavy rainfall with intensities of 2-3 inches per hour is expected. Avoid low-lying areas and do not attempt to cross flooded roads.',
          priority: 'critical',
          icon: 'icon-flood',
          source: 'National Weather Service',
          location: 'Downtown Area',
          time: '10 min ago',
          fullTime: 'November 15, 2024 - 14:30 EST',
          read: false,
          instructions: [
            'Move to higher ground immediately',
            'Avoid walking or driving through flood waters',
            'Stay tuned to local news for updates',
            'Prepare evacuation kit'
          ],
          affectedAreas: ['Downtown', 'River District', 'East Park']
        },
        {
          id: 2,
          title: 'Evacuation Order Lifted',
          message: 'Previous evacuation order for North District has been lifted',
          fullMessage: 'The evacuation order for North District has been officially lifted. Residents can return to their homes. Emergency services are still monitoring the situation.',
          priority: 'info',
          icon: 'icon-info',
          source: 'Emergency Management',
          location: 'North District',
          time: '1 hour ago',
          fullTime: 'November 15, 2024 - 13:45 EST',
          read: true
        },
        {
          id: 3,
          title: 'Road Closure Update',
          message: 'Main Street closed due to fallen power lines',
          fullMessage: 'Main Street between 5th and 8th Avenue is closed until further notice due to fallen power lines. Use alternate routes. Utility crews are on site.',
          priority: 'high',
          icon: 'icon-traffic',
          source: 'Traffic Department',
          location: 'Main Street',
          time: '2 hours ago',
          fullTime: 'November 15, 2024 - 12:15 EST',
          read: false,
          affectedAreas: ['Main Street', 'Central Business District']
        }
        // More alerts would be here...
      ]
    }
  },
  computed: {
    filteredAlerts() {
      let filtered = this.alerts
      
      // Apply active filter
      if (this.activeFilter !== 'all') {
        filtered = filtered.filter(alert => alert.priority === this.activeFilter)
      }
      
      // Apply search query
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase()
        filtered = filtered.filter(alert => 
          alert.title.toLowerCase().includes(query) ||
          alert.message.toLowerCase().includes(query) ||
          alert.location.toLowerCase().includes(query)
        )
      }
      
      return filtered
    }
  },
  methods: {
    getFloatingStyle(index) {
      const delay = (index - 1) * 2
      return {
        animationDelay: `${delay}s`
      }
    },
    togglePreferences() {
      this.showPreferences = !this.showPreferences
    },
    getFilterCount(filterId) {
      if (filterId === 'all') return this.alerts.length
      return this.alerts.filter(alert => alert.priority === filterId).length
    },
    selectAlert(alert) {
      this.selectedAlert = alert
      if (!alert.read) {
        this.markAsRead(alert)
      }
    },
    toggleRead(alert) {
      alert.read = !alert.read
      this.updateAlertStats()
    },
    markAsRead(alert) {
      alert.read = true
      this.updateAlertStats()
    },
    shareAlert(alert) {
      // In a real app, this would use the Web Share API or similar
      if (navigator.share) {
        navigator.share({
          title: alert.title,
          text: alert.message,
          url: window.location.href
        })
      } else {
        // Fallback: copy to clipboard
        navigator.clipboard.writeText(`${alert.title}: ${alert.message}`)
        alert('Alert copied to clipboard!')
      }
    },
    saveAlert(alert) {
      // Implementation for saving alerts
      console.log('Saving alert:', alert)
    },
    async refreshAlerts() {
      this.refreshing = true
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000))
      this.refreshing = false
    },
    sendEmergencyAlert() {
      this.$router.push('/user/report')
    },
    updateAlertStats() {
      this.activeAlerts = this.alerts.filter(alert => !alert.read).length
      this.criticalAlerts = this.alerts.filter(alert => alert.priority === 'critical' && !alert.read).length
      this.todayAlerts = this.alerts.filter(alert => alert.time.includes('min') || alert.time.includes('hour')).length
    }
  },
  mounted() {
    this.updateAlertStats()
  }
}
</script>

<style scoped>
.user-alerts {
  min-height: 100vh;
  background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);
  color: white;
}

.alerts-header {
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

.floating-alerts {
  position: relative;
  width: 100%;
  height: 100%;
}

.floating-alert {
  position: absolute;
  width: 100px;
  height: 100px;
  background: radial-gradient(circle, rgba(0, 150, 255, 0.1) 0%, transparent 70%);
  border-radius: 50%;
  animation: float 6s ease-in-out infinite;
}

.floating-alert:nth-child(1) {
  top: 20%;
  left: 10%;
}

.floating-alert:nth-child(2) {
  top: 60%;
  right: 15%;
  animation-delay: 2s;
}

.floating-alert:nth-child(3) {
  bottom: 30%;
  left: 20%;
  animation-delay: 4s;
}

@keyframes float {
  0%, 100% { transform: translateY(0) scale(1); }
  50% { transform: translateY(-20px) scale(1.1); }
}

.header-content {
  position: relative;
  z-index: 1;
  text-align: center;
}

.alerts-title {
  font-size: 36px;
  margin-bottom: 10px;
  background: linear-gradient(90deg, #ffffff, #0096ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.alerts-subtitle {
  color: #888;
  font-size: 16px;
  margin-bottom: 30px;
}

.alert-stats {
  display: flex;
  justify-content: center;
  gap: 40px;
  margin-top: 30px;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #0096ff;
  margin-bottom: 5px;
}

.stat-label {
  color: #888;
  font-size: 14px;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.alerts-content {
  padding: 30px 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.preferences-card {
  background: rgba(30, 30, 40, 0.8);
  border-radius: 15px;
  padding: 25px;
  margin-bottom: 30px;
  border: 1px solid rgba(100, 100, 120, 0.2);
  backdrop-filter: blur(10px);
}

.preferences-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.preferences-header h3 {
  color: white;
  font-size: 20px;
}

.toggle-btn {
  background: rgba(0, 150, 255, 0.2);
  border: 1px solid #0096ff;
  color: #0096ff;
  padding: 8px 16px;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
}

.toggle-btn:hover {
  background: #0096ff;
  color: white;
}

.preferences-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  padding-top: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.preference-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  background: rgba(40, 40, 50, 0.6);
  border-radius: 10px;
}

.preference-item label {
  color: #ddd;
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

.filters-section {
  display: flex;
  gap: 20px;
  margin-bottom: 30px;
  align-items: center;
}

.filter-tabs {
  display: flex;
  gap: 10px;
  flex: 1;
  overflow-x: auto;
}

.filter-tab {
  background: rgba(40, 40, 50, 0.8);
  border: 1px solid rgba(100, 100, 120, 0.3);
  color: #888;
  padding: 12px 20px;
  border-radius: 10px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
  white-space: nowrap;
  font-size: 14px;
}

.filter-tab.active {
  background: rgba(0, 150, 255, 0.2);
  border-color: #0096ff;
  color: #0096ff;
}

.tab-count {
  background: rgba(0, 0, 0, 0.3);
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
}

.search-box {
  position: relative;
  min-width: 250px;
}

.search-input {
  width: 100%;
  padding: 12px 15px 12px 40px;
  background: rgba(40, 40, 50, 0.8);
  border: 1px solid rgba(100, 100, 120, 0.3);
  border-radius: 10px;
  color: white;
  font-size: 14px;
}

.icon-search {
  position: absolute;
  left: 15px;
  top: 50%;
  transform: translateY(-50%);
  color: #888;
}

.alerts-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.alert-card {
  background: rgba(30, 30, 40, 0.8);
  border-radius: 15px;
  padding: 20px;
  display: flex;
  gap: 15px;
  cursor: pointer;
  transition: all 0.3s ease;
  border-left: 4px solid #0096ff;
  position: relative;
  overflow: hidden;
}

.alert-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, rgba(0, 150, 255, 0.1), transparent);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.alert-card:hover::before {
  opacity: 1;
}

.alert-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.alert-card.unread {
  border-left-color: #ffaa00;
  background: rgba(255, 170, 0, 0.05);
}

.alert-card.critical {
  border-left-color: #ff4444;
  background: rgba(255, 68, 68, 0.05);
}

.alert-card.high {
  border-left-color: #ff6b6b;
}

.alert-card.info {
  border-left-color: #00cc66;
}

.alert-icon {
  position: relative;
  width: 50px;
  height: 50px;
  background: rgba(0, 150, 255, 0.2);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
}

.alert-card.critical .alert-icon {
  background: rgba(255, 68, 68, 0.2);
}

.alert-card.high .alert-icon {
  background: rgba(255, 107, 107, 0.2);
}

.alert-card.info .alert-icon {
  background: rgba(0, 204, 102, 0.2);
}

.unread-indicator {
  position: absolute;
  top: -5px;
  right: -5px;
  width: 12px;
  height: 12px;
  background: #ffaa00;
  border-radius: 50%;
  border: 2px solid #1a1a2e;
}

.alert-content {
  flex: 1;
}

.alert-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

.alert-title {
  color: white;
  font-size: 16px;
  font-weight: 600;
  margin: 0;
}

.alert-time {
  color: #888;
  font-size: 12px;
  white-space: nowrap;
}

.alert-message {
  color: #aaa;
  font-size: 14px;
  line-height: 1.5;
  margin-bottom: 10px;
}

.alert-meta {
  display: flex;
  gap: 15px;
  font-size: 12px;
  color: #666;
}

.alert-actions {
  display: flex;
  gap: 5px;
  align-self: flex-start;
}

.action-btn {
  background: rgba(60, 60, 70, 0.8);
  border: none;
  color: #888;
  width: 36px;
  height: 36px;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.action-btn:hover {
  background: rgba(0, 150, 255, 0.2);
  color: #0096ff;
}

.action-btn.primary {
  background: #0096ff;
  color: white;
}

.action-btn.primary:hover {
  background: #0077cc;
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

.alert-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.modal-backdrop {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(5px);
}

.modal-content {
  position: relative;
  background: rgba(30, 30, 40, 0.95);
  border-radius: 20px;
  max-width: 600px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  border: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
}

.modal-header {
  padding: 25px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.modal-header.critical {
  background: rgba(255, 68, 68, 0.1);
}

.modal-title {
  display: flex;
  align-items: center;
  gap: 15px;
}

.modal-title i {
  font-size: 24px;
  width: 40px;
  height: 40px;
  background: rgba(0, 150, 255, 0.2);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-header.critical .modal-title i {
  background: rgba(255, 68, 68, 0.2);
}

.modal-title h2 {
  margin: 0;
  color: white;
  font-size: 20px;
}

.close-btn {
  background: none;
  border: none;
  color: #888;
  font-size: 24px;
  cursor: pointer;
  transition: color 0.3s ease;
}

.close-btn:hover {
  color: white;
}

.modal-body {
  padding: 25px;
}

.alert-details {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 25px;
  padding-bottom: 25px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.detail-label {
  color: #888;
  font-size: 14px;
}

.detail-value {
  color: white;
  font-size: 14px;
  font-weight: 500;
}

.priority-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  text-transform: capitalize;
}

.priority-badge.critical {
  background: rgba(255, 68, 68, 0.2);
  color: #ff4444;
}

.priority-badge.high {
  background: rgba(255, 107, 107, 0.2);
  color: #ff6b6b;
}

.priority-badge.info {
  background: rgba(0, 204, 102, 0.2);
  color: #00cc66;
}

.alert-full-message,
.alert-instructions,
.affected-areas {
  margin-bottom: 25px;
}

.alert-full-message h4,
.alert-instructions h4,
.affected-areas h4 {
  color: white;
  margin-bottom: 15px;
  font-size: 16px;
}

.alert-full-message p {
  color: #aaa;
  line-height: 1.6;
}

.alert-instructions ul {
  color: #aaa;
  padding-left: 20px;
}

.alert-instructions li {
  margin-bottom: 8px;
  line-height: 1.5;
}

.areas-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.area-tag {
  background: rgba(0, 150, 255, 0.2);
  color: #0096ff;
  padding: 6px 12px;
  border-radius: 15px;
  font-size: 12px;
}

.modal-actions {
  display: flex;
  gap: 10px;
  padding: 20px 25px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.emergency-actions {
  position: fixed;
  bottom: 20px;
  right: 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  z-index: 100;
}

.emergency-btn {
  background: rgba(40, 40, 50, 0.9);
  border: 1px solid rgba(100, 100, 120, 0.3);
  color: #ddd;
  padding: 15px 20px;
  border-radius: 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 10px;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  font-weight: 600;
}

.emergency-btn.critical {
  background: linear-gradient(135deg, #ff4444, #cc0000);
  border-color: #ff4444;
  color: white;
  animation: pulse-critical 2s infinite;
}

.emergency-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.3);
}

.emergency-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@keyframes pulse-critical {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Transitions */
.alert-item-enter-active,
.alert-item-leave-active {
  transition: all 0.5s ease;
}

.alert-item-enter-from {
  opacity: 0;
  transform: translateX(-30px);
}

.alert-item-leave-to {
  opacity: 0;
  transform: translateX(30px);
}

.modal-enter-active,
.modal-leave-active {
  transition: all 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
  transform: scale(0.9);
}

/* Responsive Design */
@media (max-width: 768px) {
  .alerts-header {
    padding: 30px 15px;
  }
  
  .alerts-title {
    font-size: 28px;
  }
  
  .alert-stats {
    gap: 20px;
  }
  
  .stat-value {
    font-size: 24px;
  }
  
  .filters-section {
    flex-direction: column;
  }
  
  .filter-tabs {
    width: 100%;
    justify-content: flex-start;
  }
  
  .search-box {
    width: 100%;
    min-width: auto;
  }
  
  .alert-card {
    padding: 15px;
  }
  
  .alert-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 5px;
  }
  
  .modal-content {
    margin: 10px;
    max-height: calc(100vh - 20px);
  }
  
  .modal-actions {
    flex-direction: column;
  }
  
  .emergency-actions {
    position: static;
    margin-top: 30px;
    flex-direction: row;
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .preferences-content {
    grid-template-columns: 1fr;
  }
  
  .alert-details {
    grid-template-columns: 1fr;
  }
  
  .alert-meta {
    flex-direction: column;
    gap: 5px;
  }
}

/* Icon placeholders */
.icon-settings::before { content: "⚙️"; }
.icon-all::before { content: "📋"; }
.icon-critical::before { content: "🚨"; }
.icon-weather::before { content: "🌤️"; }
.icon-safety::before { content: "🛡️"; }
.icon-traffic::before { content: "🚧"; }
.icon-search::before { content: "🔍"; }
.icon-flood::before { content: "🌊"; }
.icon-info::before { content: "ℹ️"; }
.icon-location::before { content: "📍"; }
.icon-read::before { content: "📭"; }
.icon-unread::before { content: "📬"; }
.icon-share::before { content: "📤"; }
.icon-save::before { content: "💾"; }
.icon-emergency::before { content: "🚨"; }
.icon-refresh::before { content: "🔄"; }
.icon-empty::before { content: "📭"; }
</style>