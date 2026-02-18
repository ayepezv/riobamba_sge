from django import template
from django.contrib.admin.views.main import PAGE_VAR

register = template.Library()

@register.simple_tag
def admin_page_url(cl, page_num):
    """
    Generates a URL for a specific page number in the admin changelist,
    preserving existing filters.
    page_num is 0-indexed (p=0 is page 1).
    """
    return cl.get_query_string({PAGE_VAR: page_num})
