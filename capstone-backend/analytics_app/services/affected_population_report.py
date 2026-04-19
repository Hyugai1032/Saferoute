from collections import defaultdict
from typing import Any

from django.db.models import Max, Sum
from django.utils import timezone


def _safe_int(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def _blank_row(row_type="data", province="", municipality="", barangay=""):
    return {
        "row_type": row_type,
        "province": province,
        "municipality": municipality,
        "barangay": barangay,

        "affected_brgys": 0,
        "affected_families": 0,
        "affected_persons": 0,

        "ecs_cum": 0,
        "ecs_now": 0,

        "inside_families_cum": 0,
        "inside_families_now": 0,
        "inside_persons_cum": 0,
        "inside_persons_now": 0,

        "outside_families_cum": 0,
        "outside_families_now": 0,
        "outside_persons_cum": 0,
        "outside_persons_now": 0,

        "total_families_cum": 0,
        "total_families_now": 0,
        "total_persons_cum": 0,
        "total_persons_now": 0,
    }


def _add_totals(target: dict, row: dict):
    fields = [
        "affected_brgys",
        "affected_families",
        "affected_persons",
        "ecs_cum",
        "ecs_now",
        "inside_families_cum",
        "inside_families_now",
        "inside_persons_cum",
        "inside_persons_now",
        "outside_families_cum",
        "outside_families_now",
        "outside_persons_cum",
        "outside_persons_now",
        "total_families_cum",
        "total_families_now",
        "total_persons_cum",
        "total_persons_now",
    ]
    for field in fields:
        target[field] += _safe_int(row.get(field))


def build_affected_population_report(*, EvacuationCenterModel, EvacuationLogModel, as_of=None):
    if as_of is None:
        as_of = timezone.now()

    centers = list(
        EvacuationCenterModel.objects.select_related("municipality", "barangay").values(
            "id",
            "name",
            "province",
            "municipality__name",
            "barangay__name",
            "shelter_category",
        )
    )

    def has_activity(row):
        return any([
            row["affected_families"] > 0,
            row["affected_persons"] > 0,
            row["inside_families_now"] > 0,
            row["inside_persons_now"] > 0,
            row["outside_families_now"] > 0,
            row["outside_persons_now"] > 0,
            row["inside_families_cum"] > 0,
            row["outside_families_cum"] > 0,
        ])

    center_map = {
        c["id"]: {
            "province": c.get("province") or "Oriental Mindoro",
            "municipality": c.get("municipality__name") or "Unknown Municipality",
            "barangay": c.get("barangay__name") or c.get("name") or "Unknown Barangay",
            "shelter_category": c.get("shelter_category") or "INSIDE_EC",
        }
        for c in centers
    }

    cumulative_logs = (
        EvacuationLogModel.objects
        .filter(date_recorded__lte=as_of)
        .values("center_id")
        .annotate(
            families_in_sum=Sum("families_in"),
            persons_in_sum=Sum("individuals_in"),
        )
    )

    cumulative_map = {
        row["center_id"]: {
            "families_in_sum": _safe_int(row["families_in_sum"]),
            "persons_in_sum": _safe_int(row["persons_in_sum"]),
        }
        for row in cumulative_logs
    }

    latest_times = (
        EvacuationLogModel.objects
        .filter(date_recorded__lte=as_of)
        .values("center_id")
        .annotate(latest_time=Max("date_recorded"))
    )

    latest_snapshot_map = {}
    for row in latest_times:
        center_id = row["center_id"]
        latest_time = row["latest_time"]

        latest = (
            EvacuationLogModel.objects
            .filter(center_id=center_id, date_recorded=latest_time)
            .values("total_current_families", "total_current")
            .order_by("-id")
            .first()
        )

        latest_snapshot_map[center_id] = {
            "families_now": _safe_int((latest or {}).get("total_current_families")),
            "persons_now": _safe_int((latest or {}).get("total_current")),
        }

    grouped = defaultdict(dict)

    for center_id, location in center_map.items():
        province = location["province"]
        municipality = location["municipality"]
        barangay = location["barangay"]
        shelter_category = location["shelter_category"]

        key = (province, municipality, barangay)

        if key not in grouped:
            grouped[key] = _blank_row(
                row_type="data",
                province=province,
                municipality=municipality,
                barangay=barangay,
            )

        row = grouped[key]

        cum = cumulative_map.get(center_id, {"families_in_sum": 0, "persons_in_sum": 0})
        snap = latest_snapshot_map.get(center_id, {"families_now": 0, "persons_now": 0})

        # temporary approximation until a separate affected-population source exists
        row["affected_brgys"] = 1
        row["affected_families"] += cum["families_in_sum"]
        row["affected_persons"] += cum["persons_in_sum"]

        if shelter_category == "INSIDE_EC":
            if cum["families_in_sum"] > 0 or cum["persons_in_sum"] > 0:
                row["ecs_cum"] += 1

            if snap["families_now"] > 0 or snap["persons_now"] > 0:
                row["ecs_now"] += 1

            row["inside_families_cum"] += cum["families_in_sum"]
            row["inside_families_now"] += snap["families_now"]
            row["inside_persons_cum"] += cum["persons_in_sum"]
            row["inside_persons_now"] += snap["persons_now"]

        elif shelter_category == "OUTSIDE_EC":
            row["outside_families_cum"] += cum["families_in_sum"]
            row["outside_families_now"] += snap["families_now"]
            row["outside_persons_cum"] += cum["persons_in_sum"]
            row["outside_persons_now"] += snap["persons_now"]

        row["total_families_cum"] = row["inside_families_cum"] + row["outside_families_cum"]
        row["total_families_now"] = row["inside_families_now"] + row["outside_families_now"]
        row["total_persons_cum"] = row["inside_persons_cum"] + row["outside_persons_cum"]
        row["total_persons_now"] = row["inside_persons_now"] + row["outside_persons_now"]

    filtered_rows = [
        row for row in grouped.values()
        if has_activity(row)
    ]

    data_rows = sorted(
        filtered_rows,
        key=lambda r: (r["municipality"], r["barangay"])
    )

    if not data_rows:
        return {
            "title": "Affected Population Report",
            "as_of": as_of.isoformat(),
            "rows": [],
            "note": "No affected areas found for this time period."
        }

    final_rows = []
    grand_total = _blank_row(row_type="grand_total", barangay="Total")

    current_municipality = None
    subtotal = None

    for row in data_rows:
        municipality = row["municipality"]

        if municipality != current_municipality:
            if subtotal is not None:
                final_rows.append(subtotal)

            current_municipality = municipality
            subtotal = _blank_row(row_type="subtotal", municipality=municipality, barangay="Subtotal")

        final_rows.append(row)
        _add_totals(subtotal, row)
        _add_totals(grand_total, row)

    if subtotal is not None:
        final_rows.append(subtotal)

    final_rows.append(grand_total)

    return {
        "title": "Affected Population Report",
        "as_of": as_of.isoformat(),
        "rows": final_rows,
    }