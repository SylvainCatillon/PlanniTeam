from django.urls import path

from participations import views

app_name = 'participations'
urlpatterns = [
    path('view/<str:planning_ekey>/', views.view_planning, name='view')
]