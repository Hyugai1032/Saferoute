# analytics_app/api_views.py
from rest_framework.throttling import ScopedRateThrottle
from datetime import datetime, timedelta
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from pathlib import Path
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Max
from .services.affected_population_report import build_affected_population_report
from .permissions import IsProvincialAdmin

from evac_app.models import EvacuationCenter, EvacuationLog
from .services.congestion import compute_congestion_risk, CongestionParams

    
class CenterCongestionRiskView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_scope = 'congestion'
    throttle_classes = [ScopedRateThrottle]

    def get(self, request, center_id: int):
        # Optional query params:
        # ?window=60&horizon=60
        try:
            window = int(request.query_params.get("window", 60))
            horizon = int(request.query_params.get("horizon", 60))
        except ValueError:
            return Response({"detail": "window and horizon must be integers."}, status=400)

        window = max(5, min(window, 24 * 60))     # clamp 5 min .. 24 hours
        horizon = max(5, min(horizon, 6 * 60))    # clamp 5 min .. 6 hours

        center = EvacuationCenter.objects.filter(id=center_id).first()
        if not center:
            return Response({"detail": "Center not found."}, status=404)

        result = compute_congestion_risk(
            center=center,
            EvacuationLogModel=EvacuationLog,
            params=CongestionParams(window_minutes=window, horizon_minutes=horizon),
        )

        status_code = 200 if "error" not in result else 400
        return Response(result, status=status_code)

class BulkCongestionRiskView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'congestion'

    def get(self, request):
        ids_param = request.query_params.get("center_ids", "")
        try:
            center_ids = [int(i) for i in ids_param.split(",") if i.strip()]
        except ValueError:
            return Response({"detail": "center_ids must be a comma-separated list of integers."}, status=400)

        window = max(5, min(int(request.query_params.get("window", 60)), 24 * 60))
        horizon = max(5, min(int(request.query_params.get("horizon", 60)), 6 * 60))

        centers = EvacuationCenter.objects.filter(id__in=center_ids)
        results = [
            compute_congestion_risk(
                center=center,
                EvacuationLogModel=EvacuationLog,
                params=CongestionParams(window_minutes=window, horizon_minutes=horizon),
            )
            for center in centers
        ]
        return Response(results)
    
class AnalyticsStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Total current evacuees = sum of latest total_current per center
        # Simplest reliable approach: take latest log per center, then sum in Python.

        latest_logs = (
            EvacuationLog.objects
            .values("center_id")
            .annotate(latest_time=Max("date_recorded"))
        )

        # Build a map center_id -> latest_time
        latest_map = {x["center_id"]: x["latest_time"] for x in latest_logs}

        total_evacuees = 0
        active_centers = 0

        for center_id, latest_time in latest_map.items():
            latest = (
                EvacuationLog.objects
                .filter(center_id=center_id, date_recorded=latest_time)
                .values("total_current")
                .first()
            )
            if latest:
                total_evacuees += int(latest["total_current"] or 0)
                active_centers += 1

        return Response({
            "total_evacuees": total_evacuees,
            "active_centers": active_centers,
        })
    
class AffectedPopulationReportView(APIView):
    permission_classes = [IsAuthenticated, IsProvincialAdmin]

    def get(self, request):
        as_of_raw = request.query_params.get("as_of")

        if as_of_raw:
            as_of = parse_datetime(as_of_raw)

            if as_of is None:
                return Response({"detail": "Invalid as_of datetime format."}, status=400)

            if timezone.is_aware(as_of):
                as_of = timezone.make_naive(as_of, timezone.get_current_timezone())
        else:
            as_of = timezone.localtime(timezone.now()).replace(tzinfo=None)

        data = build_affected_population_report(
            EvacuationCenterModel=EvacuationCenter,
            EvacuationLogModel=EvacuationLog,
            as_of=as_of,
        )
        return Response(data)