from django.shortcuts import render, redirect
from .models import Post,Category,Tag,Comment
from django.views.generic import ListView,DetailView,CreateView,UpdateView,DeleteView #여러포스트 나열 시 ListView 사용 👈🏻 23/12/23 수정(DeleteView 추가)
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin,UserPassesTestMixin #로그인했을때만 정상적으로 페이지 보여주는 라이브러리(LoginRequiredMinin)
from django.core.exceptions import PermissionDenied
from django.utils.text import slugify
from .forms import CommentForm
from django.shortcuts import get_object_or_404
from django.db.models import Q  #쿼리문 사용할때 Q객체 사용





#CBV
class PostUpdate(LoginRequiredMixin, UpdateView):
    model = Post
    fields = ['title','hook_text','content','head_image','file_upload','category','tags']

    template_name = 'blog/post_update_form.html' # CBV로 뷰 생성시 원하는 html파일을 템플릿파일로 설정 가능

    def get_context_data(self, **kwargs): #템플릿으로 추가 인자를 넘기기위해 사용
        context = super(PostUpdate, self).get_context_data()
        if self.object.tags.exists():       #해당 포스트에 태그가 존재할경우
            tags_str_list = list()
            for t in self.object.tags.all():
                tags_str_list.append(t.name)
            context['tags_str_default'] = '; '.join(tags_str_list)
        return context

    def dispatch(self, request, *args, **kwargs): #사용자 요청이 GET인지 POST인지 판단
        if request.user.is_authenticated and request.user == self.get_object().author:
            return super(PostUpdate, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied

    def form_valid(self, form):
        response = super(PostUpdate, self).form_valid(form)
        self.object.tags.clear()

        tags_str = self.request.POST.get('tags_str')
        if tags_str:
            tags_str = tags_str.strip()
            tags_str = tags_str.replace(',', ';')
            tags_list = tags_str.split(';')

            for t in tags_list:
                t = t.strip()
                tag, is_tag_created = Tag.objects.get_or_create(name=t)
                if is_tag_created:
                    tag.slug = slugify(t, allow_unicode=True)
                    tag.save()
                self.object.tags.add(tag)
        return response
#CBV
class PostCreate(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Post
    fields = ['title','hook_text','content','head_image','file_upload','category']

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff #해당 페이지 접근가능한 사용자를 su or staff로 제한

    def form_valid(self, form):             #현재 스텝에서 오버라이드 한 이유는, db저장 전 폼에 없던 author, tag를 추가하기위해서 오버라이드 진행
        current_user = self.request.user    #웹사이트 방문자를 의미
        if current_user.is_authenticated and (current_user.is_staff or current_user.is_superuser): #방문자가 로그인한상태인지 확인
            form.instance.author = current_user
            response = super(PostCreate, self).form_valid(form) #태그와 관련된 작업 전, CreateView의 form_valid() 함수 결과값을 저장

            tags_str = self.request.POST.get('tags_str') #POST로 전달된 정보 중 name='tags_str'인 input값 가져오기
            if tags_str:
                tags_str = tags_str.strip()

                tags_str = tags_str.replace(',',';').replace(' ','')
                tags_list = tags_str.split(';')

                for t in tags_list:
                    t = t.strip()       # 태그의 앞뒤공백 제거
                    if len(t) < 3: continue
                    tag, is_tag_created = Tag.objects.get_or_create(name=t) #이 값을 태그로 갖고있으면 가져오고, 없으면 생성

                    if is_tag_created:  #새 태그 생성시 slug 생성해줘야함(아래)
                        tag.slug = slugify(t, allow_unicode=True) #한글 태그 입력 처리 allow_unicode=True)
                        tag.save()
                    self.object.tags.add(tag) #새로 만든 포스트에 태그 추가
            return response

        else:
            return redirect('/blog/')   #로그인상태가 아니라면 /blog/ 화면으로 돌려보낸다.


#CBV
class PostList(ListView): #밑에 FBV방식의 index()함수를 대체
    model = Post
    #template_name = 'blog/post_list.html'#템플릿네임을 지정하는방법
    ordering = '-pk' #웹 페이지 내 내림차순 정렬
    paginate_by = 5 #장고에서 제공하는 기능으로, 한 페이지에 5개의 포스트만 보여주겠다라는 뜻

    def get_context_data(self, **kwargs): #템플릿으로 추가 인자를 넘기기위해 사용
        context = super(PostList, self).get_context_data()  #부모클래스의 get_context_data 그대로 호출하여 저장
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(category=None).count()
        return context


class PostDetail(DetailView): #밑에 FBV방식의 single_page 함수를 대체
    model = Post

    def get_context_data(self, **kwargs):   #템플릿으로 추가 인자를 넘기기위해 사용
        context = super(PostDetail, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(category=None).count()
        context['comment_form'] = CommentForm
        return context

#FBV 방식
def category_page(request, slug):
    #category = Category.objects.get(slug=slug)

    if slug == 'no_category':
        category = '미분류'
        post_list = Post.objects.filter(category=None)
    else:
        category = Category.objects.get(slug=slug)
        post_list = Post.objects.filter(category=category)

    return render(
        request,
        'blog/post_list.html',          # 템플릿은 post_list를 그대로 사용하겠다.
        {
            #post_list.html을 사용하기위해선, PostList 클래스에서 context 로 정의한 데이터들을 매핑시켜야함.

            'post_list':post_list, #포스트중, 카테고리가 = category 인것만 추출
            'categories':Category.objects.all(), #페이지 오른쪽에 위치한 카테고리 카드 채워줌
            'no_category_post_count': Post.objects.filter(category=None).count(), # 카테고리 카드 맨 아래 미분류 포스트와 그 개수 알려줌
            'category':category, #페이지 타이틀 옆 카테고리 이름을 알려줌
        }
    )

def tag_page(request,slug):
    tag=Tag.objects.get(slug=slug)
    post_list = tag.post_set.all()

    return render(
        request,
        'blog/post_list.html',
        {
            'post_list' : post_list,
            'tag':tag,
            'categories':Category.objects.all(),
            'no_category_post_count': Post.objects.filter(category=None).count(),
        }
    )

def new_comment(request, pk):
    if request.user.is_authenticated:      #비정상적인 시도 있을경우에 로그인하지않은경우 PermissionDenied 발생시킴
        post = get_object_or_404(Post, pk=pk) #Post.objects.get(pk=pk)로 가져올수있으나, 해당 pk가 없는경우 오류발생위하여 get_object_or_404 사용

        if request.method == 'POST':    # 폼작성후 submit버튼 클릭시 POST방식으로 전달한다, 그러나 누군가 127.0.0.1:8000/new_comment로 입력할경우 GET방식으로 요청하게되므로 걍pk=10으로 리다이렉트되도록 함
            comment_form = CommentForm(request.POST) #정상적으로 폼 작성 후 POST로 요청 들어온경우엔 CommentForm의 형태로 가져옴
            if comment_form.is_valid(): #폼이 유효하게 작성됐다면,
                comment = comment_form.save(commit=False) #해당 내용으로 새로운 레코드 만들어 db저장, 이 때 바로저장기능 잠시 미루고 comment_form에 담긴 정보로 Comment인스턴스만 가져옴
                comment.post = post
                comment.author = request.user
                comment.save()
                return redirect(comment.get_absolute_url()) #마지막으로 comment의 url로 리다이렉트함.
        else:
            return redirect(post.get_absolute_url())
    else:
        raise PermissionDenied

#CBV
class CommentUpdate(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs): #사용자 요청이 GET인지 POST인지 판단
        if request.user.is_authenticated and request.user == self.get_object().author: #로그인되어있고, 작성자라면
            return super(CommentUpdate, self).dispatch(request, *args, **kwargs)  #edit버튼 클릭하여 이 페이지로 접근시엔 GET방식이므로 pk=1인 comment의 내용이 폼에 채워진상태로 나타난다.
        else:
            raise PermissionDenied

#FBV
def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)   #Comment 객체에서 pk=pk 인것을 가쟈오겠다.
    post = comment.post #댓글을 받아온경우 post에 저장(댓글 삭제이후 그 댓글이 달려있던 해당 포스트로 리다이렉트 하기때문), 못받아온경우 위에서 404에러
    if request.user.is_authenticated and request.user == comment.author: #로그인되어있는 상태이고, 해당 작성자라면
        comment.delete()    #제거
        return redirect(post.get_absolute_url())
    else:
        raise PermissionDenied

#CBV
class PostSearch(PostList):
    paginate_by = None #검색결과를 한페이지에 다 보여주기위해 다시 None 처리

    def get_queryset(self):
        q=self.kwargs['q'] #PostList의 Post.objects.all()과 동일
        post_list = Post.objects.filter(
            Q(title__contains=q) | Q(tags__name__contains=q) #여러 쿼리를 동시에 적용할떄는 Q사용!!!! , 밑줄2개 __ 는 title.contains의 .과 동일!! 장고 약속
        ).distinct() #중복검색 방지, ex) 제목과 태그가 둘다 파이썬일경우 하나의 포스트를 두번가져오게됨 그래서 중복제거 함수 사용
        return post_list

    def get_context_data(self, **kwargs): #템플릿으로 추가인자 넘기기 위해 오버라이딩
        context = super(PostSearch, self).get_context_data()
        q = self.kwargs['q']
        context['search_info'] = f'Search: {q} ({self.get_queryset().count()})' #Search : 파이썬(2)

        return context

#FBV
def delete_post(request, pk): # 👈🏻 23/12/23 추가
    post=get_object_or_404(Post, pk=pk)
    if request.user.is_authenticated and request.user == post.author:
        post.delete()
        return redirect('/blog/')
    else:
        raise PermissionDenied
    #success_url = reverse_lazy('/blog/')
