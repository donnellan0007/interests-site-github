from django.db import models
from django.urls import reverse
from django.utils import timezone,timesince
from django.contrib.auth.models import User
from PIL import Image
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill
import tagulous
from django.utils.text import slugify
from taggit.managers import TaggableManager
from django.dispatch import receiver
from django.db.models.signals import post_save
from pyuploadcare.dj.models import ImageField
from django_countries.fields import CountryField
from .validators import validate_file_extension
from tinymce.models import HTMLField
import uuid
from notifications.signals import notify
# Create your models here.



class UserProfileInfo(models.Model):
    MALE = 'Male'
    FEMALE = 'Female'

    GENDER = [
        (MALE, 'Male'),
        (FEMALE, 'Female'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE,max_length=30)
    description = models.TextField(max_length=150)
    country = CountryField()
    website = models.URLField(max_length=200,blank=True,null=True)
    banner = ProcessedImageField(upload_to='banner_pics',
                                           processors=[ResizeToFill(1920, 600)],
                                           default='default_banner.jpg',
                                           format='JPEG',
                                           options={'quality': 60})

    image = ProcessedImageField(upload_to='profile_pics',
                                           processors=[ResizeToFill(150, 150)],
                                           default='default.jpg',
                                           format='JPEG',
                                           options={'quality': 60})
    joined_date = models.DateTimeField(blank=True,null=True,default=timezone.now)
    gender = models.CharField(
        max_length=10,
        choices=GENDER,
        default=MALE,
    )
    verified = models.BooleanField(default=False)
    is_private = models.BooleanField(default=False)
    slug = models.SlugField(unique=True,allow_unicode=True)
    colour = models.CharField(max_length=500,default='#4287f5')
    moderator = models.BooleanField(default=False)
    skills = models.PositiveIntegerField(default=0)
    owner = models.CharField(max_length=100,default="",blank=True,null=True)
    premium = models.BooleanField(default=False)
    tags = TaggableManager()

    def __str__(self):
        return f'{self.user.username} Profile'

    def save(self, *args, **kwargs):
        self.slug = slugify(self.user.username)
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


class HomePage(models.Model):
    image = ProcessedImageField(upload_to='home_page',
                                           processors=[ResizeToFill(150, 150)],
                                           blank=True,
                                           null=True,
                                           format='JPEG',
                                           options={'quality': 60})


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
        

class Tag(models.Model):
    name = models.CharField(max_length=150,unique=True)

    def __str__(self):
        return self.name
    

class Post(models.Model):
    author = models.ForeignKey(User,related_name='posts',on_delete=models.CASCADE)
    title = models.CharField(max_length=75)
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,max_length=8)
    # id = models.BigIntegerField(unique=True, primary_key=True)
    text = models.TextField(null=True,blank=True)
    random_url = models.UUIDField(default=uuid.uuid4)
    group = models.ForeignKey(Group,null=True,blank=True,related_name='posts',on_delete=models.CASCADE)
    created_date = models.DateTimeField(default=timezone.now)
    image = models.ImageField(upload_to='post_images',blank=True,null=True)
    # image = ImageField(blank=True, manual_crop="")
    published_date = models.DateTimeField(blank=True,null=True,auto_now_add=True)
    file = models.FileField(upload_to="post_files",blank=True,null=True, validators=[validate_file_extension])
    comments_disabled = models.BooleanField(default=False)
    NSFW = models.BooleanField(default=False)
    spoiler = models.BooleanField(default=False)
    likes = models.ManyToManyField(User,blank=True,related_name='post_likes')
    saves = models.ManyToManyField(User,blank=True,related_name='post_saves')
    tags = TaggableManager()
    tag = models.ManyToManyField(Tag,related_name='tags',blank=True)
    slug = models.SlugField(
        default='',
        editable=False,
        max_length=75,
        unique=True
    )
    
    def __str__(self):
        return self.title
    
    def get_slug(self):
        uuid_value = str(uuid.uuid4())
        unique_slug = slugify(uuid_value[0:12])
        return unique_slug

    def publish(self):
        self.published_date = timezone.now()
        self.save()
    
    def approve_comments(self):
        return self.comments.filter(approved_comment=True)
    
    def get_absolute_url(self):
        kwargs = {
            'slug':self.slug,
        }
        return reverse('mainapp:post_detail',kwargs=kwargs)
    
    def save(self, *args, **kwargs):
        value = self.title
        self.slug = self.get_slug()
        super().save(*args, **kwargs)

class Message(models.Model):
    sender = models.ForeignKey(User,related_name='senders',on_delete=models.CASCADE)
    receiver = models.ForeignKey(User,related_name='receivers',on_delete=models.CASCADE)
    content = models.CharField(max_length=2000)
    date_created = models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        return reverse('index')

    def save(self,*args,**kwargs):
        super(Message,self).save(*args,**kwargs)
        notify.send(self.sender,recipient=self.receiver,verb='has sent you a ',description='message',target=self)
    
    class Meta():
        ordering = ['date_created']
    
    def __str__(self):
        return self.content


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
    slug = models.SlugField()
    parent = models.ForeignKey("self",on_delete=models.CASCADE,null=True,blank=True)
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


