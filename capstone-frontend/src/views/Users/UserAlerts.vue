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
        <transition name="fade">
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
        </transition>
      </div>

<div v-if="loadingAlerts" class="loading-line">
  Loading alerts...
</div>
<div v-else-if="alertsError" class="error-line">
  {{ alertsError }}
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
            <button class="action-btn primary" @click.stop="markAsRead(selectedAlert)">
              <i class="icon-read"></i>
              Mark as Read
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
import axios from "axios";

const RAW_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";
const API_BASE = RAW_BASE.replace(/\/api\/?$/, ""); // removes trailing /api if present
const HAZARDS_URL = `${API_BASE}/api/hazards/`;

function haversineKm(lat1, lon1, lat2, lon2) {
  const toRad = (v) => (v * Math.PI) / 180;
  const R = 6371;
  const dLat = toRad(lat2 - lat1);
  const dLon = toRad(lon2 - lon1);
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLon / 2) ** 2;
  return 2 * R * Math.asin(Math.sqrt(a));
}

export default {
  name: 'UserAlerts',
  data() {
    return {
      activeFilter: 'all',
      searchQuery: '',
      showPreferences: false,
      selectedAlert: null,
      refreshing: false,
activeAlerts: 0,
criticalAlerts: 0,
todayAlerts: 0,
      radiusKm: 3,
      userLoc: null, // { lat, lng }
      loadingAlerts: false,
      alertsError: "",
      preferences: {
        push: true,
        email: true,
        sms: false,
        criticalOnly: false
      },
      filterTabs: [
        { id: 'all', name: 'All', icon: 'icon-all' },
        { id: 'critical', name: 'Critical', icon: 'icon-critical' },
        { id: 'my_reports', name: 'My Reports', icon: 'icon-report' },
        { id: 'nearby', name: 'Nearby', icon: 'icon-location' }
      ],
      alerts: [
        {
          id: 1,
          title: 'Flash Flood Warning',
          message: 'Heavy rainfall expected in your area for the next 3 hours',
          fullMessage: 'Heavy rainfall with intensities of 2–3 inches per hour is expected. Avoid low-lying areas and do not attempt to cross flooded roads.',
          category: 'nearby',
          severity: 'critical',
          icon: 'icon-flood',
          source: 'Emergency Management',
          location: 'Near your pinned location',
          time: '10 min ago',
          fullTime: 'Today',
          createdAt: new Date(Date.now() - 10 * 60 * 1000).toISOString(),
          read: false,
          instructions: [
            'Move to higher ground if needed',
            'Avoid walking or driving through flood waters',
            'Prepare an emergency kit',
            'Monitor updates in the app'
          ],
          affectedAreas: ['Nearby roads', 'Low-lying areas']
        },
        {
          id: 2,
          title: 'Your Hazard Report Submitted',
          message: 'We received your hazard report and it is pending review.',
          fullMessage: 'Your hazard report has been submitted successfully. Staff will review and verify it as soon as possible.',
          category: 'my_reports',
          severity: 'info',
          icon: 'icon-info',
          source: 'System',
          location: 'From your recent report',
          time: '1 hour ago',
          fullTime: 'Today',
          createdAt: new Date(Date.now() - 60 * 60 * 1000).toISOString(),
          read: true
        },
        {
          id: 3,
          title: 'Report Status Updated',
          message: 'Your report status is now IN PROGRESS.',
          fullMessage: 'A staff member has acknowledged your report and is currently taking action on it. You may receive follow-up updates.',
          category: 'my_reports',
          severity: 'high',
          icon: 'icon-info',
          source: 'Evacuation Staff',
          location: 'From your recent report',
          time: '2 hours ago',
          fullTime: 'Today',
          createdAt: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
          read: false
        },
        {
          id: 4,
          title: 'Road Closure Nearby',
          message: 'Road blocked due to fallen power lines. Use alternate route.',
          fullMessage: 'A nearby road is temporarily closed due to fallen power lines. Please avoid the area and use alternative routes.',
          category: 'nearby',
          severity: 'high',
          icon: 'icon-traffic',
          source: 'Emergency Management',
          location: 'Main Road (approx. 1.2 km)',
          time: '3 hours ago',
          fullTime: 'Today',
          createdAt: new Date(Date.now() - 3 * 60 * 60 * 1000).toISOString(),
          read: false,
          affectedAreas: ['Main Road', 'Nearby intersections']
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
        if (this.activeFilter === 'critical') {
          filtered = filtered.filter(alert => alert.severity === 'critical')
        } else {
          filtered = filtered.filter(alert => alert.category === this.activeFilter)
        }
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
      if (filterId === 'critical') return this.alerts.filter(a => a.severity === 'critical').length
      return this.alerts.filter(a => a.category === filterId).length
    },
selectAlert(alert) {
  this.selectedAlert = alert
  // don’t auto mark read
},

toggleRead(alert) {
  if (!alert) return;
  alert.read = !alert.read;

  const readSet = this.getReadSet();
  const key = String(alert.id);
  if (alert.read) readSet.add(key);
  else readSet.delete(key);
  this.setReadSet(readSet);

  this.updateAlertStats();
},
markAsRead(alert) {
  if (!alert) return;
  alert.read = true;

  const readSet = this.getReadSet();
  readSet.add(String(alert.id));
  this.setReadSet(readSet);

  this.updateAlertStats();
   // ✅ Auto close modal
  this.selectedAlert = null;
},

getReadSet() {
  try {
    return new Set(JSON.parse(localStorage.getItem("alerts_read_keys") || "[]"));
  } catch {
    return new Set();
  }
},
setReadSet(readSet) {
  localStorage.setItem("alerts_read_keys", JSON.stringify([...readSet]));
},

getSavedSet() {
  try {
    return new Set(JSON.parse(localStorage.getItem("alerts_saved_keys") || "[]"));
  } catch {
    return new Set();
  }
},
setSavedSet(savedSet) {
  localStorage.setItem("alerts_saved_keys", JSON.stringify([...savedSet]));
},

applyLocalStatesToAlerts() {
  const readSet = this.getReadSet();
  const savedSet = this.getSavedSet();

  this.alerts = this.alerts.map(a => ({
    ...a,
    read: readSet.has(String(a.id)),
    saved: savedSet.has(String(a.id)),
  }));

  this.updateAlertStats();
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
  if (!alert) return;

  // toggle save
  alert.saved = !alert.saved;

  const savedSet = this.getSavedSet();
  const key = String(alert.id);
  if (alert.saved) savedSet.add(key);
  else savedSet.delete(key);
  this.setSavedSet(savedSet);
},
    async useMyLocation() {
  this.alertsError = "";
  if (!navigator.geolocation) {
    this.alertsError = "Geolocation not supported in this browser.";
    return;
  }

  const pos = await new Promise((resolve, reject) => {
    navigator.geolocation.getCurrentPosition(resolve, reject, {
      enableHighAccuracy: true,
      timeout: 10000,
    });
  });

  this.userLoc = {
    lat: pos.coords.latitude,
    lng: pos.coords.longitude,
  };
  localStorage.setItem("alerts_userLoc", JSON.stringify(this.userLoc));

  // refresh so Nearby updates
  await this.refreshAlerts();
},

mapHazardToAlert(h, category, distanceKm = null) {
  const hazardType = h.hazard_type || h.type || h.category || "Hazard";
  const status = String(h.status || "REPORTED").toUpperCase();

  const createdAt = h.created_at || h.createdAt || new Date().toISOString();
  const updatedAt = h.updated_at || h.updatedAt || createdAt;

  const typeLower = String(hazardType).toLowerCase();

  let severity = "info";
  if (
    status === "VERIFIED" || status === "CONFIRMED" ||
    typeLower.includes("flood") || typeLower.includes("fire") || typeLower.includes("landslide")
  ) severity = "high";

  if (typeLower.includes("flood") || typeLower.includes("fire") || typeLower.includes("landslide"))
    severity = "critical";

  const address = h.address || h.location || "Pinned location";
  const desc = h.description || h.details || "";

  return {
    id: `${category}:${h.id}`,
    title: category === "my_reports" ? `My Report: ${hazardType}` : `${hazardType} nearby`,
    message:
      category === "my_reports"
        ? `Status: ${status} • ${address}`
        : `${address}${distanceKm != null ? ` • ~${distanceKm.toFixed(1)} km` : ""}`,
    fullMessage:
      category === "my_reports"
        ? `Your hazard report is currently: ${status}\n\n${desc || "No description provided."}`
        : `${desc || "A hazard was reported in your area."}\n\nLocation: ${address}`,
    category,
    severity,
    icon: "icon-info",          // you can improve later
    source: category === "my_reports" ? "Your Submission" : "Community Reports",
    location: address,
    time: "",                   // optional (you can remove if not used)
    fullTime: "",               // optional
    createdAt: updatedAt,
    read: false,
  };
},
async refreshAlerts() {
  this.refreshing = true;
  this.loadingAlerts = true;
  this.alertsError = "";

  try {
    const token = localStorage.getItem("access_token");
    const headers = token ? { Authorization: `Bearer ${token}` } : {};

    const res = await axios.get(HAZARDS_URL, { headers });
    const hazards = Array.isArray(res.data) ? res.data : (res.data.results || []);

    // Try to get current user from localStorage
    const meRaw = localStorage.getItem("user") || localStorage.getItem("me");
    let me = null;
    try { me = meRaw ? JSON.parse(meRaw) : null; } catch (e) {}
    const myId = me?.id || me?.user_id || null;
    const myEmail = me?.email || null;

    const isMine = (h) => {
      if (myId && (h.reporter_id === myId || h.reporter === myId)) return true;
      if (myEmail && (h.reporter_email === myEmail)) return true;

      if (h.reporter && typeof h.reporter === "object") {
        if (myId && h.reporter.id === myId) return true;
        if (myEmail && h.reporter.email === myEmail) return true;
      }
      return false;
    };

    // My Reports
    const myReports = hazards
      .filter(isMine)
      .map((h) => this.mapHazardToAlert(h, "my_reports"));

    // Nearby (needs userLoc)
    let nearby = [];
    if (this.userLoc?.lat && this.userLoc?.lng) {
      nearby = hazards
        .filter((h) => !isMine(h))
        .filter((h) => h.latitude != null && h.longitude != null)
        // OPTIONAL: show only verified nearby
        // .filter((h) => String(h.status || "").toUpperCase() === "VERIFIED")
        .map((h) => {
          const d = haversineKm(
            this.userLoc.lat,
            this.userLoc.lng,
            Number(h.latitude),
            Number(h.longitude)
          );
          return { h, d };
        })
        .filter((x) => x.d <= this.radiusKm)
        .sort((a, b) => a.d - b.d)
        .map((x) => this.mapHazardToAlert(x.h, "nearby", x.d));
    }

    const all = [...nearby, ...myReports].sort((a, b) => {
      return new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime();
    });

    this.alerts = all;
// ✅ apply read/saved states from localStorage
this.applyLocalStatesToAlerts();
  } catch (err) {
    console.error(err);
    this.alertsError =
      err?.response?.data?.detail ||
      err?.message ||
      "Failed to load alerts. Check API URL and login token.";
  } finally {
    this.refreshing = false;
    this.loadingAlerts = false;
  }
},
sendEmergencyAlert() {
      this.$router.push('/user/report')
    },
    isToday(isoString) {
      if (!isoString) return false
      const d = new Date(isoString)
      const now = new Date()
      return (
        d.getFullYear() === now.getFullYear() &&
        d.getMonth() === now.getMonth() &&
        d.getDate() === now.getDate()
      )
    },
    updateAlertStats() {
      this.activeAlerts = this.alerts.filter(a => !a.read).length
      this.criticalAlerts = this.alerts.filter(a => a.severity === 'critical' && !a.read).length
      this.todayAlerts = this.alerts.filter(a => this.isToday(a.createdAt)).length

    // ✅ publish unread count to header badge
localStorage.setItem("unread_alerts_count", String(this.activeAlerts))
window.dispatchEvent(new CustomEvent("alerts:unread", { detail: { count: this.activeAlerts } }))    }
  },
mounted() {
  // load last saved location for Nearby
  const saved = localStorage.getItem("alerts_userLoc");
  if (saved) {
    try { this.userLoc = JSON.parse(saved); } catch(e) {}
  }

  // fetch alerts from backend
  this.refreshAlerts();

  // ✅ if a new report is submitted, refresh alerts list
  this._onNewReport = () => this.refreshAlerts();
  window.addEventListener("alerts:newReport", this._onNewReport);
},
beforeUnmount() {
  window.removeEventListener("alerts:newReport", this._onNewReport);
  
},
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

.fade-enter-active, .fade-leave-active { transition: opacity .2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

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

/* Prevent button labels from overflowing */
.toggle-btn,
.filter-tab,
.emergency-btn,
.action-btn {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Alert card layout: keep actions fixed, content flexible */
.alert-card {
  display: flex;
  align-items: center;
  gap: 12px;
}

.alert-content {
  flex: 1;
  min-width: 0; /* IMPORTANT for ellipsis to work */
}

.alert-title,
.alert-message,
.alert-location,
.alert-source {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* Make tab row scrollable instead of wrapping ugly */
.filter-tabs {
  display: flex;
  gap: 10px;
  overflow-x: auto;
  padding-bottom: 6px;
}

.filter-tabs::-webkit-scrollbar {
  height: 6px;
}

/* Tabs: keep them consistent and compact */
.filter-tab {
  flex: 0 0 auto;
  max-width: 160px;
}

/* Floating emergency actions: compact vertical stack */
.emergency-actions {
  position: fixed;
  right: 24px;
  bottom: 24px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  z-index: 50;
}

.emergency-btn {
  width: 180px; /* prevents weird stretching */
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 12px 14px;
  border-radius: 12px;
}

/* Modal footer actions: stop clipping */
.modal-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-start;
  flex-wrap: wrap;
  padding: 14px 18px;
}

/* Make modal buttons readable */
.modal-actions .modal-action,
.modal-actions button {
  min-width: 140px;
  padding: 10px 14px;
  border-radius: 10px;
  white-space: nowrap;
}

.emergency-actions {
  position: fixed;
  right: 24px;
  bottom: 24px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  z-index: 50;
}

.emergency-btn {
  width: 190px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 12px 14px;
  border-radius: 12px;
}

.spinning {
  animation: spin 0.9s linear infinite;
}
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.loading-line, .error-line {
  margin: 10px 0 0;
  padding: 10px 14px;
  border-radius: 10px;
  font-size: 14px;
  opacity: 0.9;
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