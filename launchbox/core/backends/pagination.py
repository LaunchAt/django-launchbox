from django.utils.translation import gettext_lazy as _
from rest_framework.pagination import CursorPagination as BaseCursorPagination
from rest_framework.settings import api_settings


class CursorPagination(BaseCursorPagination):
    cursor_query_param = 'cursor'
    cursor_query_description = _('The pagination cursor value.')
    page_size = api_settings.PAGE_SIZE or 10
    invalid_cursor_message = 'invalid_cursor'
    ordering = None
    page_size_query_param = 'page_size'
    page_size_query_description = _('Number of results to return per page.')
    max_page_size = 100
    offset_cutoff = None
