from django.urls import path
from .views import (
    PostListView,
    PostUpdateView,
    PostDeleteView,
    UserPostListView,
    PostCategoryListView,
    PostCreateView
)

from . import views

app_name='blog'
urlpatterns = [
    path('', PostListView.as_view(), name='blog-home'),
    path('post/category/<int:pk>/', PostCategoryListView.as_view(), name='post_by_category'),
    path('user/<str:username>/', UserPostListView.as_view(), name='user-posts'),
    path('post/<slug:slug>/', views.post_detail, name='post-detail'),
    path('post/<slug:slug>/comment/', views.add_comment_to_post, name='add_comment_to_post'),
    path('new_post/', PostCreateView.as_view(), name='post-create'),
    path('post/<slug:slug>/update/', PostUpdateView.as_view(), name='post-update'),
    path('post/<slug:slug>/delete/', PostDeleteView.as_view(), name='post-delete'),
    path('search/', views.search, name='search'),
    path('contact/', views.contact, name='contact'),

]
