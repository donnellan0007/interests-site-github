from django.shortcuts import render,get_object_or_404,redirect
from django.utils import timezone
from mainapp.forms import UserProfileInfoForms,PostForm,CommentForm
from django.contrib.auth import authenticate,login,logout
from django.http import HttpResponseRedirect,HttpResponse
from django.urls import reverse,reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin,PermissionRequiredMixin,UserPassesTestMixin
from django.db import IntegrityError
from django.views.generic import TemplateView,ListView,DetailView,CreateView,UpdateView,DeleteView
from django.contrib.auth.decorators import login_required
from mainapp.models import Post,Comment,GroupMember,Group,Friend,UserProfileInfo,Preference,Reply,SendMessageToAdmin
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
from mainapp.forms import UserCreationForm,UserProfileInfoForms,UserUpdateForm,ProfileUpdateForm,ReplyForm,AdminMessageForm
import random
from django.core.paginator import Paginator
from django.conf.urls import (
handler400, handler403, handler404, handler500
)
# Create your views here.
def index(request):
    users = User.objects.exclude(id=request.user.id)
    return render(request,'mainapp/index.html')
    
def random(request):
    import random
    random_number = random.randint(100,1000)
    return render(request, 'mainapp/random.html', {'random_number': random_number})

@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))

def register(request):
    if request.method == 'POST':
        form = UserProfileInfoForms(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Your account has been created! You are now able to log in')
            return redirect('mainapp:user_login')
    else:
        form = UserProfileInfoForms()
    return render(request, 'mainapp/registration.html', {'form': form})


@login_required(login_url='/mainapp/user_login/')
def profile_page(request):
    return render(request,'mainapp/profile.html')


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
#                 print("Username: {} and password {}".format(username,password))
#             else:
#                 messages.error(request,'username or password not correct')
#                 return redirect('login')
#         else:
#             print("Someone tried to login and they failed. They failed! Haha! They're lucky we're not returning this message to them!")
#             print("Username: {} and password {}".format(username,password))
#             messages.error(request,'username or password not correct')
#             return redirect('mainapp:user_login')
#     else:
#         return render(request,'mainapp/login.html',{})
class PostDetailView(HitCountDetailView,DetailView):
    model = Post
    count_hit = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm() # Inject CommentForm
        return context

class PostUpdateView(LoginRequiredMixin,UserPassesTestMixin,UpdateView):
    login_url = '/login/'
    redirect_field_name = 'mainapp/post_details.html'
    form_class = PostForm
    model = Post
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
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
    paginate_by = 10
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
        return Post.objects.filter(author=user).order_by('-published_date')

# def view_profile(request,pk=None):
#         if pk:
#             user_profile = User.objects.get(pk=pk)
#         else:
#             user_profile = request.user
#         context = {'user':user_profile}
#         return render(request,'mainapp/profile.html',context)

def view_profile(request,pk=None):
        if pk:
            user_profile = User.objects.get(pk=pk)
            user_posts = Post.objects.filter(author__id=pk).order_by('-published_date')   #<---add these
            friend, created = Friend.objects.get_or_create(current_user=request.user)
            friends = friend.users.all()
        else:
            user_profile = request.user
            user_posts = Post.objects.filter(author__id = request.user.id).order_by('-published_date')   #<---add these
            friend, created = Friend.objects.get_or_create(current_user=request.user)
            friends = friend.users.all()
        context = {
                   'user':user_profile,
                   'user_posts':user_posts,
                   'friends':friends,
                  }
        return render(request,'mainapp/profile.html',context)

class UserDetailView(ListView):
    model = Post
    template_name = 'mainapp/profile.html'
    context_object_name = 'post'

    def get_queryset(self):
        return user.post_set.all()

# def view_profile(request,pk=None):
#         if pk:
#             user_profile = User.objects.get(pk=pk)
#             user_posts = Post.objects.filter(user__id=pk)   #<---add these
#         else:
#             user_profile = request.user
#             user_posts = Post.objects.filter(user__id = request.user.id)   #<---add these
#         context = {
#                    'user':user_profile,
#                    'user_posts':user_posts
#                   }
#         return render(request,'mainapp/profile.html',context)


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

@login_required(login_url='/mainapp/user_login/')
def add_comment_to_post(request,pk):
    post = get_object_or_404(Post,pk=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user # add this line
            comment.save()
            return redirect('mainapp:post_detail',pk=post.pk)
           
    else:
        form = CommentForm()
    return render(request,'mainapp/comment_form.html',{'form':form})
    
def get_queryset(self):
    return Comment.objects.filter(created_date__lte=timezone.now()).order_by('-created_date')

@login_required(login_url='/mainapp/user_login/')
def add_reply_to_comment(request,pk):
    comment = get_object_or_404(Comment,pk=pk)
    if request.method == 'POST':
        form = ReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.comment = comment
            reply.author = request.user
            reply.save()
            return redirect('mainapp:post_detail',pk=comment.pk)
    else:
        form = ReplyForm()
    return render(request,'mainapp/reply_form.html',{'form':form})
def get_queryset(self):
    return Reply.objects.filter(created_date__lte=timezone.now()).order_by('-created_date')

# @login_required(login_url='/mainapp/user_login/')
# # def add_reply_to_reply(request,pk):
 #     reply


class PostDeleteView(LoginRequiredMixin,DeleteView,UserPassesTestMixin):
    model = Post
    success_url = reverse_lazy('mainapp:post_list')
    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
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
    return redirect('mainapp:post_list')

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
def postpreference(request,postid,userpreference):
    if request.method == 'POST':
        post = get_object_or_404(Post,id=postid)

        obj = ""

        valueobj = ""

        try:
            obj = Preference.objects.get(user=request.user,post=post)

            valueobj = obj.value

            valueobj = int(valueobj)

            userpreference = int(userpreference)

            if valueobj != userpreference:
                obj.delete

                upref = Preference()
                upref.user = request.user

                upref.post = post

                upref.value = userpreference

                if userpreference == 1 and valueobj != 1:
                    post.likes += 1
                    eachpost.dislikes -= 1
                elif userpreference == 2 and valueobj != 2:
                    post.dislikes += 1
                    post.likes -= 1

                upref.save()

                post.save()

                context = {'eachpost':post,'postid':postid}

                return render(request,'mainapp:post_list',context)
            
            elif valueobj == userpreference:
                obj.delete

                if userpreference == 1:
                    post.likes -= 1
                elif userpreference == 2:
                    post.dislikes -= 1

                post.save()

                context = {'eachpost':post,'postid':postid}

                return render(request,'mainapp:post_list',context)

        except Preference.DoesNotExist:
            upref = Preference()

            upref.user = request.user

            upref.post = post

            upref.value = userpreference

            userpreference = int(userpreference)

            if userpreference == 1:
                post.likes += 1
            elif userpreference == 2:
                post.dislikes += 1
            
            upref.save()

            post.save()

            context = {'eachpost':post,'postid':postid}

            return render(request,'mainapp:post_list',context)
    else:
        post = get_object_or_404(Post,id=postid)
        context = {'eachpost':post,'postid':postid}

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
