from django.urls import path
from . import views

urlpatterns=[
    path('delete_post/<int:pk>/', views.delete_post), # 👈🏻 23/12/23 추가
    path('search/<str:q>/', views.PostSearch.as_view()),  #<str:q>는 검색어에 해당하는 값을 (str)로 받고 q로 할당한다.
    path('delete_comment/<int:pk>/', views.delete_comment),
    path('update_comment/<int:pk>/', views.CommentUpdate.as_view()),
    path('update_post/<int:pk>/', views.PostUpdate.as_view()),
    path('create_post/', views.PostCreate.as_view()),
    path('tag/<str:slug>/', views.tag_page),
    path('category/<str:slug>/', views.category_page),
    path('', views.PostList.as_view()),
    path('<int:pk>/new_comment/', views.new_comment), #FBV 스타일로
    path('<int:pk>/', views.PostDetail.as_view()),
    #path('<int:pk>/', views.single_post_page), #FBV
    #path('', views.index), #FBV
]