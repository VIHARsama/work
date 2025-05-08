from django.urls import path
from .views import create_event, get_all_events, generate_unique_id, randomize_names

urlpatterns = [
    path('create-event/', create_event, name='create_event'),
    path('get-all-events/', get_all_events, name='get_all_events'),
    path('generate-unique-id/', generate_unique_id, name='generate_unique_id'),
    path('upload', randomize_names, name='randomize_names')
]