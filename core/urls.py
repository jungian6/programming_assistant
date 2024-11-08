from . import views
from django.urls import path
from django.contrib.auth.views import LogoutView


urlpatterns = [
    path('', views.home, name='home'),
    path('chat/', views.chat_view, name='chat'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('chat/generate-completion/<str:user_prompt>/', views.generate_completion, name='generate-completion'),

]