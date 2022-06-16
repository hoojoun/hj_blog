from django.urls import path
from . import views

urlpatterns=[
    path('projects/pdf',views.pdf),
    path('projects/',views.about_me),
    path('',views.landing),
    path('music/',views.music),
]