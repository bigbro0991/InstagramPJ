from django.db import models
from imagekit.models import ProcessedImageField
from django.urls import reverse
from django.contrib.auth.models import AbstractUser
# Create your models here.



class InstaUser(AbstractUser):
    profile_pic=ProcessedImageField(
        upload_to='static/images/profile',
        format='JPEG',
        options={'quality':100},
        blank=True,
        null=True
    )

    def get_connections(self):
        connections = Userconnection.objects.filter(creator=self)
        return connections
    
    def get_followers(self):
        followers = Userconnection.objects.filter(following = self )
        return followers
    
    def is_followed_by(self,user):
        followers = Userconnection.objects.filter(following = self )
        return follower.filter(creator= user).exists()

    def get_absolute_url(self):
        return reverse('user_detail', args=[str(self.id)])

    def __str__(self):
        return self.username


class Post(models.Model):
    author = models.ForeignKey(
        InstaUser,
        on_delete=models.CASCADE,
        related_name="my_posts"
    )
    title = models.TextField(blank=True, null=True)
    image = ProcessedImageField(
        upload_to='static/images/posts',
        format='JPEG',
        options={'quality':100},
        blank=True,
        null=True
    )

    posted_on = models.DateTimeField(
        auto_now_add=True,
        editable=False,
    )
    
    def __str__(self):
        return self.title

    def get_like_count(self):
        return self.likes.count()

    def get_absolute_url(self):
        return reverse("post_detail",args=[str(self.pk)])

    def get_comment_count(self):
        return self.comments.count()

class Like(models.Model):
    post = models.ForeignKey(
        Post, 
        on_delete=models.CASCADE,
        related_name="likes")
    user = models.ForeignKey(
        InstaUser,
        on_delete=models.CASCADE,
        related_name="likes")
    
    class Meta:##distinct in sql
        unique_together = ("post","user")

    def __str__(self):
        return "like"+str(self.pk)+": "+ self.user.username + ' likes ' + self.post.title



class Comment(models.Model):
    post = models.ForeignKey(
        Post, 
        on_delete=models.CASCADE,
        related_name="comments",
    )

    user = models.ForeignKey(
        InstaUser,
        on_delete=models.CASCADE,
        related_name="all_comments")

    comment = models.CharField(max_length=100)
    posted_on = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return self.comment


class Userconnection(models.Model):
    created = models.DateTimeField(auto_now_add=True , editable=False)
    creator = models.ForeignKey(
        InstaUser,
        on_delete=models.CASCADE,
        related_name="friendship_creator_set")
    following = models.ForeignKey(
        InstaUser,
        on_delete=models.CASCADE,
        related_name="friend_set")
    
    def __str__(self):
        return self.creator.username + "follows" + self.following.username
    