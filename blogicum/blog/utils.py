from django.db.models import Count
from django.utils import timezone

from .models import Post


def filter_posts():
    return Post.objects.select_related(
        'author',
        'location',
        'category',
    ).filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True,
    ).annotate(
        comment_count=Count('comment')
    ).order_by('-pub_date')
