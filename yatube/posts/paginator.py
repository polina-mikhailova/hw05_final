from django.core.paginator import Paginator

from yatube.settings import LATEST_POSTS_COUNT


def paginate_page(posts, request):
    paginator = Paginator(posts, LATEST_POSTS_COUNT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
