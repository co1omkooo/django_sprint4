from django.db.models import Count
from django.utils import timezone

from .models import Post


def filter_posts(
        posts=Post.objects,
        do_related=True,
        do_annotate=True,
        do_filter=True,
):
    if do_related:
        posts = posts.select_related(
            'author',
            'location',
            'category',
        )
    if do_annotate:
        posts = posts.annotate(
            comment_count=Count('comments')
        ).order_by(*Post._meta.ordering)
    if do_filter:
        posts = posts.filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True
        )
    return posts
