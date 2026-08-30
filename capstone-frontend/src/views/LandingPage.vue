<template>
  <div class="landing-page">
    <div class="bg-orb orb-1"></div>
    <div class="bg-orb orb-2"></div>
    <div class="bg-orb orb-3"></div>
    <div class="grid-overlay"></div>

    <!-- NAVBAR -->
<<<<<<< HEAD
    <header class="landing-header">
      <div class="brand" @click="scrollToSection('hero')">
        <img :src="saferouteLogo" alt="SafeRoute Logo" class="logo-img" />
        <div>
          <h1>SafeRoute</h1>
          <p>Evacuation Monitoring System</p>
        </div>
      </div>

      <nav class="nav-links">
        <button @click="scrollToSection('features')">Features</button>
        <button @click="scrollToSection('about-pdrrmo')">About PDRRMO</button>
        <button @click="scrollToSection('donate')">Donate</button>
        <button @click="scrollToSection('how-it-works')">How it Works</button>
        <button @click="scrollToSection('roles')">Users</button>
        <button @click="scrollToSection('contact')">Contact</button>
      </nav>

      <div class="nav-actions">
        <button class="btn ghost" @click="goToLogin">Login</button>
        <button class="btn primary" @click="goToRegister">Get Started</button>
      </div>
    </header>
=======
    <IndexNavBar />
