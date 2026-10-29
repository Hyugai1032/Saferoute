from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("audit_app", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="auditlog",
            name="action",
            field=models.CharField(
                choices=[
                    ("CREATE", "Created"),
                    ("UPDATE", "Updated"),
                    ("DELETE", "Deleted"),
                    ("LOGIN", "Logged in"),
                    ("LOGIN_FAILED", "Failed login"),
                    ("PERMISSION_DENIED", "Permission denied"),
                    ("EXPORT", "Exported data"),
                    ("ROUTE", "Route request"),
                    ("OTHER", "Other"),
                ],
                db_index=True,
                max_length=20,
            ),
        ),
    ]