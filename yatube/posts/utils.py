from django.core.paginator import Paginator
from yatube.settings import PAGINATOR_AMOUNT


def paginate_page(posts, request,
                  paginator_number=PAGINATOR_AMOUNT):
    paginator = Paginator(posts, paginator_number)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
