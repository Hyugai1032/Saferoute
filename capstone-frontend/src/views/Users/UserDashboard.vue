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
      <div class="status-card" :class="activeHazards > 0 ? 'warning' : 'safe'">
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
          <div v-if="loadingHazards" class="empty-state">
            <span class="loading-spinner"></span>
            <p>Loading nearby hazards...</p>
          </div>

          <div v-else-if="recentHazards.length === 0" class="empty-state">
            <span class="empty-state-icon">✅</span>
            <p>No recent nearby hazards.</p>
            <span class="empty-state-sub">Your area looks clear for now.</span>
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
  /* Reuse the app's real theme tokens (proven live via ThemeToggle) wherever
     they exist, with dark-mode-safe fallbacks. We deliberately do NOT
     redeclare --text-primary/--surface-elevated/--border-light locally —
     doing that previously shadowed the real global values for this whole
     subtree, which is why text vanished in light mode. */
  --sr-accent: var(--accent-primary, #0096ff);
  --sr-accent-soft: rgba(0, 150, 255, 0.16);
  --sr-safe: #16a34a;
  --sr-safe-soft: rgba(22, 163, 74, 0.16);
  --sr-warning: #d97706;
  --sr-warning-soft: rgba(217, 119, 6, 0.16);
  --sr-critical: #dc2626;
  --sr-critical-soft: rgba(220, 38, 38, 0.16);
  --sr-panel: var(--surface-elevated, rgba(255, 255, 255, 0.045));
  --sr-panel-inner: rgba(120, 120, 130, 0.07);
  --sr-panel-inner-hover: rgba(120, 120, 130, 0.13);
  --sr-border: var(--border-light, rgba(255, 255, 255, 0.09));
  --sr-border-strong: rgba(120, 120, 130, 0.35);
  --sr-text-secondary: #767b85;
  --sr-text-tertiary: #8a8f97;
  --radius-md: 12px;
  --radius-lg: 16px;

  padding: 24px clamp(20px, 3vw, 32px) 40px;
  background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);
  min-height: 100vh;
  color: var(--text-primary, #ffffff);
}

/* ===== Top status cards ===== */
.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 18px;
  margin-bottom: 24px;
}

.status-card {
  background: var(--sr-panel);
  min-height: 120px;
  border-radius: var(--radius-lg);
  padding: 22px 24px;
  display: flex;
  align-items: center;
  gap: 18px;
  border: 1px solid var(--sr-border);
  border-left: 4px solid var(--sr-accent);
  transition: transform 0.25s ease, box-shadow 0.25s ease, background 0.25s ease;
  position: relative;
  overflow: hidden;
}

.status-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 14px 28px rgba(0, 0, 0, 0.22);
}

.status-card.critical {
  border-left-color: var(--sr-critical);
  background: var(--sr-critical-soft);
}

.status-card.warning {
  border-left-color: var(--sr-warning);
  background: var(--sr-warning-soft);
}

/* Zero-hazard state reads as reassurance, not an unresolved alert */
.status-card.safe {
  border-left-color: var(--sr-safe);
  background: var(--sr-safe-soft);
}

.status-icon {
  width: 54px;
  height: 54px;
  flex-shrink: 0;
  background: var(--sr-accent-soft);
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
}

.status-card.critical .status-icon { background: var(--sr-critical-soft); }
.status-card.warning .status-icon { background: var(--sr-warning-soft); }
.status-card.safe .status-icon { background: var(--sr-safe-soft); }