>>>>>>> 30e6c4e2eb4ae2dde2f6a87f3f18476c293961df

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

    <!-- ABOUT PDRRMO -->
    <section id="about-pdrrmo" class="content-section">
      <div class="section-heading center">
        <span class="section-tag">About Our Partner</span>
        <h2>Powered by the PDRRMO</h2>
        <p>
          SafeRoute is built with and for the Provincial Disaster Risk Reduction and Management Office (PDRRMO),
          which leads disaster preparedness and emergency response for the province.
        </p>
      </div>

      <p class="placeholder-note">
        ⚠️ Sample content — the items below are the PDRRMO's general, publicly known mandate.
        Replace with the client's actual programs once confirmed (client is available starting Sept 7).
      </p>

      <div class="feature-grid">
        <article class="feature-card">
          <div class="feature-icon">🛡️</div>
          <h3>Disaster Preparedness</h3>
          <p>Community drills, hazard mapping, and readiness planning before disasters strike.</p>
        </article>
        <article class="feature-card">
          <div class="feature-icon">🚑</div>
          <h3>Emergency Response</h3>
          <p>Coordinating search and rescue, relief operations, and on-ground response teams.</p>
        </article>
        <article class="feature-card">
          <div class="feature-icon">📚</div>
          <h3>Public Training</h3>
          <p>Training barangay officials, volunteers, and citizens on disaster risk reduction.</p>
        </article>
      </div>

      <div class="gallery-heading">
        <h3>PDRRMO Through the Years</h3>
        <p>Trainings, relief operations, and community drives from the field.</p>
      </div>
      <PdrrmoGallery :slides="pdrrmoGallerySlides" />
    </section>

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

    <!-- DONATION DRIVE PREVIEW -->
    <section id="donate" class="content-section alt-bg">
      <div class="section-heading center">
        <span class="section-tag">Donation Drive</span>
        <h2>Help evacuation centers stay stocked and ready</h2>
        <p>
          These are current needs across active evacuation centers. Anyone can pledge a donation — no account required.
        </p>
      </div>

      <div class="donate-layout">
        <div class="donate-summary">
          <div class="donate-stat">
            <h4>{{ donationSummary.openNeeds }}</h4>
            <p>Open Needs</p>
          </div>
          <div class="donate-stat urgent">
            <h4>{{ donationSummary.urgentNeeds }}</h4>
            <p>Urgent Needs</p>
          </div>
        </div>

        <div class="donate-needs-card">
          <h3>Most needed right now</h3>
          <ul class="donate-needs-list">
            <li v-for="need in topNeeds" :key="need.id">
              <span class="need-name">{{ need.item_name }}</span>
              <span class="need-qty">{{ need.remaining_quantity }} {{ need.unit }} remaining</span>
              <span class="need-pill" :class="need.priority.toLowerCase()">{{ need.priority }}</span>
            </li>
          </ul>

          <button class="btn primary large donate-cta" @click="openPledgeModal">
            Pledge a Donation
          </button>
          <p class="donate-note">
            No sign-up needed — click to schedule an in-kind donation directly with PDRRMO.
          </p>
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

    <!-- CTA
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
    </section> -->

    <!-- CONTACT / FOOTER -->
    <section id="contact" class="contact-section">
      <div class="contact-shell">
        <div class="contact-intro">
          <span class="section-tag">Contact & Support</span>
          <h2>Need assistance with SafeRoute?</h2>
        </div>

        <div class="contact-grid three-division-grid">
          <article class="contact-card primary-contact-card">
            <div class="contact-card-top">
              <div>
                <p class="contact-kicker">{{ contactInfo.researchPlanning.label }}</p>
                <h3>Research &amp; Planning</h3>
              </div>
            </div>

            <div class="contact-details-list">
              <div class="contact-line">
                <span class="contact-icon">📘</span>
                <div>
                  <label>Facebook</label>
                  <p>{{ contactInfo.researchPlanning.facebook }}</p>
                </div>
              </div>
              <div class="contact-line">
                <span class="contact-icon">✉️</span>
                <div>
                  <label>Email</label>
                  <a :href="`mailto:${contactInfo.researchPlanning.email}`">
                    {{ contactInfo.researchPlanning.email }}
                  </a>
                </div>
              </div>
              <div class="contact-line">
                <span class="contact-icon">📞</span>
                <div>
                  <label>Phone</label>
                  <a :href="`tel:${contactInfo.researchPlanning.phoneLink}`">
                    {{ contactInfo.researchPlanning.phoneDisplay }}
                  </a>
                </div>
              </div>
            </div>


          </article>

          <article class="contact-card">
            <p class="contact-kicker">{{ contactInfo.adminTraining.label }}</p>
            <h3>Administration &amp; Training</h3>

            <div class="contact-details-list compact">
              <div class="contact-line">
                <span class="contact-icon">📘</span>
                <div>
                  <label>Facebook</label>
                  <p>{{ contactInfo.adminTraining.facebook }}</p>
                </div>
              </div>
              <div class="contact-line">
                <span class="contact-icon">✉️</span>
                <div>
                  <label>Email</label>
                  <a :href="`mailto:${contactInfo.adminTraining.email}`">
                    {{ contactInfo.adminTraining.email }}
                  </a>
                </div>
              </div>
              <div class="contact-line">
                <span class="contact-icon">📞</span>
                <div>
                  <label>Phone</label>
                  <a :href="`tel:${contactInfo.adminTraining.phoneLink}`">
                    {{ contactInfo.adminTraining.phoneDisplay }}
                  </a>
                </div>
              </div>
            </div>
          </article>

          <article class="contact-card">
            <p class="contact-kicker">{{ contactInfo.opsWarning.label }}</p>
            <h3>Operations &amp; Warning</h3>

            <div class="contact-details-list compact">
              <div class="contact-line">
                <span class="contact-icon">📘</span>
                <div>
                  <label>Facebook</label>
                  <p>{{ contactInfo.opsWarning.facebook }}</p>
                </div>
              </div>
              <div class="contact-line">
                <span class="contact-icon">✉️</span>
                <div>
                  <label>Email</label>
                  <a :href="`mailto:${contactInfo.opsWarning.email}`">
                    {{ contactInfo.opsWarning.email }}
                  </a>
                </div>
              </div>
              <div class="contact-line">
                <span class="contact-icon">📞</span>
                <div>
                  <label>Hotlines</label>
                  <a :href="`tel:${contactInfo.opsWarning.phoneLink}`">{{ contactInfo.opsWarning.phoneDisplay }}</a>
                  <a :href="`tel:${contactInfo.opsWarning.phoneLink2}`">{{ contactInfo.opsWarning.phoneDisplay2 }}</a>
                </div>
              </div>
            </div>
          </article>

          <article class="contact-card wide-card">
            <p class="contact-kicker">Office</p>
            <h3>{{ contactInfo.office }}</h3>
            <div class="contact-details-list compact">
              <div class="contact-line">
                <span class="contact-icon">🕒</span>
                <div>
                  <label>Office Hours</label>
                  <p>{{ contactInfo.hours }}</p>
                </div>
              </div>
            </div>
          </article>
        </div>
      </div>
    </section>

    <!-- IN-KIND GUEST PLEDGE MODAL -->
    <div v-if="showModal" class="modal-backdrop" @click.self="closePledgeModal">
      <div class="modal-card glass-card">
        <button class="modal-close" @click="closePledgeModal">&times;</button>

        <!-- FORM STATE -->
        <div v-if="!pledgeSuccess">
          <div class="modal-header">
            <span class="section-tag">Public In-Kind Pledge</span>
            <h3>Schedule a Goods Donation</h3>
            <p>Pledge items directly to PDRRMO without creating an account.</p>
          </div>

          <form @submit.prevent="submitPledge" class="pledge-form">
            <div class="form-group">
              <label>Select Item to Donate *</label>
                <select v-model="pledgeForm.need_id" required class="form-input">
                  <option 
                    v-for="need in (donationNeeds.length ? donationNeeds : topNeeds)" 
                    :key="need.id" 
                    :value="need.id"
                  >
                    {{ need.item_name }} ({{ need.remaining_quantity || need.quantity }} {{ need.unit }} needed)
                  </option>
                </select>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label>Your Name *</label>
                <input v-model="pledgeForm.donor_name" type="text" required placeholder="e.g. Juan Cruz" class="form-input" />
              </div>

              <div class="form-group">
                <label>Contact Number *</label>
                <input v-model="pledgeForm.contact_number" type="tel" required placeholder="e.g. 09171234567" class="form-input" />
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label>Quantity to Pledge *</label>
                <input v-model.number="pledgeForm.quantity" type="number" min="1" required class="form-input" />
              </div>

              <div class="form-group">
                <label>Target Drop-off Date *</label>
                <input v-model="pledgeForm.dropoff_date" type="date" required class="form-input" />
              </div>
            </div>

            <div class="form-group">
              <label>Notes / Remarks (Optional)</label>
              <textarea v-model="pledgeForm.notes" rows="2" placeholder="e.g., Will bring directly to main office." class="form-input"></textarea>
            </div>

            <div class="modal-actions">
              <button type="button" class="btn ghost" @click="closePledgeModal">Cancel</button>
              <button type="submit" class="btn primary" :disabled="submittingPledge">
                {{ submittingPledge ? 'Submitting...' : 'Submit Pledge' }}
              </button>
            </div>
          </form>
        </div>

        <!-- SUCCESS CONFIRMATION STATE -->
        <div v-else class="pledge-success-view">
          <div class="success-icon">🎉</div>
          <h3>Pledge Submitted Successfully!</h3>
          <p class="ref-code">Reference Code: <strong>{{ pledgeRefCode }}</strong></p>

          <p class="success-text">
            Thank you for your generous pledge! Please bring the items to the main PDRRMO office on your selected date.
            Our team will verify and receive your items upon drop-off.
          </p>

          <div class="modal-actions center">
            <button class="btn primary" @click="closePledgeModal">Done</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import api from '@/services/api'
