import api from "./api";

export const evacService = {
  listLogs(params) {
    return api.get("evac_centers/evacuation-logs/", { params });
  },
  createLog(payload) {
    return api.post("evac_centers/evacuation-logs/", payload);
  },
  updateLog(id, payload) {
    return api.patch(`evac_centers/evacuation-logs/${id}/`, payload);
  },
  deleteLog(id) {
    return api.delete(`evac_centers/evacuation-logs/${id}/`);
  },
  staffSummary() {
    return api.get("evac_centers/evacuation-logs/staff_summary/");
  },
  latestByCenter(centerId) {
    return api.get("evac_centers/evacuation-logs/latest_by_center/", { params: { center: centerId } });
  },
};