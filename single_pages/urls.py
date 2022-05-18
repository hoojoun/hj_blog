from django.urls import path
from . import views

urlpatterns=[
    path('projects/',views.about_me),
    path('',views.about_me),
]