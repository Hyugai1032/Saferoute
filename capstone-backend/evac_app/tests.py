import uuid

from django.test import TestCase
from rest_framework.test import APIClient

from auth_app.models import CustomUser, Municipality
from evac_app.models import EvacuationCenter, EvacuationReason, Evacuee

SYNC_URL = "/api/evac_centers/evacuees/sync/"
CREATE_URL = "/api/evac_centers/evacuees/"


class OfflineEvacueeSyncTests(TestCase):
    """Records typed in offline on a phone and uploaded later, possibly more than once."""

    def setUp(self):
        self.mun = Municipality.objects.create(name="Naujan")
        self.other_mun = Municipality.objects.create(name="Victoria")
        self.center = EvacuationCenter.objects.create(name="Naujan Gym", municipality=self.mun)
        self.other_center = EvacuationCenter.objects.create(name="Victoria Hall", municipality=self.other_mun)
        self.reason = EvacuationReason.objects.create(name="Typhoon")

        self.staff = CustomUser.objects.create_user(
            email="staff@example.com", password="x", first_name="Ana", last_name="Cruz",
            role="EVAC_CENTER_STAFF", municipality=self.mun, assigned_center=self.center,
        )
        self.client = APIClient()
        self.client.force_authenticate(self.staff)

    def record(self, **overrides):
        data = {
            "client_id": str(uuid.uuid4()),
            "center": self.center.id,
            "first_name": "Juan",
            "last_name": "Dela Cruz",
            "age": 34,
            "sex": "MALE",
            "reason_for_evacuation": self.reason.id,
            "recorded_at": "2026-10-23T08:15:00",
        }
        data.update(overrides)
        return data

    def sync(self, *records):
        return self.client.post(SYNC_URL, {"records": list(records)}, format="json")

    def test_sync_creates_and_records_who_and_when(self):
        rec = self.record()
        res = self.sync(rec)

        self.assertEqual(res.status_code, 200)
        result = res.data["results"][0]
        self.assertEqual(result["status"], "created")
        evacuee = Evacuee.objects.get(client_id=rec["client_id"])
        self.assertEqual(evacuee.registered_by, self.staff)
        self.assertEqual(evacuee.recorded_at.isoformat(), "2026-10-23T08:15:00")

    def test_retrying_same_batch_never_duplicates(self):
        rec = self.record()
        self.sync(rec)
        res = self.sync(rec)

        self.assertEqual(res.data["results"][0]["status"], "exists")
        self.assertEqual(Evacuee.objects.filter(client_id=rec["client_id"]).count(), 1)

    def test_one_bad_record_does_not_block_the_rest(self):
        good, bad = self.record(), self.record(first_name="")
        res = self.sync(good, bad)

        statuses = [r["status"] for r in res.data["results"]]
        self.assertEqual(statuses, ["created", "invalid"])
        self.assertIn("first_name", res.data["results"][1]["errors"])

    def test_other_center_is_rejected(self):
        res = self.sync(self.record(center=self.other_center.id))
        self.assertEqual(res.data["results"][0]["status"], "rejected")
        self.assertFalse(Evacuee.objects.exists())

    def test_reason_deactivated_while_offline_is_still_accepted(self):
        self.reason.is_active = False
        self.reason.save()
        res = self.sync(self.record())
        self.assertEqual(res.data["results"][0]["status"], "created")

    def test_same_name_at_center_is_flagged(self):
        self.sync(self.record())
        res = self.sync(self.record(first_name="JUAN "))
        result = res.data["results"][0]
        self.assertEqual(result["status"], "created")
        self.assertEqual(len(result["possible_duplicates"]), 1)

    def test_missing_client_id_is_invalid(self):
        res = self.sync(self.record(client_id="not-a-uuid"))
        self.assertEqual(res.data["results"][0]["status"], "invalid")

    def test_batch_size_is_limited(self):
        res = self.sync(*[self.record() for _ in range(51)])
        self.assertEqual(res.status_code, 400)

    def test_citizen_cannot_sync(self):
        citizen = CustomUser.objects.create_user(email="c@example.com", password="x",
                                                 first_name="C", last_name="D")
        self.client.force_authenticate(citizen)
        self.assertEqual(self.sync(self.record()).status_code, 403)

    def test_plain_create_is_idempotent_too(self):
        rec = self.record()
        first = self.client.post(CREATE_URL, rec, format="json")
        second = self.client.post(CREATE_URL, rec, format="json")

        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(first.data["id"], second.data["id"])
        self.assertEqual(Evacuee.objects.count(), 1)

    def test_editing_cannot_change_client_id(self):
        rec = self.record()
        created = self.client.post(CREATE_URL, rec, format="json").data
        self.client.patch(f"{CREATE_URL}{created['id']}/", {"client_id": str(uuid.uuid4())}, format="json")
        self.assertEqual(str(Evacuee.objects.get().client_id), rec["client_id"])
