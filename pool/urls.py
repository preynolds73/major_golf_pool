from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home, name='pool-home'),
    path('leaderboard/', views.leaderboard, name='pool-leaderboard'),
    path('admin_init/', views.admin_init, name='pool-init'),
    #path('about/', views.about, name='blog-about'),
]
