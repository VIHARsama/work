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
            return Response({'message': 'You are logged in'}, status=status.HTTP_201_CREATED)

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
        data = json.loads(request.body)
        user_eventID = data.get('eventID')
        excel_file = request.FILES.get("file")

        if not user_eventID:
            return Response({"error": "Missing event ID"}, status=status.HTTP_400_BAD_REQUEST)
        if not excel_file:
            return Response({"error": "No File Uploaded"}, status=status.HTTP_400_BAD_REQUEST)
        if not allowed_file(excel_file):
            return Response({"error": "The uploaded file is not in excel format"}, status=status.HTTP_400_BAD_REQUEST)

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
                pairs.append(pair)
            SantaPair.objects.create(pair)
            
            return Response({"message": "Secret Santas assigned successfully!"}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except json.JSONDecodeError:
        return Response({"error": "Invalid JSON"}, status=status.HTTP_400_BAD_REQUEST)

# check for santa pairs with eventID
@api_view(['GET'])
def check_for_santapairs(request):
    user_eventID = request.GET.get('eventID')

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