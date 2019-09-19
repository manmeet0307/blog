
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='blog-home'),
    path('filter/',views.filter,name="filter"),
    path('about/', views.about, name='blog-about'),
    path('firstfilter/',views.firstfilter,name='firstfilter')
    
]