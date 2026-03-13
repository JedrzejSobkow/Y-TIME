from django.contrib.auth.models import User
from apps.users.models import Profile, Friendship, FriendRequest
from django.core.exceptions import ValidationError

from django.test import TestCase

class ProfileModelTests(TestCase):
    def test_profile_creation(self):
        user = User.objects.create(username="test", email="test@gmail.com", first_name="Test_first", last_name="Test_last")
        profile = Profile.objects.create(user=user)
        
        self.assertEqual(profile.user.username, "test")
        self.assertEqual(profile.user.email, "test@gmail.com")
        self.assertEqual(profile.user.first_name, "Test_first")
        self.assertEqual(profile.user.last_name, "Test_last")
        self.assertIsNotNone(profile.created_at)
        self.assertIsNotNone(profile.updated_at)
        

class FriendRequestModelTests(TestCase):
    def setUp(self):
        u1 = User.objects.create(username="John", email="johm.doe@mail.com", first_name="John", last_name="Doe")
        u2 = User.objects.create(username="Travis07", email="travis.scott@mail.com", first_name="Travis", last_name="Scott")
        self.profile1 = Profile.objects.create(user=u1)
        self.profile2 = Profile.objects.create(user=u2)
        
    def test_cannot_send_request_to_self(self):
        fr = FriendRequest(from_profile=self.profile1, to_profile=self.profile1)
        
        with self.assertRaises(ValidationError):
            fr.clean()
        
    def test_friend_request_creation(self):
        fr = FriendRequest.objects.create(from_profile=self.profile1, to_profile=self.profile2)
        
        self.assertEqual(fr.status, FriendRequest.Status.PENDING)
        self.assertEqual(fr.from_profile, self.profile1)
        self.assertEqual(fr.to_profile, self.profile2)
        
        
class FriendshipModelTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="alice", email="alice@example.com", password="pass123")
        self.user2 = User.objects.create_user(username="bob", email="bob@example.com", password="pass123")
        self.profile1 = Profile.objects.create(user=self.user1)
        self.profile2 = Profile.objects.create(user=self.user2)
        
    def test_cannot_friend_self(self):
        friendship = Friendship(profile1=self.profile1, profile2=self.profile1)
        
        with self.assertRaises(ValidationError):
            friendship.clean()
            
    def test_friendship_creation_ordering(self):
        friendship = Friendship.objects.create(profile1=self.profile2, profile2=self.profile1)

        self.assertTrue(friendship.profile1.id < friendship.profile2.id)