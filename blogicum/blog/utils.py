from django.db.models import Count
from django.utils import timezone

from .models import Post


def filter_posts(
        posts_object=Post.objects,
        do_related=True,
        do_annotate=True,
        do_filter=True,
):
    if do_related:
        posts_object = posts_object.select_related(
            'author',
            'location',
            'category',
        )
    if do_annotate:
        posts_object = posts_object.annotate(
            comment_count=Count('comments')
        ).order_by(*Post._meta.ordering)
    if do_filter:
        posts_object = posts_object.filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True
        )
    return posts_object
