
from annoying.decorators import ajax_request
from django.shortcuts import render
from django.views.generic import TemplateView,ListView,DetailView
from django.views.generic.edit import CreateView,UpdateView,DeleteView
from Insta.models import Post,Like,InstaUser,Userconnection,Comment
from django.contrib.auth.mixins import LoginRequiredMixin
from Insta.forms import CustomUserCreationForm
from django.urls import reverse_lazy

# Create your views here.

class HelloWorld(TemplateView):
    template_name = 'test.html'

class PostsListView(ListView):
    model = Post
    template_name = "index.html"

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return

        current_user = self.request.user
        following = set()
        for conn in Userconnection.objects.filter(
                creator=current_user).select_related('following'):
            following.add(conn.following)
        return Post.objects.filter(author__in=following)


class PostsDetailView(DetailView):
    model = Post
    template_name = "post_detail.html"


class PostsCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = "posts_create.html"
    fields = ["title","image"]##autofield 不包含
    login_url = 'login'##LoginRequiredMixin 如果没login 跳转到那个页面

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


    
class PostsUpdateView(UpdateView):
    model = Post
    template_name = "post_update.html"
    fields = ["title","image"]

class PostsDeleteView(LoginRequiredMixin,DeleteView):
    model = Post
    template_name ="post_delete.html"
    success_url =reverse_lazy("posts")
    login_url = 'login'

class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    template_name="signup.html"
    success_url=reverse_lazy("login")


class UserdetailView(LoginRequiredMixin,DetailView):
    model = InstaUser
    template_name = "user_detail.html"
    login_url = 'login'

class ExploreView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'explore.html'
    login_url = 'login'

    def get_queryset(self):
        return Post.objects.all().order_by('-posted_on')[:20]

class EditProfile(LoginRequiredMixin, UpdateView):
    model = InstaUser
    template_name = 'edit_profile.html'
    fields = ['profile_pic', 'username']
    login_url = 'login'

class FollowersView(ListView):
    model = InstaUser
    template_name = 'followers.html'

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return 

        current_user = self.kwargs['pk']
        following = set()
        for conn in Userconnection.objects.filter(following=current_user).select_related('creator'):
            following.add(conn.creator)
        return InstaUser.objects.filter(username__in=following)

class FollowingsView(ListView):
    model = InstaUser
    template_name = 'followings.html'

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return 

        current_user = self.kwargs['pk']
        following = set()
        for conn in Userconnection.objects.filter(creator=current_user).select_related('following'):
            following.add(conn.following)
        return InstaUser.objects.filter(username__in=following)

@ajax_request
def toggleFollow(request):
    current_user = InstaUser.objects.get(pk=request.user.pk)
    follow_user_pk = request.POST.get('follow_user_pk')
    follow_user = InstaUser.objects.get(pk=follow_user_pk)
   
    try:
        if current_user.pk != follow_user.pk:

            if request.POST.get('type') == 'follow':
                connection = Userconnection(creator=current_user,
                                            following=follow_user)
                connection.save()
            elif request.POST.get('type') == 'unfollow':
                Userconnection.objects.filter(creator=current_user,
                                              following=follow_user).delete()
            result = 1
        else:

            result = 0
    except Exception as e:
        result = 0

    return {
        "user1" : current_user.pk,
        "user2" : follow_user.pk,
        'result': result,
        'type': request.POST.get('type'),
        'follow_user_pk': follow_user_pk
    }


@ajax_request
def addLike(request):
    post_pk = request.POST.get('post_pk')
    post = Post.objects.get(pk=post_pk)
    try:
        like = Like(post=post, user=request.user)
        like.save()
        result = 1
    except Exception as e:
        like = Like.objects.get(post=post, user=request.user)
        like.delete()
        result = 0

    return {'result': result, 'post_pk': post_pk}

@ajax_request
def addComment(request):
    comment_text = request.POST.get('comment_text')
    post_pk = request.POST.get('post_pk')
    post = Post.objects.get(pk=post_pk)
    commenter_info = {}

    try:
        comment = Comment(comment=comment_text, user=request.user, post=post)
        comment.save()

        username = request.user.username

        commenter_info = {'username': username, 'comment_text': comment_text}

        result = 1
    except Exception as e:
        print(e)
        result = 0

    return {
        'result': result,
        'post_pk': post_pk,
        'commenter_info': commenter_info
    }