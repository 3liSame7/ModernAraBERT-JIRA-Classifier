# Generated by Django 5.1.5 on 2025-01-28 20:00

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Ticket",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("ticket_id", models.CharField(max_length=255, unique=True)),
                ("summary", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True, null=True)),
                (
                    "priority",
                    models.CharField(
                        choices=[
                            ("Highest", "Highest"),
                            ("High", "High"),
                            ("Medium", "Medium"),
                            ("Low", "Low"),
                            ("Lowest", "Lowest"),
                        ],
                        max_length=50,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("Open", "Open"),
                            ("In Progress", "In Progress"),
                            ("Done", "Done"),
                            ("Closed", "Closed"),
                        ],
                        default="Open",
                        max_length=50,
                    ),
                ),
                ("assignee", models.CharField(blank=True, max_length=255, null=True)),
                ("reporter", models.CharField(max_length=255)),
                ("tags", models.JSONField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
