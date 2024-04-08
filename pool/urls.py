from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='pool-home'),
    path('home/', views.home, name='pool-home'),
    path('leaderboard/', views.leaderboard, name='pool-leaderboard'),
    path('admin_init/', views.admin_init, name='pool-init'),
    path('odds/', views.odds, name='pool-odds'),
    #path('about/', views.about, name='blog-about'),
]
