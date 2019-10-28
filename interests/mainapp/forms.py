from django import forms
from django.contrib.auth.models import User
from .models import UserProfileInfo, Post, Comment, Reply, SendMessageToAdmin
from emoji_picker.widgets import EmojiPickerTextInput, EmojiPickerTextarea
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError



class UserProfileInfoForms(UserCreationForm):
    email = forms.EmailField()

    class Meta():
        model = User
        fields = ['username','first_name','last_name','email']

class PostForm(forms.ModelForm):
    class Meta():
        model = Post
        fields = ['title','text','group','image','file','tags','spoiler','NSFW']
        widgets = {
            'title':forms.TextInput(attrs={'class':'textinputclass'}),
            'text':forms.Textarea(attrs={'class':'textareaclass editable'}),
        }
        def __init__(self, *args, **kwargs):
            super(PostForm, self).__init__(*args, **kwargs)
            self.fields['image'].required = False
            self.fields['file'].required = False
        # def clean_tags(self):
    #     tn = self.cleaned_data.get('tags', [])
    #     if len(tn) > 3:
    #         raise ValidationError('Invalid number of tags')

class AdminMessageForm(forms.ModelForm):
    class Meta():
        model = SendMessageToAdmin
        fields = ['title','text']

        def __init__(self,*args,**kwargs):
            super(AdminMessageForm,self).__str__(*args,**kwargs)

    

    
    
    



class CommentForm(forms.ModelForm):
    class Meta():
        model = Comment
        fields = ['text',]
        widgets = {
            'text':forms.Textarea(attrs={'class':'textareaclass'}),
        }

class ReplyForm(forms.ModelForm):
    class Meta():
        model = Reply
        fields = ['text']
        widgets = {
            'text':forms.Textarea(attrs={'class':'textareaclass'}),
        }

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username','email']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfileInfo
        fields = ['image','description','gender','tags','website']
