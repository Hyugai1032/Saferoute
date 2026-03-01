# from django.shortcuts import get_object_or_404
# from django.utils import timezone
# from django.db.models import Q
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

# from .models import HazardReport
# from .serializers import HazardReportSerializer


# class HazardReportView(APIView):
#     permission_classes = [IsAuthenticated]
#     parser_classes = [JSONParser, MultiPartParser, FormParser]  

#     def get(self, request):
#         qs = HazardReport.objects.filter(status="REPORTED")

#         if request.user.role == "MUNICIPAL_ADMIN":
#             qs = qs.filter(municipality=request.user.municipality)

#             serializer = HazardReportSerializer(
#                 qs,
#                 many=True,
#                 context={"request": request}
#             )

#     def post(self, request):
#         serializer = HazardReportSerializer(data=request.data, context={"request": request})
#         serializer.is_valid(raise_exception=True)

#         user = request.user
#         if not user.municipality:
#             return Response({"municipality": "No municipality assigned"}, status=400)

#         report = serializer.save(
#             reporter=user,
#             municipality=user.municipality,
#             status="REPORTED"
#         )
#         return Response(HazardReportSerializer(report).data, status=201)

#     def patch(self, request, pk):
#         report = get_object_or_404(HazardReport, pk=pk)

#         if request.user.role not in ["PROVINCIAL_ADMIN", "MUNICIPAL_ADMIN"]:
#             return Response({"detail": "Forbidden"}, status=403)

#         new_status = request.data.get("status")
#         if new_status not in ["APPROVED", "DISMISSED"]:
#             return Response({"status": "Only APPROVED or DISMISSED allowed."}, status=400)

#         report.status = new_status
#         report.reviewed_by = request.user
#         report.reviewed_at = timezone.now()
#         report.save()

#         return Response(HazardReportSerializer(report).data)

# # from django.shortcuts import render
# # from django.shortcuts import get_object_or_404


# # from .models import HazardReport
# # from .serializers import HazardReportSerializer
# # from rest_framework.views import APIView
# # from rest_framework.response import Response
# # from rest_framework.permissions import IsAuthenticated
# # from django.db.models import Q

# # class HazardPendingList(APIView):
# #     permission_classes = [IsAuthenticated]

# #     def get(self, request):
# #         user = request.user
# #         qs = HazardReport.objects.select_related("municipality", "reporter").filter(status="REPORTED")

# #         if user.role == "MUNICIPAL_ADMIN":
# #             qs = qs.filter(municipality=user.municipality)

# #         search = request.query_params.get("search")
# #         if search:
# #             qs = qs.filter(
# #                 Q(hazard_type__icontains=search) |
# #                 Q(description__icontains=search) |
# #                 Q(reporter__email__icontains=search)
# #             )

# #         data = HazardReportSerializer(qs.order_by("-created_at"), many=True).data
# #         return Response(data)

# # from rest_framework.parsers import MultiPartParser, FormParser
# # from rest_framework import status as drf_status

# # class HazardCreate(APIView):
# #     permission_classes = [IsAuthenticated]
# #     parser_classes = [MultiPartParser, FormParser]

# #     def post(self, request):
# #         serializer = HazardReportSerializer(data=request.data)
# #         if serializer.is_valid():
# #             user = request.user

# #             mun = getattr(user, "municipality", None) or serializer.validated_data.get("municipality")
# #             if not mun:
# #                 return Response({"municipality": "Municipality is required."}, status=400)

# #             report = serializer.save(
# #                 reporter=user,
# #                 municipality=mun,
# #                 status="REPORTED"
# #             )
# #             return Response(HazardReportSerializer(report).data, status=drf_status.HTTP_201_CREATED)

# #         return Response(serializer.errors, status=400)
    

# # from django.shortcuts import get_object_or_404
# # from django.utils import timezone

# # class HazardReportView(APIView):
# #     permission_classes = [IsAuthenticated]
# #     parser_classes = [MultiPartParser, FormParser]

# #     def post(self, request):
# #         serializer = HazardReportSerializer(data=request.data, context={"request": request})
# #         if not serializer.is_valid():
# #             return Response(serializer.errors, status=400)

# #         user = request.user
# #         mun = getattr(user, "municipality", None)
# #         if not mun:
# #             return Response({"municipality": "Your account has no municipality assigned."}, status=400)

# #         # ✅ force required fields
# #         report = serializer.save(
# #             reporter=user,
# #             municipality=mun,
# #             status="REPORTED",
# #         )
# #         return Response(HazardReportSerializer(report).data, status=201)

# #     def patch(self, request, pk=None):
# #         report = get_object_or_404(HazardReport, pk=pk)
# #         user = request.user

# #         # role check
# #         if user.role not in ["PROVINCIAL_ADMIN", "MUNICIPAL_ADMIN"]:
# #             return Response({"detail": "Not allowed."}, status=403)

# #         # municipality scope
# #         if user.role == "MUNICIPAL_ADMIN" and report.municipality != user.municipality:
# #             return Response({"detail": "Not allowed."}, status=403)

# #         new_status = request.data.get("status")
# #         if new_status not in ["VALIDATED", "DISMISSED"]:
# #             return Response({"status": "Only VALIDATED or DISMISSED allowed."}, status=400)

# #         report.status = new_status
# #         report.reviewed_by = user
# #         report.reviewed_at = timezone.now()

# #         if new_status == "VALIDATED":
# #             report.validated_at = timezone.now()
# #             report.dismissed_at = None
# #         else:
# #             report.dismissed_at = timezone.now()
# #             report.validated_at = None

# #         report.save()
# #         return Response(HazardReportSerializer(report).data)
