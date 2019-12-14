from django.contrib import admin
from emoji_picker.widgets import EmojiPickerTextInput, EmojiPickerTextarea
from mainapp.models import UserProfileInfo,Post,Comment,Group,GroupMember,Friend,Preference,Reply,SendMessageToAdmin,Tag
from django.db import models


# Register your models here.
admin.site.register(UserProfileInfo)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Group)
admin.site.register(GroupMember)
admin.site.register(Friend)
admin.site.register(Preference)
admin.site.register(Reply)
admin.site.register(SendMessageToAdmin)
admin.site.register(Tag)

admin.site.site_header = 'Interests Admin Panel'
admin.site.site_title = 'Interest Admin Panel'

class UserAdmin(admin.ModelAdmin):
    search_fields = ('username', 'first_name', 'last_name', )



