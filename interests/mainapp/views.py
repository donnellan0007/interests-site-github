from django.shortcuts import render,get_object_or_404,redirect
from django.utils import timezone
from mainapp.forms import UserProfileInfoForms,PostForm,CommentForm
from django.contrib.auth import authenticate,login,logout
from django.http import HttpResponseRedirect,HttpResponse
from django.urls import reverse,reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView,ListView,DetailView,CreateView,UpdateView,DeleteView
from django.contrib.auth.decorators import login_required
from mainapp.models import Post,Comment
from django.db.models import Q
from django.contrib.auth.models import User
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.urls import resolve
from django.contrib import messages
from taggit.managers import TaggableManager
from taggit.managers import TaggedItem
from taggit.models import Tag
from mainapp.forms import UserCreationForm,UserProfileInfoForms,UserUpdateForm,ProfileUpdateForm
from django.conf.urls import (
handler400, handler403, handler404, handler500

)
# Create your views here.
def index(request):
    users = User.objects.exclude(id=request.user.id)
    return render(request,'mainapp/index.html')
    

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


class PostDetailView(DetailView):
    model = Post


class PostUpdateView(LoginRequiredMixin,UpdateView):
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

class PostListView(TagMixin,ListView):
    model = Post
    def get_queryset(self):
        return Post.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')


class TagIndexView(TagMixin,ListView):
    template_name = 'mainapp/post_list.html'
    context_object_name = 'posts'
    model = Post
    def get_queryset(self):
        return Posts.objects.filter(tags__slug=self.kwargs.get('slug'))


class UserPostListView(ListView):
    model = Post
    template_name = 'mainapp/user_posts.html'
    context_object_name = 'posts'

    def get_queryset(self):
        user = get_object_or_404(User,username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).order_by('-published_date')

class TagIndexView(TagMixin,ListView):
    model = Post
    def get_queryset(self):
        return Post.objects.filter(tags__slug=self.kwargs.get('slug'))

class SearchResultsView(ListView):
    model = Post
    template_name = 'mainapp/search_results.html'
    
    def get_queryset(self): # new
        query = self.request.GET.get('q')
        return Post.objects.filter(Q(title__icontains=query) | Q(text__icontains=query))
        


class CreatePostView(LoginRequiredMixin,CreateView):
    login_url = '/login/'
    redirect_field_name = 'mainapp/post_details.html'
    form_class = PostForm
    model = Post
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

@login_required
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
            # remove `def form_valid`
    else:
        form = CommentForm()
    return render(request,'mainapp/comment_form.html',{'form':form})

class PostDeleteView(LoginRequiredMixin,DeleteView):
    model = Post
    success_url = reverse_lazy('mainapp:post_list')

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
