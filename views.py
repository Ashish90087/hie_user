# user_service/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny  
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from .models import User
from .serializers import UserSerializer, UserLoginSerializer
from .tasks import check_user_registered, send_confirmation_email

# user_service/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import User
from .serializers import UserSerializer
from .tasks import send_confirmation_email  # Assuming the task is still required

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    # Validate and create the user using the serializer
    serializer = UserSerializer(data=request.data)
    
    if serializer.is_valid():
        try:
            # Save the user and return success response
            user = serializer.save()
            
            # Send confirmation email in the background (via Celery)
            send_confirmation_email.delay(user.id)
            
            # Return success message
            return Response({"message": "User registered and confirmation email sent!"}, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            # Return error response if user creation fails
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    else:
        # Return validation errors if the serializer is invalid
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# @api_view(['POST'])
# @permission_classes([AllowAny])
# @api_view(['POST'])
# def register(request):
#     serializer = UserSerializer(data=request.data)
    
#     if serializer.is_valid():
#         username = serializer.validated_data['username']
#         email = serializer.validated_data['email']
        
#         # Check if user exists synchronously
#         is_registered = check_user_registered(username, email)
#         if is_registered:
#             user = serializer.save()
#             send_confirmation_email.delay(user.id)
#             return Response({"message": "User registered and confirmation email sent!"}, status=status.HTTP_201_CREATED)
#         else:
#             return Response({"message": "User already exists!"}, status=status.HTTP_400_BAD_REQUEST)
#     else:
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# def register(request):
#     serializer = UserSerializer(data=request.data)
    
#     if serializer.is_valid():
#         username = serializer.validated_data['username']
#         email = serializer.validated_data['email']
        
#         # Check if user is already registered
#         is_registered = check_user_registered.delay(username, email)

#         if is_registered:
#             # Create the user
#             user = serializer.save()

#             # Send confirmation email asynchronously
#             send_confirmation_email.delay(user.id)

#             return Response({"message": "User registered and confirmation email sent!"}, status=status.HTTP_201_CREATED)
#         else:
#             return Response({"message": "User already exists!"}, status=status.HTTP_400_BAD_REQUEST)
#     else:
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login(request):
    serializer = UserLoginSerializer(data=request.data)
    
    if serializer.is_valid():
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        # Authenticate the user
        user = authenticate(username=username, password=password)

        if user:
            # Login successful, generate JWT token here (using `rest_framework_simplejwt`)
            from rest_framework_simplejwt.tokens import RefreshToken
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token)
            }, status=status.HTTP_200_OK)
        
        return Response({"message": "Invalid credentials!"}, status=status.HTTP_401_UNAUTHORIZED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
