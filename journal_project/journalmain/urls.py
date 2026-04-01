from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='/login/'), name='logout'),
    path('', views.dashboard, name='dashboard'),
    path('journals/', views.journals, name='journals'),
    path('details/<int:id>/', views.journal_detail, name='journal_detail'),
    path('reports/<int:id>/', views.report_detail, name='report_detail'),
    path('journals/create.html', views.journal_create, name='journal_create'),
    path('journals/ask.html', views.journal_question, name='journal_question'),
    path('details/<int:id>/edit/', views.journal_edit, name='journal_edit'),
    path('details/<int:id>/delete/', views.journal_delete, name='journal_delete'),
    path('details/<int:id>/bookmark/', views.journal_toggle_bookmark, name='journal_toggle_bookmark'),
    path('goals/', views.goals, name='goals'),
    path('goals/create.html', views.goal_create, name='goal_create'),
    path('goals/<int:id>/', views.goal_detail, name='goal_detail'),
    path('goals/<int:id>/edit/', views.goal_edit, name='goal_edit'),
    path('goals/<int:id>/delete/', views.goal_delete, name='goal_delete'),
    path('mood-calendar/', views.mood_calendar, name='mood_calendar'),
    path('tags/', views.tag_list, name='tag_list'),
    path('tags/<int:id>/', views.tag_detail, name='tag_detail'),
]
