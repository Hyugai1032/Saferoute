<template>
  <div class="landing-page">
    <div class="bg-orb orb-1"></div>
    <div class="bg-orb orb-2"></div>
    <div class="bg-orb orb-3"></div>
    <div class="grid-overlay"></div>

    <!-- NAVBAR -->
    <header class="landing-header">
      <div class="brand" @click="scrollToSection('hero')">
        <div class="brand-mark">S</div>
        <div>
          <h1>SafeRoute</h1>
          <p>Evacuation Monitoring System</p>
        </div>
      </div>

      <nav class="nav-links">
        <button @click="scrollToSection('features')">Features</button>
        <button @click="scrollToSection('how-it-works')">How it Works</button>
        <button @click="scrollToSection('roles')">Users</button>
        <button @click="scrollToSection('contact')">Contact</button>
      </nav>

      <div class="nav-actions">
        <button class="btn ghost" @click="goToLogin">Login</button>
        <button class="btn primary" @click="goToRegister">Get Started</button>
      </div>
    </header>

    <!-- HERO -->
    <section id="hero" class="hero-section">
      <div class="hero-content">
        <span class="eyebrow">Disaster Preparedness • Evacuation Visibility • Faster Response</span>
        <h2>
          Smarter evacuation monitoring for <span>safer communities</span>
        </h2>
        <p class="hero-text">
          SafeRoute helps administrators, response teams, and evacuation center staff monitor hazards,
          track evacuees, manage centers, and coordinate emergency response in one unified platform.
        </p>

        <div class="hero-actions">
          <button class="btn primary large" @click="goToLogin">Access SafeRoute</button>
          <button class="btn secondary large" @click="scrollToSection('features')">Explore Features</button>
        </div>

        <div class="hero-feature-chips" aria-label="SafeRoute highlights">
          <div class="feature-chip">
            <span class="chip-dot blue"></span>
            <div>
              <strong>Real-time Monitoring</strong>
              <p>Instant visibility across hazards, centers, and response activity.</p>
            </div>
          </div>
          <div class="feature-chip">
            <span class="chip-dot cyan"></span>
            <div>
              <strong>Evacuation Center Management</strong>
              <p>Track capacity, occupancy, and readiness from one dashboard.</p>
            </div>
          </div>
          <div class="feature-chip">
            <span class="chip-dot orange"></span>
            <div>
              <strong>Hazard Reporting</strong>
              <p>Collect field reports quickly and route them for review.</p>
            </div>
          </div>
          <div class="feature-chip">
            <span class="chip-dot green"></span>
            <div>
              <strong>GIS Map Integration</strong>
              <p>Understand where incidents and centers are located at a glance.</p>
            </div>
          </div>
        </div>
      </div>

      <div class="hero-visual">
        <div class="glass-card dashboard-preview">
          <div class="preview-top">
            <div>
              <p class="mini-label">System Overview</p>
              <h3>Emergency Response Snapshot</h3>
            </div>
            <span class="status-pill">Live</span>
          </div>

          <div class="stats-grid">
            <div class="stat-card accent-blue">
              <h4>{{ displayStats.totalCenters }}</h4>
              <p>Evacuation Centers</p>
            </div>
            <div class="stat-card accent-orange">
              <h4>{{ displayStats.totalHazards }}</h4>
              <p>Active Hazard Reports</p>
            </div>
            <div class="stat-card accent-green">
              <h4>{{ displayStats.totalEvacuees }}</h4>
              <p>Tracked Evacuees</p>
            </div>
            <div class="stat-card accent-purple">
              <h4>{{ displayStats.occupancyRate }}%</h4>
              <p>Center Occupancy</p>
            </div>
          </div>

          <div class="activity-panel">
            <div class="activity-header">
              <h4>Response Coordination</h4>
              <span>Updated {{ lastUpdated }}</span>
            </div>

            <div class="activity-list">
              <div class="activity-item">
                <span class="dot green"></span>
                <div>
                  <strong>Evacuation logs centralized</strong>
                  <p>Monitor incoming and outgoing evacuees efficiently.</p>
                </div>
              </div>
              <div class="activity-item">
                <span class="dot orange"></span>
                <div>
                  <strong>Hazard reports submitted</strong>
                  <p>Field reports can be reviewed and mapped for faster response.</p>
                </div>
              </div>
              <div class="activity-item">
                <span class="dot blue"></span>
                <div>
                  <strong>GIS map visibility improved</strong>
                  <p>Track hazard and center locations from one dashboard.</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- TRUST BAR
    <section class="trust-strip">
      <div class="trust-item">
        <strong>Unified Tracking</strong>
        <span>From report to response</span>
      </div>
      <div class="trust-item">
        <strong>Role-Based Access</strong>
        <span>Admin, team, and staff workflows</span>
      </div>
      <div class="trust-item">
        <strong>Prepared for Emergencies</strong>
        <span>Focused on clarity and speed</span>
      </div>
    </section> -->

    <!-- FEATURES -->
    <section id="features" class="content-section">
      <div class="section-heading center">
        <span class="section-tag">Core Features</span>
        <h2>Everything needed to support coordinated evacuation operations</h2>
        <p>
          Designed to reduce delays, improve visibility, and make information easier to access during critical situations.
        </p>
      </div>

      <div class="feature-grid">
        <article class="feature-card">
          <div class="feature-icon">📍</div>
          <h3>Hazard Reporting</h3>
          <p>
            Submit and review hazard incidents with location context, helping authorities respond faster and more accurately.
          </p>
        </article>

        <article class="feature-card">
          <div class="feature-icon">🏫</div>
          <h3>Evacuation Center Monitoring</h3>
          <p>
            View center capacity, occupancy, and operational details to support better decision-making during emergencies.
          </p>
        </article>

        <article class="feature-card">
          <div class="feature-icon">👥</div>
          <h3>Evacuee Log Management</h3>
          <p>
            Record incoming and outgoing evacuees and maintain organized tracking at the center level.
          </p>
        </article>

        <article class="feature-card">
          <div class="feature-icon">🗺️</div>
          <h3>GIS Map View</h3>
          <p>
            Visualize hazards and evacuation centers on the map for a clearer understanding of the response environment.
          </p>
        </article>

        <article class="feature-card">
          <div class="feature-icon">🔔</div>
          <h3>Alerts & Notifications</h3>
          <p>
            Keep users informed of urgent updates, pending reports, and operational changes that require attention.
          </p>
        </article>

        <article class="feature-card">
          <div class="feature-icon">🔐</div>
          <h3>Role-Based Access Control</h3>
          <p>
            Provide the right information to the right users, whether they are provincial admins, municipal admins, responders, or staff.
          </p>
        </article>
      </div>
    </section>

    <!-- HOW IT WORKS -->
    <section id="how-it-works" class="content-section alt-bg">
      <div class="section-heading center">
        <span class="section-tag">Workflow</span>
        <h2>How SafeRoute supports emergency coordination</h2>
      </div>

      <div class="steps-grid">
        <div class="step-card">
          <span class="step-number">01</span>
          <h3>Report Hazards</h3>
          <p>Authorized users submit hazard reports and incident details for review.</p>
        </div>
        <div class="step-card">
          <span class="step-number">02</span>
          <h3>Monitor Centers</h3>
          <p>Administrators oversee center locations, occupancy, and resource visibility.</p>
        </div>
        <div class="step-card">
          <span class="step-number">03</span>
          <h3>Track Evacuees</h3>
          <p>Center staff encode and update evacuee logs to maintain accurate records.</p>
        </div>
        <div class="step-card">
          <span class="step-number">04</span>
          <h3>Coordinate Response</h3>
          <p>Teams use dashboards and maps to guide decisions and improve disaster response.</p>
        </div>
      </div>
    </section>

    <!-- ROLES -->
    <section id="roles" class="content-section">
      <div class="section-heading center">
        <span class="section-tag">User Roles</span>
        <h2>Built for the people who manage and respond on the ground</h2>
      </div>

      <div class="roles-grid">
        <div class="role-card">
          <h3>Provincial Admin</h3>
          <p>Oversees system-wide data, center monitoring, user coordination, and visibility across municipalities.</p>
        </div>
        <div class="role-card">
          <h3>Municipal Admin</h3>
          <p>Manages local evacuation operations, hazard reviews, and municipality-based monitoring.</p>
        </div>
        <div class="role-card">
          <h3>Response Team</h3>
          <p>Reviews field information, coordinates action, and supports real-time response decisions.</p>
        </div>
        <div class="role-card">
          <h3>Evacuation Center Staff</h3>
          <p>Updates center-level records, manages evacuee logs, and helps maintain operational accuracy.</p>
        </div>
      </div>
    </section>

    <!-- CTA -->
    <section class="cta-section">
      <div class="cta-card">
        <div>
          <span class="section-tag light">Start Using SafeRoute</span>
          <h2>Bring clarity, speed, and coordination to evacuation response</h2>
          <p>
            Access the platform to monitor hazards, manage evacuation centers, and support emergency operations more effectively.
          </p>
        </div>

        <div class="cta-actions">
          <button class="btn light" @click="goToLogin">Login to System</button>
          <button class="btn outline-light" @click="goToRegister">Create Account</button>
        </div>
      </div>
    </section>

