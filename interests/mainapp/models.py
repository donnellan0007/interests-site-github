from django.db import models
from django.urls import reverse
from django.utils import timezone,timesince
from django.contrib.auth.models import User
from PIL import Image

import tagulous
from emoji_picker.widgets import EmojiPickerTextInput, EmojiPickerTextarea
from taggit.managers import TaggableManager
# Create your models here.



class UserProfileInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50,blank=True,null=True)
    last_name = models.CharField(max_length=50,blank=True,null=True)
    description = models.CharField(max_length=150)
    image = models.ImageField(upload_to='profile_pics',default='default.jpg')
    joined_date = models.DateTimeField(blank=True,null=True,default=timezone.now)
    verified = models.BooleanField( default=False)

    def __str__(self):
        return f'{self.user.username} Profile'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        

    
class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=75)
    text = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)
    image = models.ImageField(upload_to='post_images',blank=True,null=True)
    file = models.FileField(upload_to='post_files',blank=True,null=True)
    published_date = models.DateTimeField(blank=True,null=True,auto_now_add=True)
    comments_disabled = models.BooleanField(default=False)
    NSFW = models.BooleanField(default=False)
    spoiler = models.BooleanField(default=False)

    tags = TaggableManager()
    
    def __str__(self):
        return self.title
    

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


    

    def publish(self):
        self.published_date = timezone.now()
        self.save()
    
    def approve_comments(self):
        return self.comments.filter(approved_comment=True)
    
    def get_absolute_url(self):
        return reverse('mainapp:post_detail',kwargs={'pk':self.pk})

    
    

class Comment(models.Model):
    post = models.ForeignKey('mainapp.Post',related_name='comments',on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)
    approved_comment = models.BooleanField(default=True)

    def approve(self):
        self.approved_comment = True
        self.save()
    
    def get_absolute_url(self):
        return reverse('post_list')

    def __str__(self):
        return self.text