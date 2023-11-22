from django.urls import path
from .views import DataVisualizationView

# Show it under the main url
urlpatterns = [
    path('', DataVisualizationView.as_view(), name='data_visualization'),
]
