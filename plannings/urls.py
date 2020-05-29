from django.urls import path

from plannings import views

app_name = 'plannings'
urlpatterns = [
    path('create/', views.create_planning, name='create'),
    path('check_event/', views.check_event, name='check_event'),  # rename???
    path('created/<str:planning_ekey>/', views.planning_created,
         name='created'),
    path('edit/<str:planning_ekey>/', views.edit_planning, name='edit')
]
