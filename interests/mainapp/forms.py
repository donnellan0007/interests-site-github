from django import forms
from django.contrib.auth.models import User
from mainapp.models import UserProfileInfo,Post,Comment

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    
    class Meta():
        model = User
        fields = ('username','email','password')


class UserProfileInfoForms(forms.ModelForm):
    class Meta():
        model = UserProfileInfo
        fields = ('bio','profile_pic')
    
class PostForm(forms.ModelForm):
    class Meta():
        model = Post
        fields = ('author','title','text')
        widgets = {
            'title':forms.TextInput(attrs={'class':'textinputclass'}),
            'text':forms.Textarea(attrs={'class':'textareaclass'}),
        }

class CommentForm(forms.ModelForm):
    class Meta():
        model = Comment
        fields = ('author','text')
        widgets = {
            'author':forms.TextInput(attrs={'class':'textinputclass'}),
            'text':forms.Textarea(attrs={'class':'textareaclass'}),
        }