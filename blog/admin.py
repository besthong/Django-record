from django.contrib import admin
from markdownx.admin import MarkdownxModelAdmin #관리자 페이지에서도 마크다운x 적용하기
from .models import Post,Category,Tag,Comment

admin.site.register(Post, MarkdownxModelAdmin)
admin.site.register(Comment)

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name', )}

class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

    # def has_view_permission(self,request,obj=None):
    #     if request.user.is_superuser:
    #         return True
    #     else:
    #         return False




admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag, TagAdmin)