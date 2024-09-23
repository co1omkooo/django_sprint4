from django.db.models import Count
from django.utils import timezone

from .models import Post


def filter_posts(
        set_post=Post.objects,
        is_published_filter=True,
        filter=True,
        ordering=Post._meta.original_attrs['ordering']
):
    queryset = set_post.select_related(
        'author',
        'location',
        'category',
    ).annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')

    queryset_filter = queryset.filter(
        pub_date__lte=timezone.now(),
        is_published=is_published_filter,
        category__is_published=True
    )
    if filter:
        return queryset_filter
    return queryset
