from django.db.models import Count
from django.utils import timezone

from .models import Post


def filter_posts(
        queryset=Post.objects,
        pub_date_filter=timezone.now(),
        is_published_filter=True,
        category_is_published_filter=True,
        filter=True
):
    if filter:
        return queryset.filter(
            pub_date__lte=pub_date_filter,
            is_published=is_published_filter,
            category__is_published=category_is_published_filter
        ).annotate(
            comment_count=Count('comments')
        ).select_related(
            'author',
            'location',
            'category'
        ).order_by('-pub_date')
    else:
        return queryset.select_related(
            'author',
            'location',
            'category',
        ).annotate(
            comment_count=Count('comments')
        ).order_by('-pub_date')