<!-- CONTACT / FOOTER -->
<section id="contact" class="contact-section">
  <div class="contact-shell">
    <div class="contact-intro">
      <span class="section-tag">Contact & Support</span>
      <h2>Need assistance with SafeRoute?</h2>
      <p>
        Keep this section short and actionable: show who users should contact,
        how they can reach them, and when support is available.
      </p>
    </div>

    <div class="contact-grid simplified">
      <article class="contact-card primary-contact-card">
        <div class="contact-card-top">
          <div>
            <p class="contact-kicker">Primary Contact</p>
            <h3>SafeRoute Support Desk</h3>
          </div>
          <span class="contact-badge">Recommended</span>
        </div>

        <div class="contact-details-list">
          <div class="contact-line">
            <span class="contact-icon">📞</span>
            <div>
              <label>Phone</label>
              <a :href="`tel:${contactInfo.supportPhoneLink}`">
                {{ contactInfo.supportPhoneDisplay }}
              </a>
            </div>
          </div>

          <div class="contact-line">
            <span class="contact-icon">✉️</span>
            <div>
              <label>Email</label>
              <a :href="`mailto:${contactInfo.supportEmail}`">
                {{ contactInfo.supportEmail }}
              </a>
            </div>
          </div>

          <div class="contact-line">
            <span class="contact-icon">🕒</span>
            <div>
              <label>Office Hours</label>
              <p>{{ contactInfo.hours }}</p>
            </div>
          </div>
        </div>

        <div class="contact-actions">
          <a
            class="btn light contact-btn"
            :href="`tel:${contactInfo.supportPhoneLink}`"
          >
            Call Support
          </a>
          <a
            class="btn outline-light contact-btn dark-outline"
            :href="`mailto:${contactInfo.supportEmail}`"
          >
            Email Support
          </a>
        </div>
      </article>

      <article class="contact-card">
        <p class="contact-kicker">Emergency Coordination</p>
        <h3>Operations Hotline</h3>

        <div class="contact-details-list compact">
          <div class="contact-line">
            <span class="contact-icon">🚨</span>
            <div>
              <label>Hotline</label>
              <a :href="`tel:${contactInfo.hotlineLink}`">
                {{ contactInfo.hotlineDisplay }}
              </a>
            </div>
          </div>

          <div class="contact-line">
            <span class="contact-icon">🏢</span>
            <div>
              <label>Office</label>
              <p>{{ contactInfo.office }}</p>
            </div>
          </div>

          <div class="contact-line">
            <span class="contact-icon">📍</span>
            <div>
              <label>Location</label>
              <p>{{ contactInfo.location }}</p>
            </div>
          </div>
        </div>
      </article>

      </div>
  </div>
