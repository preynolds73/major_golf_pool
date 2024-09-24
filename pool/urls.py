from django.urls import path
#from .views import TeamListView
from . import views

urlpatterns = [
    # path('', TeamListView.as_view(), name='pool-home'),
    path('', views.index, name='pool-index'),
    path('home/', views.home, name='pool-home'),
    path('leaderboard/', views.leaderboard, name='pool-leaderboard'),
    path('admin_init/', views.admin_init, name='pool-init'),
    path('odds/', views.odds, name='pool-odds'),
    #path('about/', views.about, name='blog-about'),
]
