from django.shortcuts import render,get_object_or_404,redirect
from django.utils import timezone
from mainapp.forms import UserForm,UserProfileInfoForms,PostForm,CommentForm
from django.contrib.auth import authenticate,login,logout
from django.http import HttpResponseRedirect,HttpResponse
from django.urls import reverse,reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView,ListView,DetailView,CreateView,UpdateView,DeleteView
from django.contrib.auth.decorators import login_required
from mainapp.models import Post,Comment
from django.db.models import Q
# Create your views here.
def index(request):
    return render(request,'mainapp/index.html')

@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))

@login_required
def profile_page(request):
    return render(request,'mainapp/profile.html',{})

class ProfileView(LoginRequiredMixin,TemplateView):
    template_name = 'mainapp/profile.html'

    def get(self,request,):
        user_id = request.user.id
        return render(request,self.template_name)

def register(request):
    registered = False

    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileInfoForms(data=request.POST)

        if user_form.is_valid and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user

            if 'profile_pic' in request.FILES:
                profile.profile_pic = request.FILES['profile_pic']

            profile.save()

            registered = True
        else:
            print(user_form.errors,profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileInfoForms()
    
    return render(request,'mainapp/registration.html',{'user_form':user_form,'profile_form':profile_form,'registered':registered,})

def user_login(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username,password=password)

        if user:
            if user.is_active:
                login(request,user)
                return HttpResponseRedirect(reverse('index'))
                print("Username: {} and password {}".format(username,password))
            else:
                return HttpResponseRedirect("Your account seems to be inactive. That is a minor problem")
        else:
            print("Someone tried to login and they failed. They failed! Haha! They're lucky we're not returning this message to them!")
            print("Username: {} and password {}".format(username,password))
            return HttpResponse("Invalid login details. Please try again. (pls do we need the traffic)")
    else:
        return render(request,'mainapp/login.html',{})

class PostDetailView(DetailView):
    model = Post

class PostUpdateView(LoginRequiredMixin,UpdateView):
    login_url = '/login/'
    redirect_field_name = 'mainapp/post_detail.html'
    form_class = PostForm
    model = Post

class PostListView(ListView):
    model = Post
    def get_queryset(self):
        return Post.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')

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

class PostDeleteView(LoginRequiredMixin,DeleteView):
    model = Post
    success_url = reverse_lazy('post_list')

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
def add_comment_to_post(request,pk):
    post = get_object_or_404(Post,pk=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()
            return redirect('mainapp:post_detail',pk=post.pk)
    else:
        form = CommentForm()
    return render(request,'mainapp/comment_form.html',{'form':form})

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