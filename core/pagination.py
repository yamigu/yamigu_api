from rest_framework.pagination import PageNumberPagination
import random


class SmallPagesPagination(PageNumberPagination):
    page_size = 5

    def page(self, number):
        page = super(ShuffledPaginator, self).page(number)
        random.shuffle(page.object_list)
        return page
