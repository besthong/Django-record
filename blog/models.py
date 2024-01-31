from django.db import models
from django.contrib.auth.models import User
from markdownx.models import MarkdownxField
from markdownx.utils import markdown, markdownify
import os
import re

from allauth.socialaccount.models import SocialApp


class Tag(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/blog/tag/{self.slug}/'

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True) #SlugField는 사람이 읽을 수 있는 텍스트로 고유 URL을 만들 때 주로 사용

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/blog/category/{self.slug}/'

    class Meta:
        verbose_name_plural = 'Categories'


class Post(models.Model):
    title = models.CharField(max_length=30)
    hook_text = models.CharField(max_length=100, blank=True)
    content = MarkdownxField()

    head_image = models.ImageField(upload_to='blog/images/%Y/%m/%d/', blank=True)
    file_upload = models.FileField(upload_to='blog/files/%Y/%m/%d/', blank=True)

    created_at = models.DateTimeField(auto_now_add=True) #auto_now_add -> 처음 레코드 생성시점
    updated_at = models.DateTimeField(auto_now=True) #auto_now -> 레코드가 마지막으로 저장된시점

    # author = models.ForeignKey(User, on_delete=models.CASCADE) #author 필드 생성 및, CASCADE 설정(지우면 다지워짐)
    author = models.ForeignKey(User, null=True ,on_delete=models.SET_NULL) # 계정 지워도 null로 포스트는 남음

    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)

    tags = models.ManyToManyField(Tag, blank=True) #ManyToMany(다대다 필드는 기본적으로 null=True인데 이유는 한개 지워지면 다른것도 다 지워질 수 있으므로 기본적으로 true


    def __str__(self):
        return f'[{self.pk}]{self.title} :: {self.author}'

    def get_absolute_url(self):
        return f'/blog/{self.pk}/'      #admin 화면 내 포스트에서 view on site 버튼 생김

    def get_file_name(self):
        return os.path.basename(self.file_upload.name)      # 업로드된파일 이름만!! 가져오기

    def get_file_ext(self):
        return self.get_file_name().split('.')[-1] #확장자 찾기!

    def get_content_markdown(self):         #해당 함수 없이 그냥 작성 후 저장하면 markdownx 모듈 적용 전 줄바꿈없이 그대로 진행됨, 해당 함수는 포스트를 렌더링 할 때
        return markdownify(self.content)       #마크다운 문법으로 작성된 content 필드 값을 HTML로 변환하는 작업이 필요. post_detail.html 내 Content 부분에서 사용!!🤔

    def get_avatar_url(self):
        if self.author.socialaccount_set.exists():
            return self.author.socialaccount_set.first().get_avatar_url()
        else:
            return f'https://doitdjango.com/avatar/id/1792/ba5c68433666ad85/svg/{self.author.email}'


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    create_at = models.DateTimeField(auto_now_add = True)
    modified_at = models.DateTimeField(auto_now=True)

    def get_avatar_url(self):
        if self.author.socialaccount_set.exists():
            return self.author.socialaccount_set.first().get_avatar_url()
        else:
            return f'https://doitdjango.com/avatar/id/1792/ba5c68433666ad85/svg/{self.author.email}'

    def __str__(self):
        return f'{self.author}::{self.content}'

    def get_absolute_url(self):
        return f'{self.post.get_absolute_url()}#comment-{self.pk}'