import saferouteLogo from '@/assets/saferoute-logo.png'
import PdrrmoGallery from '@/components/pdrrmo/PdrrmoGallery.vue'
import day1Photo1 from '@/assets/pdrrmo-gallery/bls-sfa-day1-1.jpg'
import day1Photo2 from '@/assets/pdrrmo-gallery/bls-sfa-day1-2.jpg'
import day1Photo3 from '@/assets/pdrrmo-gallery/bls-sfa-day1-3.jpg'
import day1Photo4 from '@/assets/pdrrmo-gallery/bls-sfa-day1-4.jpg'
import day2Photo1 from '@/assets/pdrrmo-gallery/bls-sfa-day2-1.jpg'
import day2Photo2 from '@/assets/pdrrmo-gallery/bls-sfa-day2-2.jpg'
import day2Photo3 from '@/assets/pdrrmo-gallery/bls-sfa-day2-3.jpg'
import day2Photo4 from '@/assets/pdrrmo-gallery/bls-sfa-day2-4.jpg'
import reliefRepacking1 from '@/assets/pdrrmo-gallery/relief-repacking-1.jpg'
import reliefRepacking2 from '@/assets/pdrrmo-gallery/relief-repacking-2.jpg'
import reliefRepacking3 from '@/assets/pdrrmo-gallery/relief-repacking-3.jpg'
import reliefRepacking4 from '@/assets/pdrrmo-gallery/relief-repacking-4.jpg'
import floodRescue1 from '@/assets/pdrrmo-gallery/flood-rescue-1.jpg'
import floodRescue2 from '@/assets/pdrrmo-gallery/flood-rescue-2.jpg'
import floodRescue3 from '@/assets/pdrrmo-gallery/flood-rescue-3.jpg'
import floodRescue4 from '@/assets/pdrrmo-gallery/flood-rescue-4.jpg'

const router = useRouter()
const route = useRoute()

const donationNeeds = ref([]);

const fetchDonationNeeds = async () => {
  try {
    const res = await fetch('http://127.0.0.1:8000/api/evac_centers/donation-needs/');
    if (res.ok) {
      const data = await res.json();
      // Unpacks paginated response results or defaults to array
      donationNeeds.value = Array.isArray(data) ? data : (data.results || []);
    }
  } catch (err) {
    console.error('Failed to fetch public needs:', err);
  }
};




const contactInfo = {
  researchPlanning: {
    label: 'Research and Planning Division',
    facebook: 'OrminPdrrmo ResearchPlanning Div',
    email: 'orminpdrrmoresplandiv@gmail.com',
    phoneDisplay: '+63 948 154 1775',
    phoneLink: '+639481541775',
  },
  adminTraining: {
    label: 'Administration and Training Division',
    facebook: 'Pdrrmo OrMin',
    email: 'pdrrmoormin@yahoo.com',
    phoneDisplay: '+63 916 220 1847',
    phoneLink: '+639162201847',
  },
  opsWarning: {
    label: 'Operations and Warning Division',
    facebook: 'OpsdivPdrrmo OrMin',
    email: 'opswarningdivpdrrmo@gmail.com',
    phoneDisplay: '+63 920 951 3690',
    phoneLink: '+639209513690',
    phoneDisplay2: '+63 948 146 0382',
    phoneLink2: '+639481460382',
  },
  office: 'Provincial Disaster Risk Reduction and Management Office — Oriental Mindoro',
  hours: 'Monday to Friday • 8:00 AM – 5:00 PM',
}

const stats = ref({
  totalCenters: 18,
  totalHazards: 7,
  totalEvacuees: 315,
  occupancyRate: 68,
})

const animatedStats = ref({ totalCenters: 0, totalHazards: 0, totalEvacuees: 0, occupancyRate: 0 })
const apiFailed = ref(false)
const loadingStats = ref(false)
const updatedAt = ref(new Date())

const displayStats = computed(() => animatedStats.value)
const lastUpdated = computed(() => {
  return updatedAt.value.toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit',
  })
})

const animateStatsTo = (target) => {
  const start = { ...animatedStats.value }
  const duration = 900
  const startTime = performance.now()

  const tick = (now) => {
    const progress = Math.min((now - startTime) / duration, 1)
    const eased = 1 - Math.pow(1 - progress, 3)

    animatedStats.value = {
      totalCenters: Math.round(start.totalCenters + (target.totalCenters - start.totalCenters) * eased),
      totalHazards: Math.round(start.totalHazards + (target.totalHazards - start.totalHazards) * eased),
      totalEvacuees: Math.round(start.totalEvacuees + (target.totalEvacuees - start.totalEvacuees) * eased),
      occupancyRate: Math.round(start.occupancyRate + (target.occupancyRate - start.occupancyRate) * eased),
    }

    if (progress < 1) requestAnimationFrame(tick)
  }

  requestAnimationFrame(tick)
}

watch(stats, (newVal) => animateStatsTo(newVal), { immediate: true, deep: true })

// ---- Public donation drive data ----
const donationSummary = ref({
  openNeeds: 12,
  urgentNeeds: 3,
})
const topNeeds = ref([
  { id: 1, item_name: 'Bottled Water', unit: 'packs', remaining_quantity: 80, priority: 'URGENT' },
  { id: 2, item_name: 'Canned Goods', unit: 'boxes', remaining_quantity: 45, priority: 'HIGH' },
  { id: 3, item_name: 'Hygiene Kits', unit: 'pcs', remaining_quantity: 30, priority: 'MEDIUM' },
])
const donationDataFailed = ref(false)
const usingLiveDonationData = ref(false)

const PRIORITY_ORDER = { URGENT: 0, HIGH: 1, MEDIUM: 2, LOW: 3 }

const fetchPublicDonationSummary = async () => {
  try {
    const res = await api.get('evac_centers/donation-needs/')
    const needs = Array.isArray(res.data) ? res.data : res.data.results || []

    if (needs.length > 0) {
      donationSummary.value = {
        openNeeds: needs.filter((n) => ['OPEN', 'PARTIALLY_FULFILLED'].includes(n.status)).length,
        urgentNeeds: needs.filter((n) => n.priority === 'URGENT').length,
      }

      topNeeds.value = [...needs]
        .filter((n) => ['OPEN', 'PARTIALLY_FULFILLED'].includes(n.status))
        .sort((a, b) => (PRIORITY_ORDER[a.priority] ?? 9) - (PRIORITY_ORDER[b.priority] ?? 9))
        .slice(0, 3)

      usingLiveDonationData.value = true
    }
  } catch (error) {
    donationDataFailed.value = true
    console.warn('Public donation summary: live endpoint unavailable, showing sample numbers.', error)
  }
}

