from django.urls import path
from . import views
urlpatterns = [
  path('home',views.home, name='home'),
  path('signin', views.signin,name= 'signin'),
  path('signup',views.signup,name = 'signup'),
  path('signout',views.signout,name = 'signout'),
  path('activate/<str:uidb64>/<str:token>',views.activate,name='activate')
 ]