</section>
</div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()

const contactInfo = {
  supportPhoneDisplay: '+63 912 345 6789',
  supportPhoneLink: '+639123456789',
  supportEmail: 'saferoute.support@example.gov.ph',
  hotlineDisplay: '(043) 123-4567',
  hotlineLink: '+63431234567',
  office: 'Local Disaster Risk Reduction and Management Office',
  hours: 'Monday to Friday • 8:00 AM – 5:00 PM',
  location: 'Replace with your official office address',
}


const stats = ref({
  totalCenters: 18,
  totalHazards: 7,
  totalEvacuees: 315,
  occupancyRate: 68,
})

const apiFailed = ref(false)
const loadingStats = ref(false)
const updatedAt = ref(new Date())

const displayStats = computed(() => stats.value)
const lastUpdated = computed(() => {
  return updatedAt.value.toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit',
  })
})

const goToLogin = () => {
  router.push('/auth/login')
}

const goToRegister = () => {
  router.push('/auth/register')
}

const scrollToSection = (id) => {
  const el = document.getElementById(id)
  if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

const fetchPublicStats = async () => {
  loadingStats.value = true

  try {
    const [centersRes, hazardsRes] = await Promise.allSettled([
      axios.get('/api/public/centers/summary/'),
      axios.get('/api/public/hazards/summary/'),
    ])

    const nextStats = { ...stats.value }

    if (centersRes.status === 'fulfilled' && centersRes.value?.data) {
      const data = centersRes.value.data
      nextStats.totalCenters = data.total_centers ?? nextStats.totalCenters
      nextStats.totalEvacuees = data.total_evacuees ?? nextStats.totalEvacuees
      nextStats.occupancyRate = data.occupancy_rate ?? nextStats.occupancyRate
    }

    if (hazardsRes.status === 'fulfilled' && hazardsRes.value?.data) {
      const data = hazardsRes.value.data
      nextStats.totalHazards = data.total_active_hazards ?? nextStats.totalHazards
    }

    stats.value = nextStats
    updatedAt.value = new Date()
  } catch (error) {
    apiFailed.value = true
    console.warn('Landing page stats fallback in use:', error)
  } finally {
    loadingStats.value = false
  }
}

onMounted(() => {
  fetchPublicStats()
})
</script>

<style scoped>
:global(*) {
  box-sizing: border-box;
}

:global(html) {
  scroll-behavior: smooth;
}

.landing-page {
  position: relative;
  min-height: 100vh;
  overflow: hidden;
  color: #e8f1ff;
  background:
    radial-gradient(circle at 10% 0%, rgba(59, 130, 246, 0.16), transparent 26%),
    radial-gradient(circle at 90% 10%, rgba(34, 211, 238, 0.14), transparent 24%),
    linear-gradient(180deg, #07111f 0%, #0a1628 18%, #081220 42%, #0b1830 72%, #060d17 100%);
}

.bg-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(12px);
  pointer-events: none;
  z-index: 0;
}

.orb-1 {
  width: 420px;
  height: 420px;
  top: -100px;
  left: -120px;
  background: radial-gradient(circle, rgba(37, 99, 235, 0.22), transparent 70%);
}

.orb-2 {
  width: 320px;
  height: 320px;
  top: 520px;
  right: -80px;
  background: radial-gradient(circle, rgba(6, 182, 212, 0.18), transparent 70%);
}

.orb-3 {
  width: 420px;
  height: 420px;
  bottom: 120px;
  left: 10%;
  background: radial-gradient(circle, rgba(59, 130, 246, 0.12), transparent 70%);
}

.grid-overlay {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(148, 163, 184, 0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(148, 163, 184, 0.05) 1px, transparent 1px);
  background-size: 44px 44px;
  mask-image: linear-gradient(180deg, rgba(0, 0, 0, 0.55), rgba(0, 0, 0, 0.1));
  pointer-events: none;
}

.landing-header,
.hero-section,
.content-section,
.cta-section,
.trust-strip,
.contact-section,
.landing-footer {
  position: relative;
  z-index: 1;
  padding-left: 5vw;
  padding-right: 5vw;
}

.landing-header {
  position: sticky;
  top: 0;
  z-index: 30;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding-top: 1rem;
  padding-bottom: 1rem;
  backdrop-filter: blur(18px);
  background: rgba(4, 12, 24, 0.6);
  border-bottom: 1px solid rgba(148, 163, 184, 0.12);
}

.brand {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  cursor: pointer;
}

.brand-mark {
  width: 50px;
  height: 50px;
  border-radius: 16px;
  display: grid;
  place-items: center;
  font-weight: 800;
  font-size: 1.2rem;
  color: white;
  background: linear-gradient(135deg, #2563eb, #22d3ee);
  box-shadow: 0 18px 38px rgba(37, 99, 235, 0.35);
}

.brand h1 {
  margin: 0;
  font-size: 1.05rem;
  color: #f8fbff;
}

.brand p {
  margin: 0.1rem 0 0;
  font-size: 0.82rem;
  color: #9bb4d0;
}

.nav-links,
.nav-actions,
.footer-links,
.hero-actions,
.cta-actions {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  flex-wrap: wrap;
}

.nav-links button,
.footer-links button {
  border: none;
  background: transparent;
  color: #c8d8f0;
  font-weight: 600;
  cursor: pointer;
  padding: 0.55rem 0.8rem;
  border-radius: 999px;
  transition: 0.25s ease;
}

.nav-links button:hover,
.footer-links button:hover {
  background: rgba(37, 99, 235, 0.14);
  color: #ffffff;
}

.hero-section {
  display: grid;
  grid-template-columns: 1.05fr 0.95fr;
  gap: 2.5rem;
  align-items: center;
  padding-top: 5rem;
  padding-bottom: 4.5rem;
}

.eyebrow,
.section-tag,
.status-pill,
.step-number {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 999px;
  font-weight: 700;
}

.eyebrow,
.section-tag {
  width: fit-content;
  font-size: 0.8rem;
  letter-spacing: 0.04em;
  padding: 0.45rem 0.85rem;
  background: rgba(37, 99, 235, 0.16);
  border: 1px solid rgba(96, 165, 250, 0.16);
  color: #90b8ff;
}

.section-tag.light {
  background: rgba(255, 255, 255, 0.12);
  color: #e5f0ff;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.hero-content h2 {
  font-size: clamp(2.7rem, 6vw, 5.1rem);
  line-height: 1.02;
  margin: 1rem 0;
  max-width: 11ch;
  color: #f8fbff;
}

.hero-content h2 span {
  background: linear-gradient(135deg, #7dd3fc, #3b82f6 45%, #8b5cf6 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.hero-text {
  max-width: 640px;
  font-size: 1.06rem;
  line-height: 1.85;
  color: #aabfd8;
  margin-bottom: 1.6rem;
}

.hero-feature-chips {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.9rem;
  margin-top: 1.4rem;
}

.feature-chip {
  display: flex;
  align-items: flex-start;
  gap: 0.8rem;
  padding: 0.95rem 1rem;
  border-radius: 18px;
  background: rgba(11, 24, 48, 0.72);
  border: 1px solid rgba(125, 211, 252, 0.08);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.03), 0 14px 30px rgba(0, 0, 0, 0.2);
}

.feature-chip strong {
  display: block;
  color: #edf5ff;
  margin-bottom: 0.25rem;
  font-size: 0.95rem;
}

.feature-chip p {
  margin: 0;
  font-size: 0.86rem;
  line-height: 1.55;
  color: #97aec7;
}

.chip-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  margin-top: 0.4rem;
  flex-shrink: 0;
  box-shadow: 0 0 16px currentColor;
}

.chip-dot.blue { color: #3b82f6; background: #3b82f6; }
.chip-dot.cyan { color: #22d3ee; background: #22d3ee; }
.chip-dot.orange { color: #f97316; background: #f97316; }
.chip-dot.green { color: #22c55e; background: #22c55e; }

.hero-visual {
  display: flex;
  justify-content: center;
}

.glass-card {
  width: 100%;
  max-width: 620px;
  border-radius: 28px;
  padding: 1.4rem;
  background: linear-gradient(180deg, rgba(9, 20, 37, 0.86), rgba(12, 24, 45, 0.82));
  box-shadow: 0 35px 70px rgba(0, 0, 0, 0.35);
  border: 1px solid rgba(148, 163, 184, 0.12);
  backdrop-filter: blur(18px);
}

.preview-top,
.activity-header,
/* .trust-strip {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
} */

.preview-top h3,
.activity-header h4,
.feature-card h3,
.role-card h3,
.step-card h3,
.cta-card h2,
.contact-card h3 {
  margin: 0;
}

.mini-label {
  margin: 0 0 0.35rem;
  font-size: 0.78rem;
  color: #8ea7c3;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.preview-top h3,
.activity-header h4 {
  color: #f6fbff;
}

.status-pill {
  background: rgba(34, 197, 94, 0.14);
  color: #6ee7b7;
  padding: 0.5rem 0.8rem;
  font-size: 0.85rem;
  border: 1px solid rgba(34, 197, 94, 0.16);
}

.stats-grid,
.feature-grid,
.steps-grid,
.roles-grid,
.contact-grid {
  display: grid;
  gap: 1rem;
}

.stats-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
  margin-top: 1.2rem;
}

.stat-card,
.feature-card,
.step-card,
.role-card,
.contact-card {
  border-radius: 22px;
  padding: 1.1rem;
  background: rgba(9, 18, 34, 0.84);
  border: 1px solid rgba(148, 163, 184, 0.1);
  box-shadow: 0 18px 34px rgba(0, 0, 0, 0.18);
}

.stat-card h4 {
  margin: 0;
  font-size: 1.65rem;
  color: #f8fbff;
}

.stat-card p,
.activity-item p,
.feature-card p,
.step-card p,
.role-card p,
.cta-card p,
.section-heading p,
.landing-footer p,
.contact-card p,
.contact-card li {
  margin: 0.4rem 0 0;
  color: #9cb3ce;
  line-height: 1.65;
}

.stat-card p,
.feature-card p,
.step-card p,
.role-card p,
.contact-card p,
.contact-card li {
  font-size: 0.95rem;
}

.feature-card h3,
.role-card h3,
.step-card h3,
.contact-card h3 {
  color: #eff6ff;
}

.accent-blue { border-top: 4px solid #2563eb; }
.accent-orange { border-top: 4px solid #f97316; }
.accent-green { border-top: 4px solid #22c55e; }
.accent-purple { border-top: 4px solid #8b5cf6; }

.activity-panel {
  margin-top: 1.2rem;
  padding: 1rem;
  border-radius: 22px;
  background: linear-gradient(180deg, rgba(9, 20, 37, 0.95), rgba(6, 16, 31, 0.9));
  border: 1px solid rgba(59, 130, 246, 0.12);
}

.activity-header span {
  font-size: 0.88rem;
  color: #7f9abc;
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 0.9rem;
  margin-top: 1rem;
}

.activity-item {
  display: flex;
  align-items: flex-start;
  gap: 0.8rem;
}

.activity-item strong {
  color: #eef6ff;
}

.dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  margin-top: 0.35rem;
  flex-shrink: 0;
}

.dot.green { background: #22c55e; }
.dot.orange { background: #f97316; }
.dot.blue { background: #3b82f6; }

/* .trust-strip {
  gap: 1rem;
  padding-top: 1.15rem;
  padding-bottom: 1.15rem;
  border-top: 1px solid rgba(148, 163, 184, 0.08);
  border-bottom: 1px solid rgba(148, 163, 184, 0.08);
  background: rgba(3, 10, 20, 0.42);
} */

.trust-item {
  flex: 1;
  min-width: 220px;
}

.trust-item strong {
  display: block;
  margin-bottom: 0.25rem;
  color: #edf5ff;
}

.trust-item span {
  color: #91a8c4;
}

.content-section {
  padding-top: 5rem;
  padding-bottom: 5rem;
}

.alt-bg {
  background: linear-gradient(180deg, rgba(4, 12, 24, 0.25), rgba(10, 20, 38, 0.42));
}

.section-heading {
  max-width: 820px;
  margin-bottom: 2rem;
}

.section-heading.center {
  margin-left: auto;
  margin-right: auto;
  text-align: center;
}

.section-heading h2 {
  margin: 1rem 0 0.85rem;
  font-size: clamp(2rem, 4vw, 3rem);
  line-height: 1.15;
  color: #f8fbff;
}

.feature-grid {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.feature-card,
.role-card,
.step-card,
.contact-card,
.feature-chip,
.stat-card {
  transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
}

.feature-card:hover,
.role-card:hover,
.step-card:hover,
.stat-card:hover,
.contact-card:hover,
.feature-chip:hover {
  transform: translateY(-4px);
  box-shadow: 0 24px 42px rgba(0, 0, 0, 0.28);
  border-color: rgba(96, 165, 250, 0.18);
}

.feature-icon {
  width: 54px;
  height: 54px;
  border-radius: 18px;
  display: grid;
  place-items: center;
  font-size: 1.4rem;
  margin-bottom: 1rem;
  background: linear-gradient(135deg, rgba(37, 99, 235, 0.18), rgba(34, 211, 238, 0.16));
}

.steps-grid {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.step-card {
  position: relative;
  overflow: hidden;
}

.step-number {
  width: fit-content;
  padding: 0.45rem 0.7rem;
  font-size: 0.85rem;
  margin-bottom: 1rem;
  background: rgba(37, 99, 235, 0.16);
  color: #90b8ff;
  border: 1px solid rgba(96, 165, 250, 0.16);
}

.roles-grid,
.contact-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.cta-section {
  padding-top: 2rem;
  padding-bottom: 5rem;
}

.cta-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1.5rem;
  padding: 2rem;
  border-radius: 30px;
  color: white;
  background: linear-gradient(135deg, #103b8d, #1d4ed8 45%, #0ea5e9 100%);
  box-shadow: 0 30px 60px rgba(0, 0, 0, 0.28);
  border: 1px solid rgba(255, 255, 255, 0.14);
}

.cta-card p {
  color: rgba(255, 255, 255, 0.88);
}

.contact-section {
  padding-top: 0.5rem;
  padding-bottom: 3rem;
}

.contact-shell {
  padding: 2rem;
  border-radius: 32px;
  background: linear-gradient(180deg, rgba(7, 17, 31, 0.92), rgba(10, 18, 34, 0.86));
  border: 1px solid rgba(148, 163, 184, 0.12);
  box-shadow: 0 26px 54px rgba(0, 0, 0, 0.24);
}

.contact-intro {
  max-width: 760px;
  margin-bottom: 1.5rem;
}

.contact-intro h2 {
  margin: 1rem 0 0.7rem;
  font-size: clamp(1.8rem, 4vw, 2.7rem);
  color: #f8fbff;
}

.contact-grid {
  gap: 1rem;
}

.contact-card ul {
  list-style: none;
  padding: 0;
  margin: 0.5rem 0 0;
}

.contact-card li + li {
  margin-top: 0.55rem;
}

.contact-card strong {
  color: #eef6ff;
}

.contact-label {
  display: inline-flex;
  width: fit-content;
  padding: 0.3rem 0.6rem;
  border-radius: 999px;
  font-size: 0.78rem;
  color: #8ab4ff;
  background: rgba(37, 99, 235, 0.14);
  border: 1px solid rgba(96, 165, 250, 0.14);
}

.feature-contact {
  background: linear-gradient(180deg, rgba(14, 28, 51, 0.98), rgba(7, 17, 31, 0.92));
}

.landing-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding-top: 1.5rem;
  padding-bottom: 2rem;
  border-top: 1px solid rgba(148, 163, 184, 0.08);
}

.landing-footer h3 {
  margin: 0;
  color: #f8fbff;
}

.btn {
  border: none;
  border-radius: 999px;
  padding: 0.8rem 1.2rem;
  font-weight: 700;
  cursor: pointer;
  transition: 0.25s ease;
}

.btn.large {
  padding: 0.95rem 1.4rem;
  font-size: 1rem;
}

.btn.primary {
  color: white;
  background: linear-gradient(135deg, #2563eb, #0ea5e9);
  box-shadow: 0 18px 34px rgba(37, 99, 235, 0.34);
}

.btn.primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 24px 40px rgba(37, 99, 235, 0.38);
}

.btn.secondary,
.btn.ghost {
  background: rgba(10, 20, 38, 0.72);
  color: #e8f1ff;
  border: 1px solid rgba(96, 165, 250, 0.16);
}

.btn.light {
  background: white;
  color: #0f3f8c;
}

.btn.outline-light {
  background: transparent;
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.38);
}

.btn.secondary:hover,
.btn.ghost:hover,
.btn.light:hover,
.btn.outline-light:hover {
  transform: translateY(-2px);
}

@media (max-width: 1180px) {
  .hero-section,
  .cta-card {
    grid-template-columns: 1fr;
    flex-direction: column;
  }

  .feature-grid,
  .roles-grid,
  .contact-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .steps-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .landing-header {
    flex-wrap: wrap;
  }
}

@media (max-width: 860px) {
  .hero-feature-chips,
  .feature-grid,
  .steps-grid,
  .roles-grid,
  .contact-grid,
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .hero-content h2 {
    max-width: 100%;
  }
}

@media (max-width: 760px) {
  .landing-header,
  .landing-footer,
  .trust-strip {
    flex-direction: column;
    align-items: flex-start;
  }

  .nav-links {
    width: 100%;
    overflow-x: auto;
    padding-bottom: 0.2rem;
    flex-wrap: nowrap;
  }

  .nav-links::-webkit-scrollbar {
    height: 6px;
  }

  .nav-links::-webkit-scrollbar-thumb {
    background: rgba(148, 163, 184, 0.24);
    border-radius: 999px;
  }

  .nav-actions,
  .hero-actions,
  .cta-actions,
  .footer-links {
    width: 100%;
  }

  .nav-actions .btn,
  .hero-actions .btn,
  .cta-actions .btn {
    width: 100%;
    justify-content: center;
  }

  .hero-section {
    padding-top: 2.8rem;
  }


  .cta-card,
  .contact-shell {
    padding: 1.3rem;
  }
}




.contact-section {
  padding-top: 0.5rem;
  padding-bottom: 3rem;
}

.contact-shell {
  padding: 2rem;
  border-radius: 32px;
  background: linear-gradient(180deg, rgba(7, 17, 31, 0.92), rgba(10, 18, 34, 0.86));
  border: 1px solid rgba(148, 163, 184, 0.12);
  box-shadow: 0 26px 54px rgba(0, 0, 0, 0.24);
}

.contact-intro {
  max-width: 760px;
  margin-bottom: 1.5rem;
}

.contact-intro h2 {
  margin: 1rem 0 0.7rem;
  font-size: clamp(1.8rem, 4vw, 2.7rem);
  color: #f8fbff;
}

.contact-grid {
  gap: 1rem;
}

.contact-grid.redesigned {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
  align-items: stretch;
}

.wide-card {
  grid-column: 1 / -1;
}

.primary-contact-card {
  background: linear-gradient(135deg, rgba(17, 39, 71, 0.98), rgba(7, 17, 31, 0.92));
}

.contact-card {
  border-radius: 22px;
  padding: 1.2rem;
  background: rgba(9, 18, 34, 0.84);
  border: 1px solid rgba(148, 163, 184, 0.1);
  box-shadow: 0 18px 34px rgba(0, 0, 0, 0.18);
  transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
}

.contact-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 24px 42px rgba(0, 0, 0, 0.28);
  border-color: rgba(96, 165, 250, 0.18);
}



.contact-kicker {
margin-bottom: 30px;
  /* margin: 0 0 0.45rem; */
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #8ab4ff;
}

.contact-summary {
  margin: 0.55rem 0 0;
  max-width: 760px;
  color: #9eb6d1;
  line-height: 1.65;
}

.contact-badge {
  align-self: flex-start;
  white-space: nowrap;

  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.38rem 0.72rem;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 700;
  color: #dbeafe;
  background: rgba(37, 99, 235, 0.16);
  border: 1px solid rgba(96, 165, 250, 0.16);
  white-space: nowrap;
}

.primary-contact-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.contact-details-list {
  display: flex;
  flex-direction: column;
  gap: 0.95rem;
  margin-top: 1rem;
}

.contact-details-list.three-up {
 display: grid;
 grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
 gap: 0.95rem;
}

.contact-details-list.compact {
  gap: 0.85rem;
}

.preview-top h3,
.contact-hero h3 {
  line-height: 1.2;
  max-width: 18ch;
}

.contact-summary {
  max-width: 60ch;
  line-height: 1.65;
}

.contact-line {
  display: flex;
  align-items: flex-start;
  gap: 0.85rem;
  padding: 0.95rem 1rem;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(148, 163, 184, 0.08);
}

.contact-icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: grid;
  place-items: center;
  flex-shrink: 0;
  font-size: 1rem;
  background: linear-gradient(135deg, rgba(37, 99, 235, 0.22), rgba(34, 211, 238, 0.16));
}

.contact-line label {
  display: block;
  margin-bottom: 0.3rem;
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: #8ea7c3;
}

.contact-line a,
.contact-line p {
  display: block;
  margin: 0;
  line-height: 1.55;
}

.contact-line a {
  color: #f8fbff;
  font-weight: 700;
  text-decoration: none;
  word-break: break-word;
}

.contact-line a:hover {
  color: #8ec5ff;
}

.contact-actions {
  display: flex;
  gap: 0.8rem;
  flex-wrap: wrap;
  margin-top: 0.2rem;
}

.contact-btn {
  text-decoration: none;
}

.dark-outline {
  background: transparent;
  color: #eef6ff;
  border: 1px solid rgba(255, 255, 255, 0.18);
}

.support-card {
  min-height: 100%;
}

.contact-note-list {
  display: flex;
  flex-direction: column;
  gap: 0.9rem;
  margin-top: 1rem;
}

.contact-note-list p {
  margin: 0;
  color: #9cb3ce;
  line-height: 1.7;
}

.contact-note-list strong {
  color: #eef6ff;
}


.preview-top,
.contact-hero {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}

.preview-top > div,
.contact-hero > div {
  flex: 1 1 260px;
  min-width: 0;
}



.status-pill,
.contact-badge {
  flex: 0 0 auto;
  white-space: nowrap;
  align-self: flex-start;
}

.preview-top {
  margin-bottom: 1rem;
}

.contact-hero {
  margin-bottom: 1rem;
}




@media (max-width: 860px) {
  .contact-grid.redesigned {
    grid-template-columns: 1fr;
  }

  .wide-card {
    grid-column: auto;
  }

  .contact-details-list.three-up {
    grid-template-columns: 1fr;
  }

  .contact-hero {
    flex-direction: column;
    align-items: flex-start;
  }
}

@media (max-width: 760px) {
  .contact-shell {
    padding: 1.3rem;
  }

  .contact-actions {
    flex-direction: column;
  }

  .contact-actions .btn,
  .contact-actions .contact-btn {
    margin-top: 70px;
    width: 100%;
    text-align: center;
    justify-content: center;
  }
}

@media (max-width: 768px) {
  .preview-top,
  .contact-hero {
    flex-direction: column;
    align-items: flex-start;
  }

  .status-pill,
  .contact-badge {
    align-self: flex-start;
  }
}
</style>
