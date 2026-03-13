from django.db import models
from django.contrib.auth.models import User
from core.models import TimeStampedModel
from django.core.exceptions import ValidationError


class Profile(TimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
        
        
        
    def __str__(self):
        return f"[{self.user.email}] {self.user.first_name} {self.user.last_name}"
    
    
    
    
class FriendRequest(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACCEPTED = "accepted", "Accepted"
        REJECTED = "rejected", "Rejected"
        CANCELLED = "cancelled", "Cancelled"
        
        

    from_profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="sent_friend_requests")
    to_profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="received_friend_requests")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)



    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["from_profile", "to_profile"], name="unique_friend_request")
        ]
        
        indexes = [
            models.Index(fields=["from_profile", "status"]),
            models.Index(fields=["to_profile", "status"])
        ]

    def __str__(self):
        return f"{self.from_profile} → {self.to_profile} ({self.status})"
    
    def clean(self):
        if self.from_profile == self.to_profile:
            raise ValidationError("Cannot send friend request to yourself")
        
        
        
    def accept(self):
        self.status = self.Status.ACCEPTED
        self.save()
        
        Friendship.objects.create(self.from_profile, self.to_profile)
    
    
    
    
class Friendship(TimeStampedModel):
    profile1 = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="friendships_initiated")
    profile2 = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="friendships_received")
    
    
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["profile1", "profile2"], name="unique_friendship")
        ]
        
        indexes = [
            models.Index(fields=["profile1"]),
            models.Index(fields=["profile2"])
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
    