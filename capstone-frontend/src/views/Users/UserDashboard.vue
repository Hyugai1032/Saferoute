<template>
  <div class="user-dashboard">
      <div class="dashboard-grid">
      <!-- Evacuation Centers Card -->
      <div class="status-card">
        <div class="status-icon">
          <i class="icon-shelter"></i>
        </div>
        <div class="status-content">
          <h3>Open Shelters</h3>

          <p v-if="loadingShelters">Loading shelters...</p>
          <p v-else>{{ openShelters }} centers available</p>

          <span class="status-time">
            <template v-if="nearestShelterDistance !== null">
              Nearest: {{ nearestShelterDistance.toFixed(1) }}km away
            </template>
            <template v-else>
              No nearby shelter location available
            </template>
          </span>
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
          <span class="status-time">{{ activeHazards }} verified nearby today</span>
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
          <div v-if="loadingHazards">
            Loading nearby hazards...
          </div>

          <div v-else-if="recentHazards.length === 0">
            No recent nearby hazards.
          </div>

          <div 
            v-else
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
</template>

<script setup>
import { ref, onMounted } from "vue";
import axios from "axios";

const RAW_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";
const API_BASE = RAW_BASE.replace(/\/api\/?$/, "");
const NEARBY_ALERTS_URL = `${API_BASE}/api/user/nearby-hazard-alerts/`;

const MAP_OVERVIEW_URL = `${API_BASE}/api/map/overview/`;

const openShelters = ref(0);
const nearestShelterDistance = ref(null);
const loadingShelters = ref(false);
const activeHazards = ref(0);
const recentHazards = ref([]);
const loadingHazards = ref(false);

const radiusKm = ref(3);
const userLoc = ref(null);

function getHazardIcon(type) {
  const t = String(type || "").toLowerCase();

  if (t.includes("flood")) return "icon-flood";
  if (t.includes("fire")) return "icon-fire";
  if (t.includes("landslide")) return "icon-landslide";
  if (t.includes("tree")) return "icon-tree";
  if (t.includes("road")) return "icon-traffic";

  return "icon-hazard";
}

function formatTimeAgo(dateString) {
  if (!dateString) return "";

  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now - date;

  const minutes = Math.floor(diffMs / 60000);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);

  if (minutes < 1) return "Just now";
  if (minutes < 60) return `${minutes} min ago`;
  if (hours < 24) return `${hours} hour${hours > 1 ? "s" : ""} ago`;
  return `${days} day${days > 1 ? "s" : ""} ago`;
}

function mapHazardToDashboardItem(h) {
  const type = h.hazard_type || h.type || "Hazard";
  const alertTime = h.approved_at || h.created_at;

  return {
    id: h.id,
    title: type,
    type,
    location: h.address || h.location || "Nearby area",
    distance: h.distance_km != null ? `${Number(h.distance_km).toFixed(1)}km` : "Nearby",
    status: String(h.status || "approved").toLowerCase(),
    time: formatTimeAgo(alertTime),
  };
}

function getDistanceKm(lat1, lng1, lat2, lng2) {
  const R = 6371;
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLng = (lng2 - lng1) * Math.PI / 180;

  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(lat1 * Math.PI / 180) *
    Math.cos(lat2 * Math.PI / 180) *
    Math.sin(dLng / 2) ** 2;

  return R * (2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a)));
}

async function getCurrentLocation() {
  const saved = localStorage.getItem("alerts_userLoc");

  if (saved) {
    try {
      userLoc.value = JSON.parse(saved);
      return;
    } catch (e) {}
  }

  if (!navigator.geolocation) return;

  const pos = await new Promise((resolve, reject) => {
    navigator.geolocation.getCurrentPosition(resolve, reject, {
      enableHighAccuracy: true,
      timeout: 10000,
    });
  });

  userLoc.value = {
    lat: pos.coords.latitude,
    lng: pos.coords.longitude,
  };

  localStorage.setItem("alerts_userLoc", JSON.stringify(userLoc.value));
}

async function fetchOpenShelters() {
  loadingShelters.value = true;

  try {
    await getCurrentLocation();

    const token = localStorage.getItem("access_token");

    const headers = token
      ? { Authorization: `Bearer ${token}` }
      : {};

    const res = await axios.get(MAP_OVERVIEW_URL, {
      headers,
      params: {
        recent_hours: 48,
        prediction_window: 60,
        prediction_horizon: 60,
      },
    });

    const centers = Array.isArray(res.data?.centers)
      ? res.data.centers
      : [];

    const availableCenters = centers.filter((center) => {
      const familyCap = Number(center.family_capacity_max || 0);
      const individualCap = Number(center.individual_capacity_max || 0);
      const totalCap = familyCap + individualCap;

      const predictedStatus = center.predicted_status;

      return (
        totalCap > 0 &&
        predictedStatus !== "LIKELY_FULL" &&
        predictedStatus !== "UNAVAILABLE"
      );
    });

    openShelters.value = availableCenters.length;

    if (userLoc.value?.lat && userLoc.value?.lng) {
      const centersWithDistance = availableCenters
        .filter((c) => c.latitude && c.longitude)
        .map((c) => ({
          ...c,
          distanceKm: getDistanceKm(
            Number(userLoc.value.lat),
            Number(userLoc.value.lng),
            Number(c.latitude),
            Number(c.longitude)
          ),
        }))
        .sort((a, b) => a.distanceKm - b.distanceKm);

      nearestShelterDistance.value = centersWithDistance.length
        ? centersWithDistance[0].distanceKm
        : null;
    }
  } catch (err) {
    console.error("Failed to load open shelters:", err);
    openShelters.value = 0;
    nearestShelterDistance.value = null;
  } finally {
    loadingShelters.value = false;
  }
}

async function fetchNearbyHazards() {
  loadingHazards.value = true;

  try {
    await getCurrentLocation();

    if (!userLoc.value?.lat || !userLoc.value?.lng) {
      recentHazards.value = [];
      activeHazards.value = 0;
      return;
    }

    const token = localStorage.getItem("access_token");

    const headers = token
      ? { Authorization: `Bearer ${token}` }
      : {};

    const res = await axios.get(NEARBY_ALERTS_URL, {
      headers,
      params: {
        lat: userLoc.value.lat,
        lng: userLoc.value.lng,
        radius_km: radiusKm.value,
        recent_hours: 24,
      },
    });

    const hazards = Array.isArray(res.data)
      ? res.data
      : res.data.results || [];

    activeHazards.value = hazards.length;
    recentHazards.value = hazards.slice(0, 3).map(mapHazardToDashboardItem);
  } catch (err) {
    console.error("Failed to load dashboard hazards:", err);
    recentHazards.value = [];
    activeHazards.value = 0;
  } finally {
    loadingHazards.value = false;
  }
}

onMounted(() => {
  fetchNearbyHazards();
  fetchOpenShelters();
});
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
  grid-template-columns: repeat(2, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.status-card {
  background: rgba(30, 30, 40, 0.8);
  min-height: 135px;
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