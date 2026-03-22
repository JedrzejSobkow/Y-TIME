from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, ListView, TemplateView, View
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.urls import reverse_lazy
from django.http import JsonResponse

from .forms import RegisterForm
from .models import Profile, FriendRequest, Friendship


# TODO move it to the core views
class UserLoginView(LoginView):
    template_name = "registration/login.html"

    
class UserLogoutView(LogoutView):
    pass


class UserRegisterView(CreateView):
    form_class = RegisterForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("login")
    
    

    
class FriendsPanelView(LoginRequiredMixin, TemplateView):
    template_name = "friends/panel.html"
    
class FriendsListView(LoginRequiredMixin, ListView):
    template_name = "friends/partials/friends_list.html"
    context_object_name = "friends"
    
    def get_queryset(self):
        return self.request.user.profile.get_friends()
    
class PendingRequestsListView(LoginRequiredMixin, ListView):
    template_name = "friends/partials/pending_list.html"
    context_object_name = "pending_requests"
    
    def get_queryset(self):
        return self.request.user.profile.get_pending_friend_requests()
    
    
class SentRequestsListView(LoginRequiredMixin, ListView):
    template_name = "friends/partials/sent_list.html"
    context_object_name = "sent_requests"
    
    def get_queryset(self):
        return self.request.user.profile.get_sent_friend_requests()
    

    
class SendFriendRequestView(LoginRequiredMixin, View):
    def post(self, request, profile_id):
        try:
            from_profile = request.user.profile
            to_profile = get_object_or_404(Profile, id = profile_id)
            
            if from_profile == to_profile:
                return JsonResponse({
                    'success': False,
                    'error': "Cannot send friend request to yourself"
                }, status = 400)
                
            if Friendship.objects.filter(
                Q(profile1 = from_profile, profile2 = to_profile) |
                Q(profile1 = to_profile, profile2 = from_profile)
            ).exists():
                return JsonResponse({
                    'success': False,
                    'error': "You are already friends"
                }, status = 400)
                
            if FriendRequest.objects.filter(
                Q(from_profile = from_profile, to_profile = to_profile) |
                Q(from_profile = to_profile, to_profile = from_profile)
            ).exists():
                return JsonResponse({
                    'success': False,
                    'error': "Friend request already exists"
                }, status = 400)
                
            friend_request = FriendRequest.objects.create(
                from_profile = from_profile,
                to_profile = to_profile
            )
            
            return JsonResponse({
                'success': True,
                'message': "Friend request sent"
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status = 400)
    
class RemoveFriendView(LoginRequiredMixin, View):
    def post(self, request, profile_id):
        try:
            removing_user = request.user.profile
            user_to_be_removed = get_object_or_404(Profile, id = profile_id)
                
            friendship = Friendship.objects.filter(
                Q(profile1 = removing_user, profile2 = user_to_be_removed) |
                Q(profile1 = user_to_be_removed, profile2 = removing_user)
            ).first()
            if not friendship:
                return JsonResponse({
                    'success': False,
                    'error': "You are not in a friendship with that user"
                }, status = 400)
                
            friendship.delete()

            return JsonResponse({
                'success': True,
                'message': f"Friendship with user {str(user_to_be_removed)} has been removed"
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status = 400)
    
class AcceptFriendRequestView(LoginRequiredMixin, View):
    pass

class RejectFriendRequestView(LoginRequiredMixin, View):
    pass

class CancelFriendRequestView(LoginRequiredMixin, View):
    pass
    
    