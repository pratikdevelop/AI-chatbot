from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.cache import cache
from .models import User, ChatMessage
from .serializers import UserSerializer, ChatMessageSerializer
from .utils import allowed_file, is_password_complex
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .chatbot import load_chatbot_model

logger = logging.getLogger('django')

class LoginView(APIView):
    throttle_scope = 'anon'

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({'error': 'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(username=username).first()
        if user and user.check_password(password):
            refresh = RefreshToken.for_user(user)
            return Response({
                'message': 'Login successful',
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh)
            }, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class SignupView(APIView):
    throttle_scope = 'anon'

    def post(self, request):
        data = request.data
        if not all([data.get('username'), data.get('email'), data.get('password'), data.get('name'), data.get('phone')]):
            return Response({'error': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)

        if not is_password_complex(data['password']):
            return Response({'error': 'Password must be 8+ chars with uppercase, lowercase, and numbers'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=data['username']).exists() or User.objects.filter(email=data['email']).exists() or User.objects.filter(phone=data['phone']).exists():
            return Response({'error': 'Username, email, or phone already exists'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            name=data['name'],
            phone=data['phone']
        )
        return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)

class ProfileView(APIView):
    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        user = request.user
        if 'profile_picture' in request.FILES:
            file = request.FILES['profile_picture']
            if file and allowed_file(file.name, file):
                filename = secure_filename(file.name)
                file.save(os.path.join('uploads', filename))
                user.profile_picture = filename

        data = request.data
        if 'preferences' in data:
            try:
                user.set_preferences(data['preferences'] if isinstance(data['preferences'], dict) else json.loads(data['preferences']))
            except json.JSONDecodeError:
                return Response({'error': 'Invalid preferences format'}, status=status.HTTP_400_BAD_REQUEST)
        if 'email' in data:
            user.email = data['email']
        if 'password' in data and is_password_complex(data['password']):
            user.set_password(data['password'])
        if 'name' in data:
            user.name = data['name']
        if 'phone' in data:
            user.phone = data['phone']

        user.save()
        return Response({'message': 'Profile updated successfully'}, status=status.HTTP_200_OK)

class ChatView(APIView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            self.model = load_chatbot_model()
        except FileNotFoundError:
            self.model = None

    def post(self, request):
        if self.model is None:
            return Response({'error': 'Model not trained yet'}, status=status.HTTP_400_BAD_REQUEST)
        
        data = request.data
        if 'message' not in data:
            return Response({'error': 'Message is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        message = data['message']
        prediction = self.model.predict([message])[0]
        return Response({'response': prediction}, status=status.HTTP_200_OK)

class HistoryView(APIView):
    def get(self, request):
        user = request.user
        messages = ChatMessage.objects.filter(user=user).order_by('-timestamp')[:100]
        serializer = ChatMessageSerializer(messages, many=True)
        return Response({'history': serializer.data}, status=status.HTTP_200_OK)

class UploadView(APIView):
    def get(self, request, filename):
        return send_from_directory('uploads', filename)