// ---- Guest Pledge Modal Logic ----
const showModal = ref(false)
const submittingPledge = ref(false)
const pledgeSuccess = ref(false)
const pledgeRefCode = ref('')

const pledgeForm = ref({
  need_id: null,
  donor_name: '',
  contact_number: '',
  quantity: 1,
  dropoff_date: '',
  notes: '',
})

const openPledgeModal = () => {
  if (topNeeds.value.length > 0) {
    pledgeForm.value.need_id = topNeeds.value[0].id
  }
  pledgeForm.value.dropoff_date = new Date(Date.now() + 86400000).toISOString().split('T')[0]
  showModal.value = true
}

const closePledgeModal = () => {
  showModal.value = false
  pledgeSuccess.value = false
  pledgeForm.value = {
    need_id: null,
    donor_name: '',
    contact_number: '',
    quantity: 1,
    dropoff_date: '',
    notes: '',
  }
}

const submitPledge = async () => {
  submittingPledge.value = true
  try {
    const needsArray = Array.isArray(donationNeeds.value) && donationNeeds.value.length 
      ? donationNeeds.value 
      : topNeeds.value

    const targetId = pledgeForm.value.need_id || pledgeForm.value.need
    const selectedNeed = needsArray.find(n => n.id == targetId)

    // Ensure center is valid integer (fallback to 1 if missing on mock items)
    const centerId = selectedNeed?.center || selectedNeed?.evacuation_center || pledgeForm.value.center || 1

    const payload = {
      need: targetId ? parseInt(targetId) : null,
      center: parseInt(centerId),
      donor_name: pledgeForm.value.donor_name,
      contact_number: pledgeForm.value.contact_number,
      quantity: parseInt(pledgeForm.value.quantity) || 1,
      dropoff_date: pledgeForm.value.dropoff_date,
      notes: pledgeForm.value.notes || '',
      item_name: selectedNeed?.item_name || 'Donated Item',
      category: selectedNeed?.category || 'FOOD',
      status: 'PLEDGED'
    }

    const res = await fetch('http://127.0.0.1:8000/api/evac_centers/donations/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })

    if (!res.ok) {
      const errorData = await res.json()
      throw new Error(JSON.stringify(errorData))
    }

    const data = await res.json()
    pledgeRefCode.value = data?.reference_code || `PLG-${Math.floor(1000 + Math.random() * 9000)}`
    pledgeSuccess.value = true
  } catch (error) {
    console.error('Failed to submit pledge:', error)
    alert('Failed to submit donation pledge. Please check the form data.')
  } finally {
    submittingPledge.value = false
  }
}

// ---- PDRRMO photo gallery ----
const pdrrmoGallerySlides = ref([
  { id: 1, image: day1Photo1, category: 'Training', year: 'Day 1', title: 'BLS & SFA Refresher Training', description: 'MDRRMO Naujan\'s Refresher Course on Basic Life Support and Standard First Aid.' },
  { id: 2, image: day1Photo2, category: 'Training', year: 'Day 1', title: 'BLS & SFA Refresher Training', description: 'Small-group discussions building emergency response knowledge.' },
  { id: 3, image: day1Photo3, category: 'Training', year: 'Day 1', title: 'BLS & SFA Refresher Training', description: 'Hands-on CPR and AED practice as part of the first-day sessions.' },
  { id: 4, image: day1Photo4, category: 'Training', year: 'Day 1', title: 'BLS & SFA Refresher Training', description: 'Facilitators walking participants through learning objectives.' },
  { id: 5, image: day2Photo1, category: 'Training', year: 'Day 2', title: 'Skills in Action', description: 'Return demonstration day for 44 MDRRMO Naujan personnel.' },
  { id: 6, image: day2Photo2, category: 'Training', year: 'Day 2', title: 'Skills in Action', description: 'Participants demonstrating CPR, AED use, and rescue breathing.' },
  { id: 7, image: day2Photo3, category: 'Training', year: 'Day 2', title: 'Skills in Action', description: 'Infant CPR and rescue breathing technique practice.' },
  { id: 8, image: day2Photo4, category: 'Training', year: 'Day 2', title: 'Skills in Action', description: 'All 44 participants successfully completed the return demonstration.' },
  { id: 9, image: reliefRepacking1, category: 'Operations', year: 'Kapit-Bisig', title: 'Relief Goods Repacking', description: 'Repacking relief goods for families affected by flooding.' },
  { id: 10, image: reliefRepacking2, category: 'Operations', year: 'Kapit-Bisig', title: 'Relief Goods Repacking', description: 'Volunteers and responders working side by side.' },
  { id: 11, image: reliefRepacking3, category: 'Operations', year: 'Kapit-Bisig', title: 'Relief Goods Repacking', description: 'Sacks of rice and repacked goods staged for distribution.' },
  { id: 12, image: reliefRepacking4, category: 'Operations', year: 'Kapit-Bisig', title: 'Relief Goods Repacking', description: 'Joint effort among PDRRMO and partner agencies.' },
  { id: 13, image: floodRescue1, category: 'Operations', year: 'Flood Response', title: 'Medical Rescue Amid Flooding', description: 'PDRRMO rescue personnel assist a resident onto a rescue vehicle.' },
  { id: 14, image: floodRescue2, category: 'Operations', year: 'Flood Response', title: 'Medical Rescue Amid Flooding', description: 'Rescue teams coordinate at an ambulance transport.' },
  { id: 15, image: floodRescue3, category: 'Operations', year: 'Flood Response', title: 'Medical Rescue Amid Flooding', description: 'Responders navigate a flooded roadway.' },
  { id: 16, image: floodRescue4, category: 'Operations', year: 'Flood Response', title: 'Medical Rescue Amid Flooding', description: 'PDRRMO rescue swimmers gear up before deployment.' },
])

const goToLogin = () => router.push('/auth/login')
const goToRegister = () => router.push('/auth/register')

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
  fetchPublicDonationSummary()
})
</script>

