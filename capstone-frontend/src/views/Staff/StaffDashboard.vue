<template>
  <div class="dash">
    <!-- top row -->
    <div class="top">
      <div>
        <h1 class="title">Staff Dashboard</h1>
        <p class="sub">Quick access for evacuation staff (center + logs + map).</p>
      </div>
    </div>

    <!-- assigned center banner -->
    <div class="banner" :class="{ warn: isStaff && !me.assigned_center_id }">
      <div class="banner-left">
        <div class="kicker">Logged in as</div>
        <div class="who">
          <b>{{ me.email || "-" }}</b>
          <span class="muted">({{ me.role || "-" }})</span>
        </div>
        <div class="muted small">
          Assigned center:
          <b>{{ me.assigned_center_name || "Unassigned" }}</b>
        </div>
      </div>

      <div class="metrics">
        <div class="metric primary-metric banner">
          <div class="metric-icon">👥</div>
          <div class="metric-content">
            <div class="metric-label">Current Evacuees</div>
            <div class="metric-value">{{ latest.total_current ?? 0 }}</div>
            <div class="metric-caption muted">People currently recorded at the center</div>
          </div>
        </div>

        <div class="metric banner">
          <div class="metric-icon family-icon">🏠</div>
          <div class="metric-content">
            <div class="metric-label">Current Families</div>
            <div class="metric-value">{{ latest.total_current_families ?? 0 }}</div>
            <div class="metric-caption muted">Families currently recorded</div>
          </div>
        </div>

        <div class="last-update muted">
          <span>Last update</span>
          <strong class="muted">{{ lastUpdatedText }}</strong>
        </div>
      </div>
    </div>

    <!-- quick stats -->
    <div class="grid">
      <div class="card">
        <div class="card-top">
          <span class="label">Center Status</span>
          <span class="dot" :class="isStaff && me.assigned_center_id ? 'ok' : 'bad'"></span>
        </div>

        <div class="value">
          {{ isStaff && me.assigned_center_id ? "Assigned" : "Unassigned" }}
        </div>
        <div class="muted small">
          {{ isStaff && me.assigned_center_id
            ? "You can submit logs for your center."
            : "Ask admin to assign you an evacuation center."
          }}
        </div>
      </div>

      <div class="card">
        <div class="card-top">
          <span class="label">Quick Actions</span>
        </div>

        <div class="muted small">Go directly to pages:</div>

        <div class="btnrow">
          <button class="btn primary" @click="goLogs">
            View Logs
          </button>
          <button class="btn ghost" @click="goMap">Open Map</button>
        </div>

        <div class="hint" v-if="isStaff && !me.assigned_center_id">
          You can’t add logs until a center is assigned.
        </div>
      </div>

    </div>

    <!-- placeholder for future breakdown -->
    <div class="breakdown">
      <div class="break-head">
        <h2>Vulnerable Breakdown</h2>
        <span class="note">
          <span class="note-icon">i</span>
          Requires log breakdown fields (Children/Seniors/PWD/Pregnant/Lactating)
        </span>
      </div>

      <div class="break-grid">
        <div
          class="pillcard"
          v-for="x in breakdownCards"
          :key="x.key"
          :class="'accent-' + x.key"
        >
          <div class="pill-top">
            <span class="pill-icon">{{ iconFor(x.key) }}</span>
            <span class="pill-label">{{ x.label }}</span>
          </div>
          <div class="pill-val">{{ x.value }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import api from "../../services/api";
import { computed, onMounted, reactive, ref } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();

const me = reactive({});
const latest = reactive({ total_current: 0, total_current_families: 0, date_recorded: null });
const summary = ref(null); // ✅ add this

const isStaff = computed(() => me.role === "EVAC_CENTER_STAFF");

const lastUpdatedText = computed(() => {
  if (!latest.date_recorded) return "-";
  const d = new Date(latest.date_recorded);
  return isNaN(d.getTime()) ? String(latest.date_recorded) : d.toLocaleString();
});

// for now, values are 0 until you add breakdown fields to backend
const breakdown = ref({
  children: 0,
  seniors: 0,
  pwd: 0,
  pregnant: 0,
  lactating: 0,
});

const breakdownCards = computed(() => {
  const b = summary.value?.breakdown || {};
  return [
    { key: "children", label: "Children", value: b.children_count ?? 0 },
    { key: "seniors", label: "Seniors", value: b.senior_count ?? 0 },
    { key: "pwd", label: "PWD", value: b.pwd_count ?? 0 },
    { key: "pregnant", label: "Pregnant", value: b.pregnant_count ?? 0 },
    { key: "lactating", label: "Lactating", value: b.lactating_count ?? 0 },
  ];
});

// presentation-only helper: maps breakdown key -> icon glyph
function iconFor(key) {
  const map = {
    children: "🧒",
    seniors: "👵",
    pwd: "♿",
    pregnant: "🤰",
    lactating: "🍼",
  };
  return map[key] || "•";
}

async function fetchMe() {
  const res = await api.get("user/profile/");
  Object.assign(me, res.data || {});
}

async function fetchLatest() {
  if (!me.assigned_center_id) {
    latest.total_current = summary.value?.total_current ?? 0;
    latest.total_current_families = summary.value?.total_current_families ?? 0;
    latest.date_recorded = summary.value?.latest?.date_recorded ?? null;
    return;
  }

  const res = await api.get("evac_centers/evacuation-logs/staff_summary/");
  summary.value = res.data || null;

  // update latest from summary
  latest.total_current = summary.value?.total_current ?? 0;
  latest.total_current_families = summary.value?.total_current_families ?? 0;
  latest.date_recorded = summary.value?.latest?.date_recorded ?? null;
}

function goLogs() {
  router.push("/staff/logs"); // change if your route is different
}
function goMap() {
  router.push("/staff/map"); // change if your route is different
}

onMounted(async () => {
  try {
    await fetchMe();
    await fetchLatest();
  } catch (err) {
    console.error("StaffDashboard init error:", err);
  }
});
</script>

<style scoped>
.dash{
  --bg:#060912;
  --panel:rgba(10,14,28,.65);
  --panel2:rgba(8,12,24,.82);
  --border:rgba(56,189,248,.16);
  --border2:rgba(255,255,255,.08);
  --text:#e5e7eb;
  --muted:rgba(229,231,235,.62);
  --blue:#38bdf8;
  --blue2:#2563eb;
  --green:#22c55e;
  --red:#ef4444;
  --amber:#f59e0b;
  --pink:#f472b6;
  --violet:#a78bfa;

  padding: clamp(16px,2vw,24px);
  max-width: 1500px;
  margin: 0 auto;
  color: var(--text);
}

.top{
  display:flex;
  justify-content:space-between;
  align-items:flex-end;
  gap: 14px;
  margin-bottom: 14px;
}

.title{ margin:0; font-size: 2rem; color:#f8fafc; letter-spacing:.2px; }
.sub{ margin:6px 0 0; color: var(--muted); font-size: 13px; }

.btn{
  border-radius:14px;
  padding: 10px 14px;
  font-size: 13px;
  font-weight: 900;
  border: 1px solid rgba(56,189,248,.22);
  cursor:pointer;
  transition: transform .12s ease, box-shadow .12s ease, background .12s ease, border-color .12s ease;
  display:inline-flex; align-items:center; gap:8px;
  color: var(--text);
  background: rgba(56,189,248,.10);
}
.btn:hover:not(:disabled){ transform: translateY(-1px); background: rgba(56,189,248,.16); }
.btn:disabled{ opacity:.5; cursor:not-allowed; transform:none; }

.btn.primary{
  color:#06121f;
  background: linear-gradient(135deg, rgba(56,189,248,1), rgba(37,99,235,1));
  border-color: rgba(56,189,248,.45);
  box-shadow: 0 18px 40px rgba(37,99,235,.28);
}
.btn.primary:hover:not(:disabled){ box-shadow: 0 22px 48px rgba(37,99,235,.38); }

.btn.ghost{
  background: rgba(2,6,23,.35);
  border-color: rgba(255,255,255,.10);
}

.banner{
  display:grid;
  grid-template-columns:minmax(230px,.9fr) minmax(0,1.7fr);
  align-items:stretch;
  gap:20px;
  padding:20px;
  border-radius:20px;
  border:1px solid var(--border2);
  background:
    radial-gradient(1000px 420px at 15% -15%, rgba(56,189,248,.24), transparent 55%),
    radial-gradient(700px 320px at 100% 0%, rgba(167,139,250,.10), transparent 60%),
    linear-gradient(180deg, rgba(10,14,28,.78), rgba(6,9,18,.86));
  box-shadow:0 20px 48px rgba(0,0,0,.48);
}

.banner.warn{
  border-color:rgba(245,158,11,.35);
  background:
    radial-gradient(900px 420px at 15% -15%, rgba(245,158,11,.16), transparent 60%),
    linear-gradient(180deg, rgba(10,14,28,.78), rgba(6,9,18,.86));
}

.kicker{ font-size:12px; color:rgba(229,231,235,.55); font-weight:800; }
.who{ margin-top:4px; line-height:1.4; }
.muted{ color:var(--muted); }
.small{ font-size:12.5px; }

.metrics{
  display:grid;
  grid-template-columns:repeat(2,minmax(0,1fr));
  gap:12px;
  min-width:0;
}

.metric{
  position:relative;
  display:flex;
  align-items:center;
  gap:14px;
  min-width:0;
  padding:16px;
  border-radius:16px;
  border:1px solid rgba(255,255,255,.08);
  background:rgba(2,6,23,.38);
  transition: transform .15s ease, border-color .15s ease;
}
.metric:hover{ transform: translateY(-2px); border-color: rgba(56,189,248,.32); }

.primary-metric{
  border-color:rgba(56,189,248,.28);
  background:
    radial-gradient(300px 180px at 0% 0%, rgba(56,189,248,.18), transparent 70%),
    rgba(2,6,23,.42);
}

.metric-icon{
  flex:0 0 48px;
  width:48px;
  height:48px;
  display:grid;
  place-items:center;
  border-radius:14px;
  font-size:23px;
  background:rgba(56,189,248,.14);
  border:1px solid rgba(56,189,248,.22);
}

.family-icon{
  background:rgba(37,99,235,.16);
  border-color:rgba(37,99,235,.26);
}

.metric-content{ min-width:0; }
.metric-label{
  color:rgba(229,231,235,.68);
  font-size:11px;
  font-weight:900;
  text-transform:uppercase;
  letter-spacing:.75px;
}

.metric-value{
  margin-top:3px;
  font-size:clamp(2rem,3.2vw,3rem);
  line-height:1;
  font-weight:1000;
  letter-spacing:-1px;
  color:#f8fafc;
}

.primary-metric .metric-value{
  color:#dff6ff;
  text-shadow:0 0 24px rgba(56,189,248,.20);
}

.metric-caption{
  margin-top:6px;
  color:rgba(229,231,235,.48);
  font-size:11px;
  line-height:1.35;
}

.last-update{
  grid-column:1 / -1;
  display:flex;
  justify-content:flex-end;
  align-items:center;
  gap:6px;
  padding-top:2px;
  color:rgba(229,231,235,.45);
  font-size:11px;
}

.last-update strong{
  color:rgba(229,231,235,.68);
  font-weight:700;
}

.grid{
  display:grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  margin-top: 12px;
}

.card{
  border-radius: 18px;
  padding: 14px;
  border: 1px solid var(--border2);
  background: var(--panel2);
  box-shadow: 0 18px 40px rgba(0,0,0,.45);
  transition: transform .15s ease, border-color .15s ease;
}
.card:hover{ transform: translateY(-2px); border-color: rgba(56,189,248,.24); }

.card-top{ display:flex; justify-content:space-between; align-items:center; margin-bottom: 10px; }
.label{ font-size: 12px; text-transform: uppercase; letter-spacing:.7px; color: rgba(229,231,235,.65); font-weight: 900; }

.dot{
  width: 10px; height: 10px; border-radius: 999px;
  background: rgba(255,255,255,.25);
  box-shadow:0 0 0 6px rgba(255,255,255,.04);
}
.dot.ok{ background: var(--green); box-shadow:0 0 0 6px rgba(34,197,94,.10); }
.dot.bad{ background: var(--red); box-shadow:0 0 0 6px rgba(239,68,68,.10); }

.value{ font-size: 22px; font-weight: 1000; color:#f8fafc; }
.btnrow{ display:flex; gap:10px; flex-wrap:wrap; margin-top: 10px; }
.hint{ margin-top: 10px; font-size: 12px; color: rgba(245,158,11,.9); font-weight: 900; }

.breakdown{
  margin-top: 12px;
  border-radius: 18px;
  padding: 14px;
  border: 1px solid var(--border2);
  background: rgba(8,12,24,.82);
  box-shadow: 0 20px 48px rgba(0,0,0,.48);
}

.break-head{ display:flex; justify-content:space-between; gap: 10px; flex-wrap:wrap; align-items:center; }
.break-head h2{ margin:0; font-size: 1.1rem; color:#f8fafc; }

.note{
  display:inline-flex;
  align-items:center;
  gap:7px;
  font-size: 11.5px;
  color: rgba(229,231,235,.55);
  background: rgba(255,255,255,.04);
  border: 1px solid rgba(255,255,255,.08);
  border-radius: 999px;
  padding: 5px 10px 5px 6px;
}

.note-icon{
  flex:0 0 auto;
  width:16px; height:16px;
  display:grid; place-items:center;
  border-radius:999px;
  font-size: 10px;
  font-weight: 900;
  font-style: normal;
  color:#06121f;
  background: var(--blue);
}

.break-grid{
  display:grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 10px;
  margin-top: 14px;
}

.pillcard{
  border-radius: 16px;
  padding: 12px;
  border: 1px solid rgba(56,189,248,.14);
  border-top: 2px solid rgba(56,189,248,.5);
  background: rgba(2,6,23,.35);
  transition: transform .15s ease;
}
.pillcard:hover{ transform: translateY(-2px); }

.accent-children{ border-top-color: var(--blue); }
.accent-seniors{ border-top-color: var(--violet); }
.accent-pwd{ border-top-color: var(--amber); }
.accent-pregnant{ border-top-color: var(--pink); }
.accent-lactating{ border-top-color: var(--green); }

.pill-top{ display:flex; align-items:center; gap:8px; margin-bottom: 10px; }
.pill-icon{ font-size: 15px; line-height:1; }
.pill-label{ font-size: 12px; color: rgba(229,231,235,.65); font-weight: 900; }
.pill-val{ font-size: 26px; font-weight: 1000; color:#f8fafc; letter-spacing:-0.5px; }

@media (max-width: 1000px){
  .grid{ grid-template-columns:1fr; }
  .break-grid{ grid-template-columns:1fr 1fr; }
  .banner{ grid-template-columns:1fr; }
}

@media (max-width: 680px){
  .dash{ padding:14px; }
  .top{ align-items:flex-start; flex-direction:column; }
  .metrics{ grid-template-columns:1fr; }
  .last-update{ justify-content:flex-start; }
  .break-grid{ grid-template-columns:1fr; }
}
</style>