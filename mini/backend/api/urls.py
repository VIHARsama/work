from django.urls import path
from .views import create_event, get_all_events, generate_unique_id, randomize_names, get_all_pairs, get_santa_pairs, get_specific_pair

urlpatterns = [
    path('get-all-events/', get_all_events, name='get_all_events'),
    path('get-all-pairs/', get_all_pairs, name='get_all_pairs'),
    path('create-event/', create_event, name='create_event'),
    path('generate-unique-id/', generate_unique_id, name='generate_unique_id'),
    path('upload/', randomize_names, name='randomize_names'),
    path('get-santa-pairs/', get_santa_pairs, name='get_santa_pairs'),
    path('get-specific-pair/', get_specific_pair, name='get_specific_pair')
]