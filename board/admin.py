from django.contrib import admin

from markdownx.admin import MarkdownxModelAdmin
from .models import Article

admin.site.register(Article, MarkdownxModelAdmin)

