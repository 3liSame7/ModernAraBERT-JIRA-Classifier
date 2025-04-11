from django.urls import path
from .views import PredictLabelView, CollectTicketView


urlpatterns = [
    path('api/collect-tickets/', CollectTicketView.as_view(), name='collect-tickets'),
    path('api/predict-labels/', PredictLabelView.as_view(), name='predict-labels'),
]
