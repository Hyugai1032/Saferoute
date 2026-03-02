<template>
  <div class="page">
    <div class="page-header">
      <div>
        <h1>My Profile</h1>
        <p class="muted">View and update your account information</p>
      </div>
    </div>

    <!-- TOP CARD -->
    <div class="card profile-top">
      <div class="avatar">{{ initials }}</div>

      <div class="info">
        <div class="name-row">
          <h2>{{ fullName || me.email }}</h2>
          <span class="badge">{{ me.role || "—" }}</span>
        </div>
        <div class="muted">{{ me.email }}</div>

        <div class="meta">
          <div class="meta-item">
            <div class="label">Municipality</div>
            <div>{{ me.municipality || "—" }}</div>
          </div>

          <div class="meta-item" v-if="isStaff">
            <div class="label">Assigned Center</div>
            <div :class="me.assigned_center_name ? '' : 'warn-text'">
              {{ me.assigned_center_name || "Unassigned" }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- STAFF WARNING -->
    <div v-if="isStaff && !me.assigned_center_id" class="card warn" style="margin-top: 14px;">
      <b>Unassigned center</b>
      <div class="muted">Ask an admin to assign you to an evacuation center to access logs.</div>
    </div>

    <!-- EDIT FORM -->
    <div class="card" style="margin-top: 14px;">
      <h3 style="margin-bottom: 10px;">Edit Profile</h3>

      <form class="grid" @submit.prevent="save">
        <div class="form-group">
          <label class="label">First name</label>
          <input class="form-input" v-model="form.first_name" placeholder="First name" />
        </div>

        <div class="form-group">
          <label class="label">Last name</label>
          <input class="form-input" v-model="form.last_name" placeholder="Last name" />
        </div>

        <div class="actions">
          <button class="btn" type="submit" :disabled="saving">
            {{ saving ? "Saving..." : "Save Changes" }}
          </button>
          <span v-if="saved" class="muted">Saved.</span>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import axios from "axios";

const me = reactive({
  email: "",
  first_name: "",
  last_name: "",
  role: "",
  municipality: null,
  assigned_center_id: null,
  assigned_center_name: null,
});

const form = reactive({
  first_name: "",
  last_name: "",
});

const saving = ref(false);
const saved = ref(false);

const isStaff = computed(() =>
  String(me.role || "").toUpperCase().includes("STAFF")
);

const fullName = computed(() => {
  const fn = (me.first_name || "").trim();
  const ln = (me.last_name || "").trim();
  return (fn || ln) ? `${fn} ${ln}`.trim() : "";
});

const initials = computed(() => {
  const base = fullName.value || me.email || "";
  const parts = base.replace("@", " ").split(" ").filter(Boolean);
  const a = (parts[0]?.[0] || "?").toUpperCase();
  const b = (parts[1]?.[0] || "").toUpperCase();
  return (a + b).slice(0, 2);
});

async function loadMe() {
  const token = localStorage.getItem("access_token");
  const { data } = await axios.get("/api/me/", {
    headers: { Authorization: `Bearer ${token}` },
  });

  Object.assign(me, data);
  form.first_name = data.first_name || "";
  form.last_name = data.last_name || "";
}

async function save() {
  saving.value = true;
  saved.value = false;
  try {
    const token = localStorage.getItem("access_token");
    await axios.patch("/api/me/update/", form, {
      headers: { Authorization: `Bearer ${token}` },
    });
    await loadMe();
    saved.value = true;
    setTimeout(() => (saved.value = false), 1500);
  } finally {
    saving.value = false;
  }
}

onMounted(loadMe);
</script>

<style scoped>
.profile-top {
  display: flex;
  gap: 16px;
  align-items: center;
}
.avatar {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  display: grid;
  place-items: center;
  font-weight: 800;
  font-size: 20px;
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.08);
}
.info { flex: 1; }
.name-row { display:flex; gap:10px; align-items:center; flex-wrap:wrap; }
.badge {
  padding: 6px 10px;
  border-radius: 999px;
  font-size: 12px;
  border: 1px solid rgba(255,255,255,0.12);
  background: rgba(0, 150, 255, 0.10);
}
.meta {
  display:flex;
  gap: 18px;
  margin-top: 10px;
  flex-wrap: wrap;
}
.meta-item .label { opacity: .7; font-size: 12px; }
.warn-text { color: #ffb020; font-weight: 600; }

.grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}
.actions {
  grid-column: 1 / -1;
  display:flex;
  gap: 10px;
  align-items:center;
  margin-top: 6px;
}
@media (max-width: 720px) {
  .grid { grid-template-columns: 1fr; }
}
</style>