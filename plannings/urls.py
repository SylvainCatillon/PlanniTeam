from django.urls import path

from plannings import views

app_name = 'plannings'
urlpatterns = [
    path('create/', views.create_planning, name='create'),
    path('created/<str:planning_ekey>/', views.planning_created, name='created'),
    path('display/<str:planning_ekey>/', views.display_planning, name='display'),
]