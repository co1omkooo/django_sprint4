from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from blog.constants import POSTS_PAGE
from blog.models import Category, Comment, Post
from .forms import PostForm, ProfileEditForm, CommentForm
from .utils import filter_posts

User = get_user_model()


class IndexListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = POSTS_PAGE

    def get_queryset(self):
        return filter_posts()


class CategoryPostsListView(ListView):
    model = Post
    template_name = 'blog/category.html'
    paginate_by = POSTS_PAGE

    def get_queryset(self):
        return filter_posts().filter(
            category__slug=self.kwargs['category_slug'],
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(
            Category,
            is_published=True,
            slug=self.kwargs['category_slug'])
        return context


class ProfileListView(ListView):
    model = Post
    template_name = 'blog/profile.html'
    paginate_by = POSTS_PAGE

    def get_queryset(self):
        return (
            self.model.objects.select_related('author')
            .filter(author__username=self.kwargs['username'])
            .annotate(comment_count=Count("comment"))
            .order_by("-pub_date"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(
            User,
            username=self.kwargs['username'])
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'blog/user.html'
    form_class = ProfileEditForm

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse("blog:profile", args=[self.request.user])


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = 'blog/create.html'
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("blog:profile", args=[self.request.user])


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    user = None

    def get_object(self):
        post = get_object_or_404(
            Post,
            pk=self.kwargs['post_id']
        )
        if post.author == self.user:
            return post
        return get_object_or_404(
            self.model.objects.select_related(
                'category',
                'location',
                'author'
            ).filter(
                is_published=True,
                category__is_published=True,
                pub_date__lte=timezone.now()
            ), pk=self.kwargs['post_id'])

    def dispatch(self, request, *args, **kwargs):
        self.user = request.user
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comment.select_related('author')
        return context


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return redirect('blog:post_detail', post_id=self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = PostForm(instance=self.object)
        return context

    def get_success_url(self):
        return reverse("blog:profile", kwargs={"username": self.request.user})


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'
    form_class = CommentForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(
            filter_posts(),
            pk=self.kwargs['post_id']
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "blog:post_detail",
            kwargs={'post_id': self.kwargs['post_id']}
        )


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    pk_url_kwarg = 'post_id'
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return redirect('blog:post_detail', post_id=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.kwargs['post_id']})


class CommentMixin(LoginRequiredMixin):
    model = Comment
    template_name = "blog/comment.html"
    pk_url_kwarg = "comment_id"

    def dispatch(self, request, *args, **kwargs):
        comment = get_object_or_404(
            Comment,
            pk=kwargs['comment_id'],
        )
        if comment.author != request.user:
            return redirect('blog:post_detail', post_id=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse("blog:post_detail",
                       kwargs={'post_id': self.kwargs['post_id']})


class CommentUpdateView(CommentMixin, UpdateView):
    form_class = CommentForm


class CommentDeleteView(CommentMixin, DeleteView):
    ...
