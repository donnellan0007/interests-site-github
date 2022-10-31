from django.urls import path,include
from . import views
from . import views as user_view
from .views import SearchResultsView,UserPostListView,PostUpdateView,PostDeleteView,PostLikeRedirect,PostLikeAPIRedirect,PostSaveRedirect,Home,PostSaveListView,get_premium,MessageInbox,CreateMessageView
from django.conf import settings
from django.conf.urls.static import static
from mainapp.forms import UserCreationForm,UserProfileInfoForms,UserUpdateForm,ProfileUpdateForm,ReplyForm
from django.contrib.auth import views as auth_views
app_name = 'mainapp'


urlpatterns = [
    path('',views.Home.as_view(),name='index'),
    path('user/<str:username>', UserPostListView.as_view(), name='user-posts'),
    
    path('new/<username>/',views.CreateMessageView.as_view(),name='message-form', template_name="mainapp/message_form.html"),
    path('inbox/',views.MessageInbox.as_view(),name='inbox-list'),
    path('profile/<str:username>/',views.view_profile,name='view_profile_with_pk'),
    path('profile/',views.view_profile,name='view_profile'),
    path('posts/',views.PostListView.as_view(),name='post_list'),
    path('post_new/', views.CreatePostView.as_view(), name='post_new'),
    path('register/',user_view.register,name='register'),
    path('user_login/',auth_views.LoginView.as_view(template_name='mainapp/login.html',),name='user_login'),
    path('profile/',views.profile_page,name='profile'),
    path('account/update/',views.profile_update,name='profile_update'),
    path('posts/saved/',views.PostSaveListView.as_view(),name='saved-posts'),
    
    path('<int:pk>/<str:slug>/like', views.PostLikeRedirect.as_view(), name='post_likes'),
    path('<int:pk>/<str:slug>/save', views.PostSaveRedirect.as_view(), name='post_saves'),
    path('<int:pk>/<str:slug>/like', views.PostLikeAPIRedirect.as_view(), name='post_api_likes'),
    
    path('drafts/', views.DraftListView.as_view(), name='post_draft_list'),
    path('<int:pk>/<str:slug>/publish/', views.post_publish, name='post_publish'),
    path('<str:slug>/comment/', views.add_comment_to_post, name='add_comment_to_post'),
    path('comment/<str:slug>/reply',views.add_reply_to_comment,name='add_reply_to_comment'),
    path('comment/<int:pk>/approve/', views.comment_approve, name='comment_approve'),
    path('comment/<int:pk>/remove/', views.comment_remove, name='comment_remove'),
    path('posts_search/',views.SearchResultsView.as_view(),name='search_results'),
    path('users_search/',views.SearchResultsViewUsers.as_view(),name='search_results_user'),
    path('avatar/',include('avatar.urls')),
    path('<str:slug>/update/', PostUpdateView.as_view(), name='post-update'),
    path('<int:pk>/<str:slug>/delete/', PostDeleteView.as_view(), name='post-delete'),
    path('tag/<slug>',views.TagIndexView.as_view(),name='tagged'),
    path('groups/new/',views.CreateGroup.as_view(),name='create_group'),
    path('posts/in/<slug>/',views.SingleGroup.as_view(),name='single'),
    path('groups/all/',views.ListGroups.as_view(),name='groups'),
    path('join/<slug>/',views.JoinGroup.as_view(),name='join'),
    path('leave/<slug>/',views.LeaveGroup.as_view(),name='leave'),
    path('connect/<operation>/<pk>/<str:slug/>',views.change_friends,name='change_friends'),
    
    path('premium/',views.get_premium,name='get_premium'),
    path('random_number/',views.random,name='random_number'),
    path('admin/send/',views.SendAdminMessage.as_view(),name='send_admin_msg'),
    path('<str:slug>/',views.PostDetailView.as_view(),name='post_detail'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
