from django.db import models


class Ticket(models.Model):
    ticket_id = models.CharField(max_length=255, unique=True)  # Ensure unique constraint
    summary = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    priority = models.CharField(
        max_length=50,
        choices=[
            ('Highest', 'Highest'),
            ('High', 'High'),
            ('Medium', 'Medium'),
            ('Low', 'Low'),
            ('Lowest', 'Lowest'),
        ]
    )
    status = models.CharField(
        max_length=50,
        choices=[
            ('Open', 'Open'),
            ('In Progress', 'In Progress'),
            ('Done', 'Done'),
            ('Closed', 'Closed'),
        ],
        default='Open'
    )
    assignee = models.CharField(max_length=255, null=True, blank=True)
    reporter = models.CharField(max_length=255)
    tags = models.JSONField(null=True, blank=True)
    label = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.ticket_id
