from django.db import models
from django.urls import reverse
from django.utils import timezone,timesince
from django.contrib.auth.models import User
from PIL import Image
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill
import tagulous
from django.template.defaultfilters import slugify
from taggit.managers import TaggableManager
from django.dispatch import receiver
from django.db.models.signals import post_save
from django_countries.fields import CountryField
import uuid
# Create your models here.



class UserProfileInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,max_length=30)
    description = models.TextField(max_length=150)
    country = CountryField()
    website = models.URLField(max_length=200,blank=True,null=True)
    image = ProcessedImageField(upload_to='profile_pics',
                                           processors=[ResizeToFill(150, 150)],
                                           default='default.jpg',
                                           format='JPEG',
                                           options={'quality': 60})
    joined_date = models.DateTimeField(blank=True,null=True,default=timezone.now)
    verified = models.BooleanField(default=False)
    moderator = models.BooleanField(default=False)
    owner = models.CharField(max_length=100,default="",blank=True,null=True)
    
    tags = TaggableManager()

    def __str__(self):
        return f'{self.user.username} Profile'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
    
    def parse_mentions(self):
        mentions = [slugify(i) for i in self.text.split() if i.startswith("@")]
        return User.objects.filter(username__in=mentions)

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfileInfo.objects.create(user=instance)
    else:
        instance.userprofileinfo.save()


    

class Group(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True,allow_unicode=True)
    description = models.TextField(blank=True,null=True,default='')
    members = models.ManyToManyField(User,through='GroupMember')

    def __str__(self):
        return self.name

    def save(self,*args,**kwargs):
        self.slug = slugify(self.name)
        super().save(*args,**kwargs)
    
    def get_absolute_url(self):
        return reverse('mainapp:single',kwargs={'slug':self.slug})

    class Meta():
        ordering = ['name']

class GroupMember(models.Model):
    group = models.ForeignKey(Group,related_name='memberships',on_delete=models.CASCADE)
    user = models.ForeignKey(User,related_name='user_groups',on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username

    class Meta():
        unique_together = ("group","user") 

    
class Post(models.Model):
    author = models.ForeignKey(User,related_name='posts',on_delete=models.CASCADE)
    title = models.CharField(max_length=75)
    text = models.TextField()
    random_url = models.UUIDField(default=uuid.uuid4)
    group = models.ForeignKey(Group,null=True,blank=True,related_name='posts',on_delete=models.CASCADE)
    created_date = models.DateTimeField(default=timezone.now)
    image = models.ImageField(upload_to='post_images',blank=True,null=True)
    file = models.FileField(upload_to='post_files',blank=True,null=True)
    published_date = models.DateTimeField(blank=True,null=True,auto_now_add=True)
    comments_disabled = models.BooleanField(default=False)
    NSFW = models.BooleanField(default=False)
    spoiler = models.BooleanField(default=False)
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)

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

class Preference(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    post = models.ForeignKey(Post,on_delete=models.CASCADE)
    value = models.IntegerField()
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.str(self.user) + '' + str(self.post) + '' + str(self.value)

    class Meta():
        unique_together = ("user","post","value")

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

class Reply(models.Model):
    comment = models.ForeignKey('mainapp.Comment',related_name='replies',on_delete=models.CASCADE)
    author = models.ForeignKey(User,on_delete=models.CASCADE)
    text = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name_plural = "replies"

    def get_absolute_url(self):
        return reverse('post_list')

    def __str__(self):
        return self.text


class SendMessageToAdmin(models.Model):
    author = models.ForeignKey(User,on_delete=models.CASCADE)
    title = models.CharField(max_length=25)
    text = models.TextField(max_length=100)

    def get_absolute_url(self):
        return reverse('mainapp:post_list')

    def __str__(self):
        return self.text

class Friend(models.Model):
    users = models.ManyToManyField(User)
    current_user = models.ForeignKey(User,related_name='owner',null=True,on_delete=models.CASCADE)

    @classmethod
    def make_friend(cls,current_user,new_friend):
        friend,created = cls.objects.get_or_create(
            current_user = current_user
        )
        friend.users.add(new_friend)

    @classmethod
    def lose_friend(cls,current_user,new_friend):
        friend,created = cls.objects.get_or_create(
            current_user = current_user
        )
        friend.users.remove(new_friend)


