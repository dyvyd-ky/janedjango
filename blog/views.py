from django.utils import timezone
import datetime
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from braces.views import GroupRequiredMixin
from django.contrib.auth.models import User
from .forms import PostForm, CommentForm
from .filters import PostFilter
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from .models import Post, Category, Comment
from django.core.mail import send_mail
from django.db.models import F


def search(request):
    post_list = Post.objects.all()
    post_filter = PostFilter(request.GET, queryset=post_list)
    return render(request, 'blog/search_list.html', {'filter': post_filter})


def add_comment_to_post(request, slug):
    post = get_object_or_404(Post, slug=slug)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()
            return redirect('blog:post-detail', slug=post.slug)
    else:
        form = CommentForm()
    return render(request, 'blog/add_comment_to_post.html', {'form': form})


class PostCategoryListView(ListView):
    model = Post
    form_class = PostForm
    template_name = 'blog/post_by_category.html'  # <app>/<model>_viewtype>.html
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        self.category = get_object_or_404(Category, pk=self.kwargs['pk'])
        return Post.objects.filter(category=self.category).order_by('-publish_date')

    def get_context_data(self, **kwargs):
        context = super(PostCategoryListView, self).get_context_data(**kwargs)
        context['category'] = self.category
        return context


class PostListView(ListView):
    model = Post
    form_class = PostForm
    template_name = 'blog/post_list.html'  # <app>/<model>_viewtype>.html
    context_object_name = 'posts'
    ordering = ['-publish_date']
    paginate_by = 6
    

    """def get_context_data(self, **kwargs):
        startdate = timezone.now() - datetime.timedelta(days=7)
        enddate = timezone.now()
        post=Post.objects.get(id=post_id)
        post.views=post.views+1
        context = super(PostListView, self).get_context_data(**kwargs)
        context.update({
        'popular_posts': Post.objects.filter(publish_date__range=[startdate, enddate]).order_by(Views)[:3],
        })
        return context"""


'''class PostDetailView(DetailView):
    model = Post
    form_classes = {'PostForm': PostForm,
                    'CommentForm': CommentForm}
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'
    related_post = post.tags.similar_objects()

    def get_context_data(self, **kwargs):
        startdate = timezone.now() - datetime.timedelta(days=7)
        enddate = timezone.now()
        context = super(PostDetailView, self).get_context_data(**kwargs)
        context.update({
        'popular_posts': Post.objects.filter(publish_date__range=[startdate, enddate]).order_by('-hit_count_generic__hits')[:3],
        })
        return context'''

def post_detail(request, slug):
    template_name = 'blog/post_detail.html'
    post = get_object_or_404(Post, slug=slug)
    related_post = post.tags.similar_objects()
    comments = post.comments.filter(active=True)
    new_comment = None
    Post.objects.filter(slug=post.slug).update(views=F('views') + 1)

    recent_posts = Post.objects.exclude(slug=slug).order_by('-publish_date')[:3]
    


    return render(request, template_name, {'post': post,                                 
                                           'related_post': related_post,
                                           'recent_posts': recent_posts})

class UserPostListView(ListView):
    model = Post
    form_class = PostForm
    template_name = 'blog/user_posts.html'  # <app>/<model>_viewtype>.html
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).order_by('-publish_date')


class PostCreateView(GroupRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    context_object_name = 'posts'
    template_name = 'blog/post_form.html'
    group_required = u"authors"

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False

def contact(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        message = request.POST['message']

        send_mail(
            name,
            message,
            email,
            ['john.ky.mlv@gmail.com'],
            )
        return render(request, 'blog/contact.html', {'name':name})

    else:
        return render(request, 'blog/contact.html', {})