<style scoped>
:global(*) {
  box-sizing: border-box;
}

:global(html) {
  scroll-behavior: smooth;
}

:global(body) {
  overflow-x: hidden;
}

.landing-page {
  --sr-text: #e8f1ff;
  --sr-heading: #f8fbff;
  --sr-text-muted: #9cb3ce;
  --sr-text-faint: #8ea7c3;
  --sr-nav-link: #c8d8f0;
  --sr-accent-text: #90b8ff;
  --sr-accent-text-hover: #8ec5ff;
  --sr-badge-text: #dbeafe;

  --sr-card-bg: rgba(9, 18, 34, 0.84);
  --sr-panel-bg-1: rgba(9, 20, 37, 0.95);
  --sr-panel-bg-2: rgba(6, 16, 31, 0.9);
  --sr-glass-bg-1: rgba(9, 20, 37, 0.86);
  --sr-glass-bg-2: rgba(12, 24, 45, 0.82);
  --sr-chip-bg: rgba(11, 24, 48, 0.72);
  --sr-shell-bg-1: rgba(7, 17, 31, 0.92);
  --sr-shell-bg-2: rgba(10, 18, 34, 0.86);
  --sr-primary-card-bg-1: rgba(17, 39, 71, 0.98);
  --sr-nav-bg: rgba(4, 12, 24, 0.6);
  --sr-btn-secondary-bg: rgba(10, 20, 38, 0.72);

  --sr-border: rgba(148, 163, 184, 0.12);
  --sr-border-soft: rgba(148, 163, 184, 0.1);
  --sr-border-faint: rgba(148, 163, 184, 0.08);
  --sr-border-accent: rgba(96, 165, 250, 0.16);
  --sr-border-accent-hover: rgba(96, 165, 250, 0.18);
  --sr-chip-border: rgba(125, 211, 252, 0.08);
  --sr-panel-border: rgba(59, 130, 246, 0.12);

  --sr-shadow-soft: rgba(0, 0, 0, 0.18);
  --sr-shadow-med: rgba(0, 0, 0, 0.24);
  --sr-shadow-strong: rgba(0, 0, 0, 0.35);

  --sr-page-bg:
    radial-gradient(circle at 10% 0%, rgba(59, 130, 246, 0.16), transparent 26%),
    radial-gradient(circle at 90% 10%, rgba(34, 211, 238, 0.14), transparent 24%),
    linear-gradient(180deg, #07111f 0%, #0a1628 18%, #081220 42%, #0b1830 72%, #060d17 100%);

  position: relative;
  min-height: 100vh;
  color: var(--sr-text);
  background: var(--sr-page-bg);
  transition: background 0.2s ease, color 0.2s ease;
}

[data-theme="light"] .landing-page {
  --sr-text: #1e293b;
  --sr-heading: #0f172a;
  --sr-text-muted: #475569;
  --sr-text-faint: #64748b;
  --sr-nav-link: #334155;
  --sr-accent-text: #2563eb;
  --sr-accent-text-hover: #1d4ed8;
  --sr-badge-text: #1d4ed8;

  --sr-card-bg: rgba(255, 255, 255, 0.92);
  --sr-panel-bg-1: rgba(255, 255, 255, 0.97);
  --sr-panel-bg-2: rgba(241, 245, 249, 0.95);
  --sr-glass-bg-1: rgba(255, 255, 255, 0.94);
  --sr-glass-bg-2: rgba(241, 245, 249, 0.9);
  --sr-chip-bg: rgba(255, 255, 255, 0.85);
  --sr-shell-bg-1: rgba(255, 255, 255, 0.96);
  --sr-shell-bg-2: rgba(241, 245, 249, 0.92);
  --sr-primary-card-bg-1: rgba(226, 236, 253, 0.9);
  --sr-nav-bg: rgba(255, 255, 255, 0.75);
  --sr-btn-secondary-bg: rgba(226, 236, 253, 0.6);

  --sr-border: rgba(15, 23, 42, 0.1);
  --sr-border-soft: rgba(15, 23, 42, 0.08);
  --sr-border-faint: rgba(15, 23, 42, 0.06);
  --sr-border-accent: rgba(37, 99, 235, 0.16);
  --sr-border-accent-hover: rgba(37, 99, 235, 0.24);
  --sr-chip-border: rgba(37, 99, 235, 0.1);
  --sr-panel-border: rgba(37, 99, 235, 0.14);

  --sr-shadow-soft: rgba(15, 23, 42, 0.06);
  --sr-shadow-med: rgba(15, 23, 42, 0.09);
  --sr-shadow-strong: rgba(15, 23, 42, 0.12);

  --sr-page-bg:
    radial-gradient(circle at 10% 0%, rgba(59, 130, 246, 0.08), transparent 26%),
    radial-gradient(circle at 90% 10%, rgba(34, 211, 238, 0.08), transparent 24%),
    linear-gradient(180deg, #f5f9ff 0%, #eef4fc 30%, #eaf1fb 60%, #f2f7fd 100%);
}

.bg-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(12px);
  pointer-events: none;
  z-index: 0;
}

.orb-1 { width: 420px; height: 420px; top: -100px; left: -120px; background: radial-gradient(circle, rgba(37, 99, 235, 0.22), transparent 70%); }
.orb-2 { width: 320px; height: 320px; top: 520px; right: -80px; background: radial-gradient(circle, rgba(6, 182, 212, 0.18), transparent 70%); }
.orb-3 { width: 420px; height: 420px; bottom: 120px; left: 10%; background: radial-gradient(circle, var(--sr-panel-border), transparent 70%); }

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
.contact-section {
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
  background: var(--sr-nav-bg);
  border-bottom: 1px solid var(--sr-border);
}

.brand {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  cursor: pointer;
}

.brand h1 { margin: 0; font-size: 1.05rem; color: var(--sr-heading); }
.brand p { margin: 0.1rem 0 0; font-size: 0.82rem; color: var(--sr-text-muted); }

.nav-links, .nav-actions, .hero-actions, .cta-actions {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  flex-wrap: wrap;
}

.nav-links button {
  border: none;
  background: transparent;
  color: var(--sr-nav-link);
  font-weight: 600;
  cursor: pointer;
  padding: 0.55rem 0.8rem;
  border-radius: 999px;
  transition: 0.25s ease;
}

.nav-links button:hover {
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

.eyebrow, .section-tag, .status-pill, .step-number {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 999px;
  font-weight: 700;
}

.eyebrow, .section-tag {
  width: fit-content;
  font-size: 0.8rem;
  letter-spacing: 0.04em;
  padding: 0.45rem 0.85rem;
  background: rgba(37, 99, 235, 0.16);
  border: 1px solid var(--sr-border-accent);
  color: var(--sr-accent-text);
}

.hero-content h2 {
  font-size: clamp(2.7rem, 6vw, 5.1rem);
  line-height: 1.02;
  margin: 1rem 0;
  max-width: 11ch;
  color: var(--sr-heading);
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
  color: var(--sr-text-muted);
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
  background: var(--sr-chip-bg);
  border: 1px solid var(--sr-chip-border);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.03), 0 14px 30px var(--sr-shadow-soft);
}

.feature-chip strong { display: block; color: var(--sr-heading); margin-bottom: 0.25rem; font-size: 0.95rem; }
.feature-chip p { margin: 0; font-size: 0.86rem; line-height: 1.55; color: var(--sr-text-muted); }

.chip-dot {
  width: 10px; height: 10px; border-radius: 50%; margin-top: 0.4rem; flex-shrink: 0; box-shadow: 0 0 16px currentColor;
}
.chip-dot.blue { color: #3b82f6; background: #3b82f6; }
.chip-dot.cyan { color: #22d3ee; background: #22d3ee; }
.chip-dot.orange { color: #f97316; background: #f97316; }
.chip-dot.green { color: #22c55e; background: #22c55e; }

.glass-card {
  width: 100%;
  max-width: 620px;
  border-radius: 28px;
  padding: 1.4rem;
  background: linear-gradient(180deg, var(--sr-glass-bg-1), var(--sr-glass-bg-2));
  box-shadow: 0 35px 70px var(--sr-shadow-strong);
  border: 1px solid var(--sr-border);
  backdrop-filter: blur(18px);
}

.preview-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.mini-label {
  margin: 0 0 0.35rem;
  font-size: 0.78rem;
  color: var(--sr-text-faint);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.status-pill {
  background: rgba(34, 197, 94, 0.14);
  color: #6ee7b7;
  padding: 0.5rem 0.8rem;
  font-size: 0.85rem;
  border: 1px solid rgba(34, 197, 94, 0.16);
}

.stats-grid, .feature-grid, .steps-grid, .roles-grid, .contact-grid {
  display: grid;
  gap: 1rem;
}

.stats-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); margin-top: 1.2rem; }

.stat-card, .feature-card, .step-card, .role-card, .contact-card {
  border-radius: 22px;
  padding: 1.1rem;
  background: var(--sr-card-bg);
  border: 1px solid var(--sr-border-soft);
  box-shadow: 0 18px 34px var(--sr-shadow-soft);
  transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
}

.stat-card:hover, .feature-card:hover, .step-card:hover, .role-card:hover, .contact-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 24px 42px var(--sr-shadow-med);
  border-color: var(--sr-border-accent-hover);
}

.stat-card h4 { margin: 0; font-size: 1.65rem; color: var(--sr-heading); }
.stat-card p, .feature-card p, .step-card p, .role-card p, .contact-card p {
  margin: 0.4rem 0 0; color: var(--sr-text-muted); font-size: 0.95rem; line-height: 1.65;
}

.accent-blue { border-top: 4px solid #2563eb; }
.accent-orange { border-top: 4px solid #f97316; }
.accent-green { border-top: 4px solid #22c55e; }
.accent-purple { border-top: 4px solid #8b5cf6; }

.activity-panel {
  margin-top: 1.2rem;
  padding: 1rem;
  border-radius: 22px;
  background: linear-gradient(180deg, var(--sr-panel-bg-1), var(--sr-panel-bg-2));
  border: 1px solid var(--sr-panel-border);
}

.activity-list { display: flex; flex-direction: column; gap: 0.9rem; margin-top: 1rem; }
.activity-item { display: flex; align-items: flex-start; gap: 0.8rem; }
.activity-item strong { color: var(--sr-heading); }
.dot { width: 12px; height: 12px; border-radius: 50%; margin-top: 0.35rem; flex-shrink: 0; }
.dot.green { background: #22c55e; }
.dot.orange { background: #f97316; }
.dot.blue { background: #3b82f6; }

.content-section { padding-top: 5rem; padding-bottom: 5rem; }
.alt-bg { background: linear-gradient(180deg, rgba(4, 12, 24, 0.25), rgba(10, 20, 38, 0.42)); }

.section-heading { max-width: 820px; margin-bottom: 2rem; }
.section-heading.center { margin-left: auto; margin-right: auto; text-align: center; }
.section-heading h2 { margin: 1rem 0 0.85rem; font-size: clamp(2rem, 4vw, 3rem); line-height: 1.15; color: var(--sr-heading); }

.feature-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); }
.feature-icon {
  width: 54px; height: 54px; border-radius: 18px; display: grid; place-items: center;
  font-size: 1.4rem; margin-bottom: 1rem; background: linear-gradient(135deg, rgba(37, 99, 235, 0.18), rgba(34, 211, 238, 0.16));
}

.steps-grid { grid-template-columns: repeat(4, minmax(0, 1fr)); }
.step-number { width: fit-content; padding: 0.45rem 0.7rem; font-size: 0.85rem; margin-bottom: 1rem; background: rgba(37, 99, 235, 0.16); color: var(--sr-accent-text); border: 1px solid var(--sr-border-accent); }

.roles-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }

.placeholder-note {
  max-width: 820px; margin: -1.2rem auto 2rem; text-align: center; font-size: 0.85rem;
  color: var(--sr-text-faint); background: var(--sr-chip-bg); border: 1px dashed var(--sr-border-accent); border-radius: 14px; padding: 0.7rem 1rem;
}

.gallery-heading { max-width: 820px; margin: 2.5rem auto 1.2rem; text-align: center; }
.gallery-heading h3 { margin: 0 0 0.4rem; color: var(--sr-heading); font-size: 1.4rem; }

/* ---- DONATION DRIVE SECTION ---- */
.donate-layout { display: grid; grid-template-columns: 0.8fr 1.2fr; gap: 1.2rem; align-items: start; }
.donate-summary { display: flex; flex-direction: column; gap: 1rem; }
.donate-stat {
  border-radius: 22px; padding: 1.4rem; background: var(--sr-card-bg); border: 1px solid var(--sr-border-soft); box-shadow: 0 18px 34px var(--sr-shadow-soft); border-top: 4px solid #2563eb;
}
.donate-stat.urgent { border-top-color: #f97316; }
.donate-stat h4 { margin: 0; font-size: 2.2rem; color: var(--sr-heading); }
.donate-stat p { margin: 0.35rem 0 0; color: var(--sr-text-muted); }

.donate-needs-card {
  border-radius: 22px; padding: 1.4rem; background: var(--sr-card-bg); border: 1px solid var(--sr-border-soft); box-shadow: 0 18px 34px var(--sr-shadow-soft);
}
.donate-needs-card h3 { margin: 0 0 1rem; color: var(--sr-heading); }
.donate-needs-list { list-style: none; margin: 0 0 1.4rem; padding: 0; display: flex; flex-direction: column; gap: 0.7rem; }
.donate-needs-list li {
  display: flex; align-items: center; justify-content: space-between; gap: 0.8rem; padding: 0.75rem 0.9rem; border-radius: 14px; background: var(--sr-btn-secondary-bg); border: 1px solid var(--sr-border-faint); flex-wrap: wrap;
}
.need-name { font-weight: 700; color: var(--sr-heading); }
.need-qty { color: var(--sr-text-muted); font-size: 0.88rem; }
.need-pill { padding: 0.3rem 0.65rem; border-radius: 999px; font-size: 0.72rem; font-weight: 800; text-transform: uppercase; }
.need-pill.urgent { background: rgba(251,113,133,.16); color: #fb7185; }
.need-pill.high { background: rgba(251,191,36,.16); color: #fbbf24; }
.need-pill.medium { background: rgba(56,189,248,.16); color: #38bdf8; }
.need-pill.low { background: rgba(52,211,153,.16); color: #34d399; }

.donate-cta { width: 100%; justify-content: center; display: flex; }
.donate-note { margin: 0.8rem 0 0; font-size: 0.82rem; text-align: center; color: var(--sr-text-faint); }

/* ---- CTA & CONTACT SECTIONS ---- */
.cta-section { padding-top: 2rem; padding-bottom: 5rem; }
.cta-card {
  display: flex; align-items: center; justify-content: space-between; gap: 1.5rem; padding: 2rem; border-radius: 30px; color: white; background: linear-gradient(135deg, #103b8d, #1d4ed8 45%, #0ea5e9 100%); box-shadow: 0 30px 60px var(--sr-shadow-med); border: 1px solid rgba(255, 255, 255, 0.14);
}

.contact-section { padding-top: 0.5rem; padding-bottom: 3rem; }
.contact-shell { padding: 2rem; border-radius: 32px; background: linear-gradient(180deg, var(--sr-shell-bg-1), var(--sr-shell-bg-2)); border: 1px solid var(--sr-border); box-shadow: 0 26px 54px var(--sr-shadow-med); }
.contact-intro { max-width: 760px; margin-bottom: 1.5rem; }
.contact-intro h2 { margin: 1rem 0 0.7rem; font-size: clamp(1.8rem, 4vw, 2.7rem); color: var(--sr-heading); }

.contact-grid.three-division-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 1rem; align-items: stretch; }
.primary-contact-card { background: linear-gradient(135deg, var(--sr-primary-card-bg-1), var(--sr-shell-bg-1)); }
.contact-kicker { margin-bottom: 1rem; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.08em; color: var(--sr-accent-text); }

.contact-details-list { display: flex; flex-direction: column; gap: 0.95rem; margin-top: 1rem; }
.contact-details-list.compact { gap: 0.85rem; }
.contact-line { display: flex; align-items: flex-start; gap: 0.85rem; padding: 0.95rem 1rem; border-radius: 18px; background: rgba(255, 255, 255, 0.03); border: 1px solid var(--sr-border-faint); }
.contact-icon { width: 40px; height: 40px; border-radius: 12px; display: grid; place-items: center; flex-shrink: 0; font-size: 1rem; background: linear-gradient(135deg, rgba(37, 99, 235, 0.22), rgba(34, 211, 238, 0.16)); }
.contact-line label { display: block; margin-bottom: 0.3rem; font-size: 0.78rem; font-weight: 700; letter-spacing: 0.04em; text-transform: uppercase; color: var(--sr-text-faint); }
.contact-line a, .contact-line p { display: block; margin: 0; line-height: 1.55; }
.contact-line a { color: var(--sr-heading); font-weight: 700; text-decoration: none; word-break: break-word; }

.contact-actions { display: flex; gap: 0.8rem; flex-wrap: wrap; margin-top: 0.8rem; }
.contact-btn { text-decoration: none; }
.dark-outline { background: transparent; color: var(--sr-heading); border: 1px solid rgba(255, 255, 255, 0.18); }
.wide-card { grid-column: 1 / -1; }

.btn { border: none; border-radius: 999px; padding: 0.8rem 1.2rem; font-weight: 700; cursor: pointer; transition: 0.25s ease; }
.btn.large { padding: 0.95rem 1.4rem; font-size: 1rem; }
.btn.primary { color: white; background: linear-gradient(135deg, #2563eb, #0ea5e9); box-shadow: 0 18px 34px rgba(37, 99, 235, 0.34); }
.btn.primary:hover { transform: translateY(-2px); box-shadow: 0 24px 40px rgba(37, 99, 235, 0.38); }
.btn.secondary, .btn.ghost { background: var(--sr-btn-secondary-bg); color: var(--sr-text); border: 1px solid var(--sr-border-accent); }
.btn.light { background: white; color: #0f3f8c; }
.btn.outline-light { background: transparent; color: white; border: 1px solid rgba(255, 255, 255, 0.38); }

.logo-img { width: 50px; height: 50px; object-fit: contain; display: block; border-radius: 8px; }

/* ---- IN-KIND PLEDGE MODAL STYLES ---- */
.modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 100;
  background: rgba(4, 12, 24, 0.82);
  backdrop-filter: blur(8px);
  display: grid;
  place-items: center;
  padding: 1rem;
}

.modal-card {
  position: relative;
  width: 100%;
  max-width: 580px;
  background: var(--sr-panel-bg-1);
  border: 1px solid var(--sr-border-accent);
  max-height: 90vh;
  overflow-y: auto;
}

.modal-close {
  position: absolute;
  top: 1rem;
  right: 1.2rem;
  background: transparent;
  border: none;
  font-size: 1.8rem;
  color: var(--sr-text-muted);
  cursor: pointer;
}

.modal-header { margin-bottom: 1.2rem; }
.modal-header h3 { margin: 0.5rem 0 0.2rem; color: var(--sr-heading); }
.modal-header p { margin: 0; color: var(--sr-text-muted); font-size: 0.9rem; }

.pledge-form { display: flex; flex-direction: column; gap: 1rem; }
.form-row { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 1rem; }
.form-group { display: flex; flex-direction: column; gap: 0.4rem; }
.form-group label { font-size: 0.82rem; font-weight: 700; color: var(--sr-accent-text); }

.form-input {
  width: 100%;
  padding: 0.75rem 0.9rem;
  border-radius: 12px;
  background: var(--sr-card-bg);
  border: 1px solid var(--sr-border-soft);
  color: var(--sr-heading);
  font-family: inherit;
  font-size: 0.95rem;
}

.form-input:focus {
  outline: none;
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.2);
}

.modal-actions { display: flex; justify-content: flex-end; gap: 0.8rem; margin-top: 0.5rem; }
.modal-actions.center { justify-content: center; }

.pledge-success-view { text-align: center; padding: 1.5rem 0; }
.success-icon { font-size: 3rem; margin-bottom: 0.5rem; }
.pledge-success-view h3 { margin: 0.5rem 0; color: var(--sr-heading); }
.ref-code { font-size: 1.1rem; color: var(--sr-accent-text); }
.success-text { margin: 1rem 0 1.5rem; color: var(--sr-text-muted); line-height: 1.6; font-size: 0.95rem; }

@media (max-width: 1024px) {
  .contact-grid.three-division-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}

@media (max-width: 860px) {
  .donate-layout, .hero-section, .cta-card { grid-template-columns: 1fr; }
  .feature-grid, .steps-grid, .roles-grid, .contact-grid, .stats-grid { grid-template-columns: 1fr; }
  .wide-card { grid-column: auto; }
}

@media (max-width: 640px) {
  .form-row { grid-template-columns: 1fr; }
  .contact-grid.three-division-grid { grid-template-columns: 1fr; }
}



/* ---- MOBILE & TABLET LAYOUT FIXES ---- */

@media (max-width: 860px) {
  /* 1. Prevent screen clipping & edge crowding */
  .landing-header,
  .hero-section,
  .content-section,
  .cta-section,
  .contact-section {
    padding-left: 1.25rem !important;
    padding-right: 1.25rem !important;
  }

  /* 2. Header alignment and link collapse */
  .landing-header {
    flex-wrap: wrap;
    justify-content: space-between;
    gap: 0.75rem;
    padding-top: 0.85rem;
    padding-bottom: 0.85rem;
  }

  .nav-links {
    display: none; /* Hide standard links to prevent header crowding */
  }

  .nav-actions {
    margin-left: auto;
  }

  /* 3. Hero layout & typography scaling */
  .hero-section {
    grid-template-columns: 1fr !important;
    padding-top: 2rem;
    padding-bottom: 2rem;
    gap: 2rem;
  }

  .hero-content h2, 
  .cta-card h2 {
    font-size: clamp(1.85rem, 7vw, 2.75rem) !important;
    line-height: 1.25;
  }

  .hero-feature-chips {
    grid-template-columns: 1fr !important;
    gap: 0.5rem;
  }

  .hero-actions {
    flex-direction: column;
    width: 100%;
  }

  .hero-actions .btn,
  .cta-actions .btn {
    width: 100%;
    justify-content: center;
  }

  /* 4. Multi-column grid conversions */
  .stats-grid,
  .feature-grid,
  .steps-grid,
  .roles-grid,
  .contact-grid,
  .three-division-grid {
    grid-template-columns: 1fr !important;
    gap: 1.25rem;
  }

  /* 5. CTA banner stack */
  .cta-card {
    flex-direction: column;
    align-items: stretch;
    text-align: center;
    padding: 1.75rem 1.25rem;
  }

  .cta-actions {
    flex-direction: column;
    width: 100%;
    margin-top: 1rem;
  }
}

@media (max-width: 640px) {
  /* 6. Mobile Modal & Form optimization */
  .modal-backdrop {
    padding: 0.5rem;
    align-items: flex-end; /* Sheet presentation on mobile */
  }

  .modal-card {
    width: 100%;
    max-height: 85vh;
    overflow-y: auto;
    border-bottom-left-radius: 0;
    border-bottom-right-radius: 0;
    padding: 1.25rem;
  }

  .form-row {
    grid-template-columns: 1fr !important;
    gap: 0.75rem;
  }

  .glass-card {
    padding: 1.1rem;
    border-radius: 16px;
  }
}

</style>