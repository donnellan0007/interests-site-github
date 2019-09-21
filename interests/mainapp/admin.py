from django.contrib import admin
from emoji_picker.widgets import EmojiPickerTextInput, EmojiPickerTextarea
from mainapp.models import UserProfileInfo,Post,Comment

# Register your models here.
admin.site.register(UserProfileInfo)
admin.site.register(Post)
admin.site.register(Comment)



admin.site.site_header = 'Interests Admin Panel'
admin.site.site_title = 'Interest Admin Panel'

class UserAdmin(admin.ModelAdmin):
    search_fields = ('username', 'first_name', 'last_name', )