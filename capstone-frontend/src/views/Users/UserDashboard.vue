<template>
  <div class="user-dashboard">
    <div class="dashboard-grid">
      <!-- Emergency Status Card -->
      <div class="status-card critical">
        <div class="status-icon">
          <i class="icon-warning"></i>
        </div>
        <div class="status-content">
          <h3>Emergency Alert</h3>
          <p>Typhoon Ruby approaching your area</p>
          <span class="status-time">Updated 5 min ago</span>
        </div>
      </div>
      
      <!-- Evacuation Centers Card -->
      <div class="status-card">
        <div class="status-icon">
          <i class="icon-shelter"></i>
        </div>
        <div class="status-content">
          <h3>Open Shelters</h3>
          <p>{{ openShelters }} centers available</p>
          <span class="status-time">Nearest: 2.3km away</span>
        </div>
      </div>
      
      <!-- Active Hazards Card -->
      <div class="status-card warning">
        <div class="status-icon">
          <i class="icon-hazard"></i>
        </div>
        <div class="status-content">
          <h3>Active Hazards</h3>
          <p>{{ activeHazards }} reported in your area</p>
          <span class="status-time">3 verified today</span>
        </div>
      </div>
    </div>
    
    <div class="dashboard-content">
      <!-- Recent Hazards -->
      <div class="recent-section">
        <div class="section-header">
          <h2>Recent Hazards in Your Area</h2>
          <button class="view-all-btn" @click="$router.push('/user/map')">View All</button>
        </div>
        <div class="hazards-list">
          <div 
            v-for="hazard in recentHazards" 
            :key="hazard.id"
            class="hazard-item"
            :class="hazard.status"
          >
            <div class="hazard-icon">
              <i :class="getHazardIcon(hazard.type)"></i>
            </div>
            <div class="hazard-details">
              <h4>{{ hazard.title }}</h4>
              <p>{{ hazard.location }} • {{ hazard.distance }} away</p>
              <span class="hazard-status">{{ hazard.status }}</span>
            </div>
            <div class="hazard-time">{{ hazard.time }}</div>
          </div>
        </div>
      </div>
      
      <!-- Emergency Contacts -->
      <div class="contacts-section">
        <h2>Emergency Contacts</h2>
        <div class="contacts-grid">
          <div class="contact-item">
            <i class="icon-police"></i>
            <span>Police</span>
            <small>911</small>
          </div>
          <div class="contact-item">
            <i class="icon-fire"></i>
            <span>Fire Dept</span>
            <small>912</small>
          </div>
          <div class="contact-item">
            <i class="icon-ambulance"></i>
            <span>Ambulance</span>
            <small>913</small>
          </div>
          <div class="contact-item">
            <i class="icon-rescue"></i>
            <span>Rescue</span>
            <small>914</small>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const openShelters = ref(8)
const activeHazards = ref(12)
const recentHazards = ref([
  {
    id: 1,
    title: 'Flooded Street',
    type: 'flood',
    location: 'Main Street',
    distance: '0.8km',
    status: 'verified',
    time: '2 hours ago'
  },
  {
    id: 2,
    title: 'Fallen Tree',
    type: 'tree',
    location: 'Oak Avenue',
    distance: '1.2km',
    status: 'pending',
    time: '4 hours ago'
  },
  {
    id: 3,
    title: 'Landslide Risk',
    type: 'landslide',
    location: 'Hill Road',
    distance: '2.1km',
    status: 'verified',
    time: '6 hours ago'
  }
])

const getHazardIcon = (type) => {
  const icons = {
    flood: 'icon-flood',
    tree: 'icon-tree',
    landslide: 'icon-landslide',
    fire: 'icon-fire',
    default: 'icon-hazard'
  }
  return icons[type] || icons.default
}
</script>

<style scoped>
.user-dashboard {
  padding: 20px;
  background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);
  min-height: 100vh;
  color: white;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.status-card {
  background: rgba(30, 30, 40, 0.8);
  border-radius: 15px;
  padding: 25px;
  display: flex;
  align-items: center;
  gap: 20px;
  border: 1px solid rgba(100, 100, 120, 0.2);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.status-card::before {
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

.status-card:hover::before {
  opacity: 1;
}

.status-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.3);
}

.status-card.critical {
  border-left: 4px solid #ff4444;
  background: rgba(255, 68, 68, 0.1);
}

.status-card.warning {
  border-left: 4px solid #ffaa00;
  background: rgba(255, 170, 0, 0.1);
}

