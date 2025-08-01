"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from users.views import  signup,login
from papers.views import upload_paper , get_papers , get_paper_details



urlpatterns = [
    path('admin/', admin.site.urls),
    path('signup',signup),
    path('login',login),
    path('papers',upload_paper),
    path('get_papers',get_papers),
    path('get_papers/<str:paper_id>/', get_paper_details, name='get_paper_by_id'),
]
