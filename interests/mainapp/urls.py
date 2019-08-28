from django.urls import path,include
from . import views
from .views import SearchResultsView

app_name = 'mainapp'

urlpatterns = [
    path('',views.index,name='index'),
    path('posts/',views.PostListView.as_view(),name='post_list'),
    path('register/',views.register,name='register'),
    path('user_login/',views.user_login,name='user_login'),
    path('profile/',views.ProfileView.as_view(),name='profile'),
    path('post/<int:pk>', views.PostDetailView.as_view(), name='post_detail'),
    path('post_new/', views.CreatePostView.as_view(), name='post_new'),
    path('post/<int:pk>/edit/', views.PostUpdateView.as_view(), name='post_edit'),
    path('drafts/', views.DraftListView.as_view(), name='post_draft_list'),
    path('post/<int:pk>/remove/', views.PostDeleteView.as_view(), name='post_remove'),
    path('post/<int:pk>/publish/', views.post_publish, name='post_publish'),
    path('post/<int:pk>/comment/', views.add_comment_to_post, name='add_comment_to_post'),
    path('comment/<int:pk>/approve/', views.comment_approve, name='comment_approve'),
    path('comment/<int:pk>/remove/', views.comment_remove, name='comment_remove'),
    path('posts_search/',views.SearchResultsView.as_view(),name='search_results'),
    path('avatar/',include('avatar.urls')),
    
    
]