.status-icon {
  width: 60px;
  height: 60px;
  background: rgba(0, 150, 255, 0.2);
  border-radius: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.status-card.critical .status-icon {
  background: rgba(255, 68, 68, 0.2);
}

.status-card.warning .status-icon {
  background: rgba(255, 170, 0, 0.2);
}

.status-content h3 {
  font-size: 18px;
  margin-bottom: 5px;
  color: white;
}

.status-content p {
  color: #ddd;
  margin-bottom: 5px;
  font-size: 14px;
}

.status-time {
  color: #888;
  font-size: 12px;
}

.dashboard-content {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 30px;
}

.quick-actions h2,
.recent-section h2,
.contacts-section h2 {
  color: white;
  margin-bottom: 20px;
  font-size: 22px;
}

.action-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

.action-btn {
  background: rgba(40, 40, 50, 0.8);
  border: 1px solid rgba(100, 100, 120, 0.3);
  border-radius: 12px;
  padding: 20px;
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.action-btn:hover {
  background: rgba(0, 150, 255, 0.2);
  border-color: #0096ff;
  transform: translateY(-3px);
  box-shadow: 0 10px 20px rgba(0, 150, 255, 0.2);
}

.action-btn i {
  font-size: 24px;
  color: #0096ff;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.view-all-btn {
  background: transparent;
  border: 1px solid #0096ff;
  color: #0096ff;
  padding: 8px 16px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.view-all-btn:hover {
  background: #0096ff;
  color: white;
}

.hazards-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.hazard-item {
  background: rgba(40, 40, 50, 0.8);
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 15px;
  transition: all 0.3s ease;
  border-left: 4px solid #0096ff;
}

.hazard-item.verified {
  border-left: 4px solid #00cc66;
}

.hazard-item.pending {
  border-left: 4px solid #ffaa00;
}

.hazard-item:hover {
  transform: translateX(5px);
  background: rgba(50, 50, 60, 0.8);
}

.hazard-icon {
  width: 40px;
  height: 40px;
  background: rgba(0, 150, 255, 0.2);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}

.hazard-details {
  flex: 1;
}

.hazard-details h4 {
  color: white;
  margin-bottom: 5px;
  font-size: 16px;
}

.hazard-details p {
  color: #888;
  font-size: 14px;
  margin-bottom: 5px;
}

.hazard-status {
  font-size: 12px;
  padding: 3px 8px;
  border-radius: 12px;
  background: rgba(0, 150, 255, 0.2);
  color: #0096ff;
}

.hazard-item.verified .hazard-status {
  background: rgba(0, 204, 102, 0.2);
  color: #00cc66;
}

.hazard-item.pending .hazard-status {
  background: rgba(255, 170, 0, 0.2);
  color: #ffaa00;
}

.hazard-time {
  color: #666;
  font-size: 12px;
}

.contacts-section {
  grid-column: 1 / -1;
}

.contacts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 15px;
}

.contact-item {
  background: rgba(40, 40, 50, 0.8);
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  transition: all 0.3s ease;
  border: 1px solid rgba(100, 100, 120, 0.3);
}

.contact-item:hover {
  background: rgba(0, 150, 255, 0.2);
  border-color: #0096ff;
  transform: translateY(-3px);
}

.contact-item i {
  font-size: 24px;
  color: #0096ff;
  margin-bottom: 10px;
  display: block;
}

.contact-item span {
  display: block;
  color: white;
  font-weight: 600;
  margin-bottom: 5px;
}

.contact-item small {
  color: #888;
  font-size: 12px;
}

/* Icon placeholders - you would replace these with actual icon classes */
.icon-alert::before { content: "⚠️"; }
.icon-warning::before { content: "🚨"; }
.icon-shelter::before { content: "🏠"; }
.icon-hazard::before { content: "⚠️"; }
.icon-report::before { content: "📝"; }
.icon-map::before { content: "🗺️"; }
.icon-notification::before { content: "🔔"; }
.icon-profile::before { content: "👤"; }
.icon-flood::before { content: "🌊"; }
.icon-tree::before { content: "🌳"; }
.icon-landslide::before { content: "⛰️"; }
.icon-police::before { content: "👮"; }
.icon-fire::before { content: "🚒"; }
.icon-ambulance::before { content: "🚑"; }
.icon-rescue::before { content: "🛟"; }
.icon-logout::before { content: "🚪"; }

@media (max-width: 1024px) {
  .dashboard-content {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
  
  .action-grid {
    grid-template-columns: 1fr;
  }
  
  .dashboard-header {
    flex-direction: column;
    gap: 15px;
    align-items: flex-start;
  }
  
  .header-actions {
    width: 100%;
    justify-content: space-between;
  }
}
</style>