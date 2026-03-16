from django.urls import path
from .views import UserLoginView, UserLogoutView, UserRegisterView
from .views import FriendsPanelView, FriendsListView, PendingRequestsListView, SentRequestsListView

urlpatterns = [
    # TODO move it to the core urls
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('register/', UserRegisterView.as_view(), name='register'),
    
    path('friends/', FriendsPanelView.as_view(), name='frineds_panel'),
    path('friends/friends_list', FriendsListView.as_view(), name='friends_list'),
    path('friends/pending_list', PendingRequestsListView.as_view(), name='pending_list'),
    path('friends/sent_list', SentRequestsListView.as_view(), name='sent_list'),
    # path('friends/add/<int:profile_id>/', SendFriendRequestView.as_view(), name='send-friend-request'),
    # path('friends/request/accept/<int:request_id>/', AcceptFriendRequestView.as_view(), name='accept-friend-request'),
    # path('friends/request/reject/<int:request_id>/', RejectFriendRequestView.as_view(), name='reject-friend-request'),
    # path('friends/request/cancel/<int:request_id>/', CancelFriendRequestView.as_view(), name='cancel-friend-request'),
]
