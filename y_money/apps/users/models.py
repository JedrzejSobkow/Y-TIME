from django.db import models
from django.dispatch import receiver
from django.contrib.auth.models import User
from apps.core.models import TimeStampedModel
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from django.db.models.signals import post_save


class Profile(TimeStampedModel):
    user = models.OneToOneField(User, on_delete = models.CASCADE, related_name='profile')
        
        
    def __str__(self):
        return f"[{self.user.username}] {self.user.first_name} {self.user.last_name}"
    
    def get_friends(self):
        return Profile.objects.select_related(
            "user"
        ).filter(
            Q(friendships_initiated__profile2 = self) |
            Q(friendships_received__profile1 = self)
        )
    
    def get_pending_friend_requests(self):
        return self.received_friend_requests.filter(
            status=FriendRequest.Status.PENDING
        ).select_related('from_profile__user')
    
    def get_sent_friend_requests(self):
        return self.sent_friend_requests.filter(
            status=FriendRequest.Status.PENDING
        ).select_related('to_profile__user')

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
    
    
class FriendRequest(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACCEPTED = "accepted", "Accepted"
        REJECTED = "rejected", "Rejected"
        CANCELLED = "cancelled", "Cancelled"
        

    from_profile = models.ForeignKey(Profile, on_delete = models.CASCADE, related_name = "sent_friend_requests")
    to_profile = models.ForeignKey(Profile, on_delete = models.CASCADE, related_name = "received_friend_requests")
    status = models.CharField(max_length = 20, choices = Status.choices, default = Status.PENDING)


    class Meta:
        constraints = [
            models.UniqueConstraint(fields = ["from_profile", "to_profile"], name = "unique_friend_request")
        ]
        
        indexes = [
            models.Index(fields = ["from_profile", "status"]),
            models.Index(fields = ["to_profile", "status"])
        ]

    def __str__(self):
        return f"{self.from_profile} → {self.to_profile} ({self.status})"
    
    def clean(self):
        if self.from_profile == self.to_profile:
            raise ValidationError("Cannot send friend request to yourself")
        
        if FriendRequest.objects.filter(
            (
                (Q(from_profile = self.to_profile) & Q(to_profile = self.from_profile)) |
                (Q(from_profile = self.from_profile) & Q(to_profile = self.to_profile))
            ) & Q(status = FriendRequest.Status.PENDING)
        ).exists():
            raise ValidationError("There is already one friend request pending in this relation")
        
        if Friendship.objects.filter(
            (Q(profile1 = self.to_profile) & Q(profile2 = self.from_profile)) |
            (Q(profile1 = self.from_profile) & Q(profile2 = self.to_profile))
        ).exists():
            raise ValidationError("You are already friends with this user")
        
        
    def accept(self, accepting_profile):
        if self.status != self.Status.PENDING:
            raise ValidationError("Request is not pending")
        
        if self.to_profile != accepting_profile:
            raise ValidationError("You cannot accept this request")
        
        with transaction.atomic():
            self.status = self.Status.ACCEPTED
            self.save()
            Friendship.objects.create(profile1 = self.from_profile, profile2 = self.to_profile)
        
    def reject(self, rejecting_profile):
        if self.status != self.Status.PENDING:
            raise ValidationError("Request is not pending")
        
        if self.to_profile != rejecting_profile:
            raise ValidationError("You cannot reject this request")
        
        self.status = self.Status.REJECTED
        self.save()
        
    def cancel(self, cancelling_profile):
        if self.status != self.Status.PENDING:
            raise ValidationError("Request is not pending")
        
        if self.from_profile != cancelling_profile:
            raise ValidationError("You cannot cancel this request")
        
        self.status = self.Status.CANCELLED
        self.save()
        
    def is_pending(self):
        return self.status == self.Status.PENDING
        
    
    
class Friendship(TimeStampedModel):
    profile1 = models.ForeignKey(Profile, on_delete = models.CASCADE, related_name = "friendships_initiated")
    profile2 = models.ForeignKey(Profile, on_delete = models.CASCADE, related_name = "friendships_received")
    
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields = ["profile1", "profile2"], name = "unique_friendship")
        ]
        
        indexes = [
            models.Index(fields = ["profile1"]),
            models.Index(fields = ["profile2"])
        ]
        
    def __str__(self):
        return f"{self.profile1} ↔ {self.profile2}"
    
    def save(self, *args, **kwargs):
        if self.profile1_id > self.profile2_id:
            self.profile1, self.profile2 = self.profile2, self.profile1
        return super().save(*args, **kwargs)
    
    def clean(self):
        if self.profile1 == self.profile2:
            raise ValidationError("Cannot be friends with yourself")
    