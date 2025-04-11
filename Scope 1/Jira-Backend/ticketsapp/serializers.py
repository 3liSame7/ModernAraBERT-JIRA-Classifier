from rest_framework import serializers


class TicketSerializer(serializers.Serializer):
    ticket_id = serializers.IntegerField()
    summary = serializers.CharField()
    description = serializers.CharField()
    priority = serializers.CharField()
    status = serializers.CharField()
    reporter = serializers.EmailField()
    label = serializers.CharField(required=False, allow_blank=True)
    created_at = serializers.CharField()

class PredictionSerializer(serializers.Serializer):
    label = serializers.CharField()
    confidence = serializers.FloatField()


