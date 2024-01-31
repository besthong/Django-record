from django.urls import path
from . import views

urlpatterns=[
    path('', views.BoardList.as_view()),
    path('<int:pk>/', views.BoardDetail.as_view()),
    path('create_article/', views.ArticleCreate.as_view()),
    path('update_article/<int:pk>/', views.ArticleUpdate.as_view()),
    path('delete_article/<int:pk>/', views.delete_article),

    #path('chat/', views.chat, name='chat'), #24/01/25 추가 👈🏻
    #path('<int:pk>/',views.BoardDetail.as_view()),
]