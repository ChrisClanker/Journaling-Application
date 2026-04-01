from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='/login/'), name='logout'),
    path('journals/', views.journals, name='journals'),
    path('details/<int:id>/', views.journal_detail, name='journal_detail'),  
    path('reports/<int:id>/', views.report_detail, name='report_detail'),  
    path('journals/create.html', views.journal_create, name='journal_create'),
    path('journals/ask.html', views.journal_question, name='journal_question'),
    path('goals/', views.goals, name='goals'),
    path('goals/create.html', views.goal_create, name='goal_create'),
    path('goals/<int:id>/', views.goal_detail, name='goal_detail'),  
    path('', views.journals, name='journals'),

]
