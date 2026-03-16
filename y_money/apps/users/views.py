from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, ListView, TemplateView
from django.urls import reverse_lazy

from .forms import RegisterForm
from .models import Profile


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
        profile = Profile.objects.select_related('user').get(user=self.request.user)
        return profile.get_friends()
    
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
    

    
class SendFriendRequestView(LoginRequiredMixin):
    pass
    
class RemoveFriendView(LoginRequiredMixin):
    pass
    
class AcceptFriendRequestView(LoginRequiredMixin):
    pass

class RejectFriendRequestView(LoginRequiredMixin):
    pass

class CancelFriendRequestView(LoginRequiredMixin):
    pass
    
    