.status-content h3 {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 4px;
  color: var(--text-primary, #ffffff);
}

.status-content p {
  color: var(--sr-text-secondary);
  margin: 0 0 4px;
  font-size: 14px;
}

.status-time {
  color: var(--sr-text-tertiary);
  font-size: 12px;
}

/* ===== Main content: hazards (left) + contacts stay full-width below ===== */
.dashboard-content {
  display: grid;
  grid-template-columns: 1fr;
  gap: 24px;
  margin-bottom: 24px;
}

.recent-section,
.contacts-section {
  background: var(--sr-panel);
  border: 1px solid var(--sr-border);
  border-radius: var(--radius-lg);
  padding: 22px 24px;
}

.recent-section h2,
.contacts-section h2 {
  color: var(--text-primary, #ffffff);
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 18px;
}

.view-all-btn {
  background: transparent;
  border: 1px solid var(--sr-accent);
  color: var(--sr-accent);
  font-size: 0.85rem;
  font-weight: 600;
  padding: 7px 14px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s ease, color 0.2s ease, transform 0.2s ease;
}

.view-all-btn:hover {
  background: var(--sr-accent);
  color: white;
  transform: translateY(-1px);
}

.view-all-btn:focus-visible {
  outline: 2px solid var(--sr-accent);
  outline-offset: 2px;
}

.hazards-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.hazard-item {
  background: var(--sr-panel-inner);
  border-radius: var(--radius-md);
  padding: 16px 18px;
  display: flex;
  align-items: center;
  gap: 14px;
  transition: transform 0.2s ease, background 0.2s ease;
  border: 1px solid var(--sr-border);
  border-left: 3px solid var(--sr-accent);
}

.hazard-item.verified {
  border-left-color: var(--sr-safe);
}

.hazard-item.pending {
  border-left-color: var(--sr-warning);
}

.hazard-item:hover {
  transform: translateX(4px);
  background: var(--sr-panel-inner-hover);
}

.hazard-icon {
  width: 38px;
  height: 38px;
  flex-shrink: 0;
  background: var(--sr-accent-soft);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 17px;
}

.hazard-details {
  flex: 1;
  min-width: 0;
}

.hazard-details h4 {
  color: var(--text-primary, #ffffff);
  margin: 0 0 3px;
  font-size: 15px;
  font-weight: 600;
}

.hazard-details p {
  color: var(--sr-text-secondary);
  font-size: 13px;
  margin: 0 0 6px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.hazard-status {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.02em;
  text-transform: capitalize;
  padding: 3px 9px;
  border-radius: 12px;
  background: var(--sr-accent-soft);
  color: var(--sr-accent);
}

.hazard-item.verified .hazard-status {
  background: var(--sr-safe-soft);
  color: var(--sr-safe);
}

.hazard-item.pending .hazard-status {
  background: var(--sr-warning-soft);
  color: var(--sr-warning);
}

.hazard-time {
  color: var(--sr-text-tertiary);
  font-size: 12px;
  flex-shrink: 0;
  white-space: nowrap;
}

/* Empty / loading state — centered so it doesn't float in dead whitespace */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  gap: 6px;
  padding: 36px 20px;
  color: var(--sr-text-secondary);
}

.empty-state-icon {
  font-size: 28px;
  margin-bottom: 4px;
}

.empty-state p {
  margin: 0;
  color: var(--text-primary, #ffffff);
  font-size: 14px;
  font-weight: 600;
}

.empty-state-sub {
  font-size: 12px;
  color: var(--sr-text-tertiary);
}

.loading-spinner {
  width: 22px;
  height: 22px;
  border: 2px solid var(--sr-border-strong);
  border-top-color: var(--sr-accent);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 4px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* ===== Emergency contacts ===== */
.contacts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 14px;
}

.contact-item {
  background: var(--sr-panel-inner);
  border-radius: var(--radius-md);
  padding: 18px 12px;
  text-align: center;
  transition: transform 0.2s ease, background 0.2s ease, border-color 0.2s ease;
  border: 1px solid var(--sr-border);
}

.contact-item:hover {
  background: var(--sr-accent-soft);
  border-color: var(--sr-accent);
  transform: translateY(-3px);
}

.contact-item i {
  font-size: 22px;
  margin-bottom: 8px;
  display: block;
}

.contact-item span {
  display: block;
  color: var(--text-primary, #ffffff);
  font-weight: 600;
  font-size: 14px;
  margin-bottom: 3px;
}

.contact-item small {
  color: var(--sr-text-secondary);
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.02em;
}

/* Icon placeholders - swap for an icon font/SVG set when convenient */
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
.icon-rescue::before { content: "🆘"; }
.icon-logout::before { content: "🚪"; }

@media (max-width: 768px) {
  .user-dashboard {
    padding: 18px 16px 32px;
  }

  .dashboard-grid {
    grid-template-columns: 1fr;
  }

  .recent-section,
  .contacts-section {
    padding: 18px;
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

@media (prefers-reduced-motion: reduce) {
  .status-card,
  .hazard-item,
  .contact-item,
  .view-all-btn,
  .loading-spinner {
    transition: none;
    animation: none;
  }
}
</style>