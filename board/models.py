from django.db import models
from django.contrib.auth.models import User
from markdownx.models import MarkdownxField
from markdownx.utils import markdown
import os

# Create your models here.


class Article(models.Model):
    title = models.CharField(max_length=30)
    content = MarkdownxField()
    created_at = models.DateTimeField(auto_now_add=True) #처음 레코드 생성시점
    updated_at = models.DateTimeField(auto_now=True) #레코드 마지막 저장 시점

    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'[{self.pk}]{self.title} - {self.author}'
    def get_absolute_url(self):
        return f'/board/{self.pk}/' #admin 화면 내 Article에서 view on site 버튼 생김