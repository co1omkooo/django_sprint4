from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from blog.constants import PAGINATE_COUNT
from blog.models import Category, Comment, Post, User
from .forms import PostForm, ProfileEditForm, CommentForm
from .utils import filter_posts


class PostMixin():
    model = Post
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return redirect(
                'blog:post_detail',
                self.kwargs[self.pk_url_kwarg]
            )
        return super().dispatch(request, *args, **kwargs)


class IndexListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = PAGINATE_COUNT
    queryset = filter_posts()


class CategoryPostsListView(ListView):
    model = Post
    template_name = 'blog/category.html'
    paginate_by = PAGINATE_COUNT

    def get_category(self):
        return get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )

    def get_queryset(self):
        return filter_posts(self.get_category().posts)

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs, category=self.get_category())


class ProfileListView(ListView):
    model = Post
    template_name = 'blog/profile.html'
    paginate_by = PAGINATE_COUNT

    def get_author(self):
        return get_object_or_404(
            User,
            username=self.kwargs['username']
        )

    def get_queryset(self):
        return filter_posts(
            self.get_author().posts,
            do_filter=(self.get_author() != self.request.user)
        )

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs, profile=self.get_author())


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'blog/user.html'
    form_class = ProfileEditForm

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse('blog:profile', args=[self.request.user.username])


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = 'blog/create.html'
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:profile', args=[self.request.user.username])


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'

    def get_object(self):
        post = get_object_or_404(
            Post,
            pk=self.kwargs['post_id']
        )
        if post.author == self.request.user:
            return post
        return get_object_or_404(
            filter_posts(
                do_annotate=False,
                do_related=False
            ),
            pk=self.kwargs['post_id'],
        )

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
            form=CommentForm(),
            comments=self.object.comments.select_related('author')
        )


class PostDeleteView(PostMixin, LoginRequiredMixin, DeleteView):
    template_name = 'blog/create.html'

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
            form=PostForm(instance=self.object)
        )

    def get_success_url(self):
        return reverse('blog:profile', args=[self.request.user.username])


class PostUpdateView(PostMixin, LoginRequiredMixin, UpdateView):
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail',
                       args=[self.kwargs[self.pk_url_kwarg]])


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    template_name = 'blog/comment.html'
    form_class = CommentForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(
            Post,
            pk=self.kwargs['post_id']
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            args=[self.kwargs['post_id']]
        )


class CommentMixin(LoginRequiredMixin):
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return redirect('blog:post_detail', self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blog:post_detail',
                       args=[self.kwargs['post_id']])


class CommentUpdateView(CommentMixin, UpdateView):
    form_class = CommentForm


class CommentDeleteView(CommentMixin, DeleteView):
    ...
