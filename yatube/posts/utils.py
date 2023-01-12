from django.core.paginator import Paginator


def paginate_page(posts, request):
    LATEST_POSTS_COUNT = 10
    paginator = Paginator(posts, LATEST_POSTS_COUNT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
