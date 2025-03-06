from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('chat/', views.ChatView.as_view(), name='chat'),
    path('history/', views.HistoryView.as_view(), name='history'),
    path('uploads/<str:filename>/', views.UploadView.as_view(), name='upload'),
]