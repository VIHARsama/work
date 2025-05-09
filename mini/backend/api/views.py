import bcrypt
import json
import uuid
import pandas as pd
import random

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import EventList, SantaPair
from .serializer import EventListSerializer, SantaPairSerializer

ALLOWED_EXTENSIONS = set(['xlsx', 'xls'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@api_view(['GET'])
def get_all_events(request):
    events = EventList.objects.all()
    serializer = EventListSerializer(events, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_all_pairs(request):
    pairs = SantaPair.objects.select_related('event').all()
    serializer = SantaPairSerializer(pairs, many=True)
    return Response(serializer.data)

# Create your views here.
@api_view(['POST'])
def create_event(request):
    try:
        data = json.loads(request.body)
        user_eventID = data.get('eventID')
        user_password = data.get('password')

        if not user_eventID or not user_password:
            return Response({"message": "Missing Event ID or Password"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            existing_event = EventList.objects.get(eventID=user_eventID)
            stored_password = existing_event.password.encode('utf-8')

            if bcrypt.checkpw(user_password.encode('utf-8'), stored_password):
                return Response({"message": "You are logged in"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": f'Event ID {user_eventID} already exists! Incorrect Password'}, status=status.HTTP_400_BAD_REQUEST)
        except EventList.DoesNotExist:
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(user_password.encode('utf-8'), salt).decode('utf-8')

            EventList.objects.create(eventID=user_eventID, password=hashed_password)
            return Response({'message': "Event Created Successfully"}, status=status.HTTP_201_CREATED)

    except json.JSONDecodeError:
        return Response({"error": "Invalid JSON"}, status=status.HTTP_400_BAD_REQUEST)

# generate unique event ID
@api_view(['GET'])
def generate_unique_id(request):
    while True:
        unique_id = str(uuid.uuid4())
        try:
            existing_id = EventList.objects.get(eventID=unique_id)
        except EventList.DoesNotExist:
            return Response(unique_id)

# read excel and randomize and assign santa pairs
@api_view(['POST'])
def randomize_names(request):
    try:
        print(request.FILES)
        user_eventID = request.POST.get('eventID')
        excel_file = request.FILES.get('excel_file')

        if not user_eventID:
            return Response({"error": "Missing event ID"}, status=status.HTTP_400_BAD_REQUEST)
        if not excel_file:
            return Response({"error": "No File Uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            try:
                event_instance = EventList.objects.get(eventID=user_eventID)
            except EventList.DoesNotExist:
                return Response({"error": f"Event with ID '{user_eventID}' does not exist."}, status=status.HTTP_404_NOT_FOUND)

            df = pd.read_excel(excel_file)
            if 'Names' not in df.columns:
                return Response({"error": "No 'Names' column found"}, status=status.HTTP_400_BAD_REQUEST)

            original_names = df['Names'].dropna().tolist()

            if len(original_names) < 2:
                return Response({"error": "Atleast two names are required to assign secret santas"}, status=status.HTTP_400_BAD_REQUEST)

            # assign santas
            def assign_santa(names):
                while True:
                    randomized = names[:]
                    random.shuffle(randomized)
                    if all(og != rd for og, rd in zip(names, randomized)):
                        return randomized
            
            assigned_names = assign_santa(original_names)

            pairs = []
            for og, ag in zip(original_names, assigned_names):
                pair = SantaPair(event=event_instance, santaPair=f"{og} -> {ag}")
                # Use bulk_create if creating multiple instances
                pairs.append(pair)

            # Use bulk_create to insert multiple records at once
            SantaPair.objects.bulk_create(pairs)
            
            return Response({"message": "Secret Santas assigned successfully!"}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except json.JSONDecodeError:
        return Response({"error": "Invalid JSON"}, status=status.HTTP_400_BAD_REQUEST)

# check for santa pairs with eventID
@api_view(['GET'])
def check_for_santapairs(request):
    user_eventID = request.query_params.get('eventID')

    if not user_eventID:
        return Response({"error": "event ID query parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        event_instance = EventList.objects.get(eventID=user_eventID)
    except EventList.DoesNotExist:
        return Response({"error": f"Event with ID '{user_eventID}' does not exist"}, status=status.HTTP_400_BAD_REQUEST)

    santa_pairs = SantaPair.objects.filter(event=event_instance)

    if not santa_pairs.exists():
        return Response({'message': 'No SantaPair found for this event ID.'}, status=status.HTTP_404_NOT_FOUND)

    serializer = SantaPairSerializer(santa_pairs, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

# 
@api_view(['GET'])
def get_santa_pairs(request):
    user_eventID = request.query_params.get('eventID')

    if not user_eventID:
        return Response({'error': 'eventID query parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        event = EventList.objects.get(eventID=user_eventID)
    except EventList.DoesNotExist:
        return Response({'error': f'No event found with eventID: {user_eventID}'}, status=status.HTTP_404_NOT_FOUND)

    santa_pairs = SantaPair.objects.filter(event=event)
    data = [{'id': pair.id, 'santaPair': pair.santaPair} for pair in santa_pairs]

    return Response({'eventID': user_eventID, 'santaPairs': data}, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_specific_pair(request):
    user_eventID = request.query_params.get('eventID')
    user_pairID = request.query_params.get('id')

    if not user_eventID or not user_pairID:
        return Response(
            {'error': 'Both eventID and id query parameters are required.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        event = EventList.objects.get(eventID=user_eventID)
    except EventList.DoesNotExist:
        return Response({'error': f'No event found with eventID: {user_eventID}'}, status=status.HTTP_404_NOT_FOUND)

    try:
        santa_pair = SantaPair.objects.get(id=user_pairID, event=event)
        data = {
            'id': santa_pair.id,
            'santaPair': santa_pair.santaPair,
            'eventID': santa_pair.event.eventID,
        }
        return Response(data, status=status.HTTP_200_OK)
    except SantaPair.DoesNotExist:
        return Response(
            {'error': f'No SantaPair with id {user_pairID} found for eventID {user_eventID}.'},
            status=status.HTTP_404_NOT_FOUND
        )