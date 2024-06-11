from django.urls import path
from .views import RegisterView, LoginView, LogoutView, ProfileView, UserSearchView, SendFriendRequestView, ViewSentFriendRequestsView, ViewReceivedFriendRequestsView, FriendRequestResponseView, ListFriendsView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('search/', UserSearchView.as_view(), name='search'),
    path('send-request/', SendFriendRequestView.as_view(), name='send-friend-request'),
    path('sent-requests/', ViewSentFriendRequestsView.as_view(), name='sent-friend-requests'),
    path('received-requests/', ViewReceivedFriendRequestsView.as_view(), name='received-friend-requests'),
    path('request-response/', FriendRequestResponseView.as_view(), name='friend-request-response'),
    path('friends/', ListFriendsView.as_view(), name='list-friends'),
]