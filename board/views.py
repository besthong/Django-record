from django.shortcuts import render,redirect
from .models import Article
from django.views.generic import ListView,DetailView,CreateView,UpdateView
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin,UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

#ChatterBot 사용 위함
#from chatterbot import ChatBot  #24/01/25 추가 👈🏻
#from chatterbot.ext.django_chatterbot import settings #24/01/25 추가 👈🏻

#CBV
class BoardList(ListView):
    model = Article
    ordering = '-pk' #내림차순 정렬
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super(BoardList, self).get_context_data()
        return context

class BoardDetail(DetailView):
    model = Article

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data()
        return context

class ArticleCreate(LoginRequiredMixin, CreateView):
    model = Article

    fields=['title','content']

    def form_valid(self, form):
        current_user = self.request.user
        if current_user.is_authenticated: #LoginRequiredMixin 자체가 파라미터에 포함되는것만으로도 유저가 로그인상태인지 확인 가능함(django 제공) 따라서 이 줄은 불필요함
            form.instance.author = current_user
            response = super(ArticleCreate, self).form_valid(form)

            return response

        else:
            return redirect('/board/')

class ArticleUpdate(LoginRequiredMixin,UpdateView):
    model = Article
    fields = ['title','content']

    template_name = 'board/board_update_form.html' #updateview, createview 둘 다 동일한 _form을 사용하여 템플릿을 생성하기때문에
                                                    # 이런식으로 강제로 오버라이딩하도록 지정해줘야 정확한 페이지 안내가 이루어진다.

    def get_context_data(self, **kwargs): #템플릿으로 추가인자 넘기기위해 사용
        context = super(ArticleUpdate, self).get_context_data()
        return context

    def dispatch(self, request, *args, **kwargs): #사용자 요청이 GET,POST 인지 확인
        if request.user == self.get_object().author:
            return super(ArticleUpdate, self).dispatch(request, *args, **kwargs)
        else:
            PermissionDenied

    def form_valid(self,form): #유효한 폼 데이터가 POST 되었을때 호출됨.
        response = super(ArticleUpdate, self).form_valid(form)
        #self.object.content.clear()
        return response


def delete_article(request,pk):
    article = get_object_or_404(Article, pk=pk)
    if request.user == article.author:
        article.delete()
        return redirect('/board/')
    else:
        raise PermissionDenied