from rest_framework import serializers

from .models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    action_label = serializers.CharField(source="get_action_display", read_only=True)
    municipality_name = serializers.SerializerMethodField()

    class Meta:
        model = AuditLog
        fields = [
            "id", "timestamp", "action", "action_label",
            "actor_id", "actor_email", "actor_name", "actor_role",
            "municipality_id", "municipality_name",
            "resource_type", "resource_id", "resource_label", "details",
            "method", "path", "status_code", "ip_address", "user_agent", "request_id",
        ]
        read_only_fields = fields

    def get_municipality_name(self, obj):
        return self.context.get("municipality_names", {}).get(obj.municipality_id, "")
