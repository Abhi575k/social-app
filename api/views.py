from rest_framework import generics, permissions, status
from rest_framework.response import Response
from knox.models import AuthToken
from knox.views import LogoutView as KnoxLogoutView
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination

from .serializers import RegisterSerializer, UserSerializer, ProfileSerializer
from .models import User

class RegisterView(generics.GenericAPIView):
    serializer_class = RegisterSerializer
    queryset = User.objects.all()

    def post(self, request, *args, **kwargs):
        email, password = request.data.get('email'), request.data.get('password')
        email = email.lower()

        if not email or not password:
            return Response({'error': 'Email and password are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(email=email).exists():
            return Response({'error': 'Email already in use'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user = serializer.save()
        _, token = AuthToken.objects.create(user)
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": token
        }, status=status.HTTP_201_CREATED)

class LoginView(generics.GenericAPIView):
    serializer_class = RegisterSerializer
    queryset = User.objects.all()

    def post(self, request, *args, **kwargs):
        email, password = request.data.get('email'), request.data.get('password')
        email = email.lower()

        if not email or not password:
            return Response({'error': 'Email and password are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.filter(email=email).first()

        if user is None:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if not user.check_password(password):
            return Response({'error': 'Incorrect password'}, status=status.HTTP_400_BAD_REQUEST)
        
        _, token = AuthToken.objects.create(user)

        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": token
        }, status=status.HTTP_200_OK)

class LogoutView(KnoxLogoutView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):

        response = super().post(request, *args, **kwargs)

        return Response({
            'message': 'Successfully logged out.'
        }, status=status.HTTP_200_OK)

class ProfileView(generics.RetrieveAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ProfileSerializer

    def get(self, request):
        user = request.user
        profile_data = ProfileSerializer(user).data
        return Response(profile_data, status=status.HTTP_200_OK)

    def put(self, request):
        user = request.user
        data = request.data

        user.name = data.get('name', user.name)
        user.email = data.get('email', user.email)

        password1 = data.get('password1')
        password2 = data.get('password2')

        if password1 and password2:
            if password1 != password2:
                return Response({'error': 'Passwords do not match'}, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(password1)
        
        user.save()

        return Response({'message': 'Profile updated successfully'}, status=status.HTTP_200_OK)

class UserSearchPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 10

class UserSearchView(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserSerializer

    def get(self, request):
        search_query = self.request.query_params.get('q', '')
        
        users = User.objects.filter(
            Q(email__icontains=search_query) | Q(name__icontains=search_query)
        ).distinct()

        paginator = UserSearchPagination()
        
        result_page = paginator.paginate_queryset(users, request)
        users_data = [{'id': user.id, 'name': user.name, 'email': user.email} for user in result_page]
        
        return paginator.get_paginated_response(users_data)

