from django.urls import path
from .views import DataVisualizationView

urlpatterns = [
    path('eda/', DataVisualizationView.as_view(), name='data_visualization'),
]
