from django import forms
from django.contrib.auth.models import User
from .models import UserProfileInfo, Post, Comment
from emoji_picker.widgets import EmojiPickerTextInput, EmojiPickerTextarea
from django.contrib.auth.forms import UserCreationForm



class UserProfileInfoForms(UserCreationForm):
    email = forms.EmailField()

    class Meta():
        model = User
        fields = ['username','first_name','last_name','email']

class PostForm(forms.ModelForm):
    class Meta():
        model = Post
        fields = ['title','text','image','file','tags','spoiler','NSFW']
        widgets = {
            'title':forms.TextInput(attrs={'class':'textinputclass'}),
            'text':forms.Textarea(attrs={'class':'textareaclass editable'}),
            
        }
    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.fields['image'].required = False

class CommentForm(forms.ModelForm):
    class Meta():
        model = Comment
        fields = ['text',]
        widgets = {
            'text':forms.Textarea(attrs={'class':'textareaclass'}),
        }

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username','first_name','last_name','email']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfileInfo
        fields = ['image']
