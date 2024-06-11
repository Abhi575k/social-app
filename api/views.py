from django.core.cache import cache
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from knox.models import AuthToken
from knox.views import LogoutView as KnoxLogoutView
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination

from .serializers import RegisterSerializer, UserSerializer, ProfileSerializer
from .models import User, FriendRequest

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
    
class SendFriendRequestView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserSerializer

    def post(self, request):
        user = request.user
        to_user_id = request.data.get('to_user_id')

        cache_key = f'friend_request_{user.id}'
        if cache.get(cache_key) is None:
            cache.set(cache_key, 0, timeout=60)
        current_count = cache.get(cache_key, 0)

        if current_count >= 3:
            return Response({'error': 'You can only send 3 friend requests per minute'}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        
        cache.incr(cache_key)
        cache.expire(cache_key, 60)

        if not to_user_id:
            return Response({'error': 'to_user_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        to_user = User.objects.filter(id=to_user_id).first()

        if to_user is None:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if user == to_user:
            return Response({'error': 'You cannot send a friend request to yourself'}, status=status.HTTP_400_BAD_REQUEST)
        
        if user.friends.filter(id=to_user_id).exists():
            return Response({'error': 'You are already friends with this user'}, status=status.HTTP_400_BAD_REQUEST)
        
        if FriendRequest.objects.filter(from_user=user, to_user=to_user).exists():
            return Response({'error': 'Friend request already sent'}, status=status.HTTP_400_BAD_REQUEST)
        
        if FriendRequest.objects.filter(from_user=to_user, to_user=user).exists():
            return Response({'error': 'You have already received a friend request from this user'}, status=status.HTTP_400_BAD_REQUEST)
        
        friend_request = FriendRequest(from_user=user, to_user=to_user)
        friend_request.save()

        return Response({'message': 'Friend request sent successfully'}, status=status.HTTP_201_CREATED)

class ViewSentFriendRequestsView(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserSerializer

    def get(self, request):
        user = request.user
        friend_requests = FriendRequest.objects.filter(from_user=user, is_accepted=False, is_rejected=False)
        
        # paginate the results
        paginator = UserSearchPagination()
        result_page = paginator.paginate_queryset(friend_requests, request)
        friend_requests_data = [{'id': friend_request.id, 'name': friend_request.to_user.name, 'email': friend_request.to_user.email} for friend_request in result_page]

        return paginator.get_paginated_response(friend_requests_data)

class ViewReceivedFriendRequestsView(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserSerializer

    def get(self, request):
        user = request.user
        friend_requests = FriendRequest.objects.filter(to_user=user, is_accepted=False, is_rejected=False)
        
        # paginate the results
        paginator = UserSearchPagination()
        result_page = paginator.paginate_queryset(friend_requests, request)
        friend_requests_data = [{'id': friend_request.id, 'name': friend_request.from_user.name, 'email': friend_request.from_user.email} for friend_request in result_page]

        return paginator.get_paginated_response(friend_requests_data)
    
class FriendRequestResponseView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserSerializer

    def post(self, request):
        request_id = request.data.get('request_id')

        if not request_id:
            return Response({'error': 'request_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        friend_request = FriendRequest.objects.filter(id=request_id).first()

        if friend_request is None:
            return Response({'error': 'Friend request not found'}, status=status.HTTP_404_NOT_FOUND)
        
        to_user = friend_request.to_user
        from_user = friend_request.from_user

        cur_user = request.user

        if cur_user != to_user:
            return Response({'error': 'You are not authorized to respond to this friend request'}, status=status.HTTP_401_UNAUTHORIZED)
        
        response = request.data.get('response')

        if from_user is None:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if response == 'accept':
            to_user.friends.add(from_user)
            from_user.friends.add(to_user)
            friend_request.is_accepted = True
            friend_request.save()
        elif response == 'reject':
            friend_request.is_rejected = True
            friend_request.save()
        else:
            return Response({'error': 'Invalid response'}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'message': 'Friend request response sent successfully'}, status=status.HTTP_200_OK)

class ListFriendsView(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserSerializer

    def get(self, request):
        user = request.user
        friends = user.friends.all()
        
        # paginate the results
        paginator = UserSearchPagination()
        result_page = paginator.paginate_queryset(friends, request)
        friends_data = [{'id': friend.id, 'name': friend.name, 'email': friend.email} for friend in result_page]

        return paginator.get_paginated_response(friends_data)
