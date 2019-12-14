from django import forms
from django.contrib.auth.models import User
from .models import UserProfileInfo, Post, Comment, Reply, SendMessageToAdmin
from emoji_picker.widgets import EmojiPickerTextInput, EmojiPickerTextarea
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError



class UserProfileInfoForms(UserCreationForm):
    email = forms.EmailField(widget=forms.TextInput(
    attrs={'type': 'email',
           'placeholder':('Email')}))

    class Meta():
        model = User
        fields = ['username','first_name','last_name','email']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Username'}),
            'email': forms.TextInput(attrs={'placeholder': 'Email'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Last Name'}),
            }


    def clean(self):
        cleaned_data = super(UserProfileInfoForms, self).clean()
        name = cleaned_data.get('username')
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')


class PostForm(forms.ModelForm):
    class Meta():
        model = Post
        fields = ['title','text','group','image','file','tags','spoiler','NSFW','tag']
        widgets = {
            'title':forms.TextInput(attrs={'class':'textinputclass text-title','placeholder':'Title'}),
            'text':forms.Textarea(attrs={'class':'textareaclass textinputclass editable','placeholder':'Post Contents'}),
        }
    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.fields['title'].label = ""
        self.fields['text'].label = ""
        self.fields['image'].label = ""
        self.fields['file'].label = ""
        self.fields['tags'].label = "Please select up to 5 interests"
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
            'text':forms.Textarea(attrs={'class':'comment-from','placeholder':''}),
        }
    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.fields['text'].label = ""

class ReplyForm(forms.ModelForm):
    class Meta():
        model = Reply
        fields = ['text']
        widgets = {
            'text':forms.Textarea(attrs={'class':'textareaclass','placeholder':''}),
        }
    def __init__(self, *args, **kwargs):
        super(ReplyForm, self).__init__(*args, **kwargs)
        self.fields['text'].label = ""

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username','email']
    
    def clean(self):
        cleaned_data = super(UserUpdateForm, self).clean()
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfileInfo
        fields = ['image','description','gender','banner','tags','colour','website']
        widgets = {
            'description':forms.Textarea(attrs={'class':'textinputclass text-title','placeholder':'Title'}),
            # 'text':forms.Textarea(attrs={'class':'textareaclass textinputclass editable','placeholder':'Post Contents'}),
        }
    
    def clean(self):
        cleaned_data = super(ProfileUpdateForm, self).clean()
        image = cleaned_data.get('image')
        description = cleaned_data.get('description')
        gender = cleaned_data.get('gender')
        tags = cleaned_data.get('tags')
        colour = cleaned_data.get('colour')
        website = cleaned_data.get('website')
