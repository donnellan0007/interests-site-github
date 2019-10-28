from django.urls import path,include
from . import views
from . import views as user_view
from .views import SearchResultsView,UserPostListView,PostUpdateView,PostDeleteView,postpreference,PostLikeRedirect,PostLikeAPIRedirect
from django.conf import settings
from django.conf.urls.static import static
from mainapp.forms import UserCreationForm,UserProfileInfoForms,UserUpdateForm,ProfileUpdateForm,ReplyForm
from django.contrib.auth import views as auth_views
app_name = 'mainapp'


urlpatterns = [
    path('',views.index,name='index'),
    # path('user/<str:username>', UserPostListView.as_view(), name='user-posts'),
    path('profile/',views.view_profile,name='view_profile'),
    path('profile/<pk>/',views.view_profile,name='view_profile_with_pk'),
    path('posts/',views.PostListView.as_view(),name='post_list'),
    path('register/',user_view.register,name='register'),
    path('user_login/',auth_views.LoginView.as_view(template_name='mainapp/login.html'),name='user_login'),
    path('profile/',views.profile_page,name='profile'),
    path('account/update/',views.profile_update,name='profile_update'),
    # path('user/<str:username>',views.ProfileView.as_view(),name='profile'),
    path('post/<int:pk>', views.PostDetailView.as_view(), name='post_detail'),
    path('post/<int:pk>/like', views.PostLikeRedirect.as_view(), name='post_likes'),
    path('api/post/<int:pk>/like', views.PostLikeAPIRedirect.as_view(), name='post_api_likes'),
    path('post_new/', views.CreatePostView.as_view(), name='post_new'),
    path('drafts/', views.DraftListView.as_view(), name='post_draft_list'),
    path('post/<int:pk>/publish/', views.post_publish, name='post_publish'),
    path('post/<int:pk>/comment/', views.add_comment_to_post, name='add_comment_to_post'),
    path('comment/<int:pk>/reply',views.add_reply_to_comment,name='add_reply_to_comment'),
    path('comment/<int:pk>/approve/', views.comment_approve, name='comment_approve'),
    path('comment/<int:pk>/remove/', views.comment_remove, name='comment_remove'),
    path('posts_search/',views.SearchResultsView.as_view(),name='search_results'),
    path('users_search/',views.SearchResultsViewUsers.as_view(),name='search_results_user'),
    path('avatar/',include('avatar.urls')),
    path('post/<int:pk>/update/', PostUpdateView.as_view(), name='post-update'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post-delete'),
    path('tag/<slug>',views.TagIndexView.as_view(),name='tagged'),
    path('groups/new/',views.CreateGroup.as_view(),name='create_group'),
    path('posts/in/<slug>/',views.SingleGroup.as_view(),name='single'),
    path('groups/all/',views.ListGroups.as_view(),name='groups'),
    path('join/<slug>/',views.JoinGroup.as_view(),name='join'),
    path('leave/<slug>/',views.LeaveGroup.as_view(),name='leave'),
    path('connect/<operation>/<pk>',views.change_friends,name='change_friends'),
    path('random_number/',views.random,name='random_number'),
    path('<postid>/preference/<userpreference>/',views.postpreference,name='postpreference'),
    path('admin/send/',views.SendAdminMessage.as_view(),name='send_admin_msg'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
