from django.urls import path
from  . import views

urlpatterns = [
              path('logout/', views.logOutUser, name ="logout"),
              path('register/',views.registerPage , name= "register"),
              path('login/', views.loginPage, name="login"),
              path('', views.home, name='home'),
              path('room/<str:pk>/', views.room,  name='room'),
              path('profile/<str:pk>/',views.profileUser, name ='profile'),
              path('create-room/',views.createRoom,  name="create-room"),
              path('update-room/<str:pk>/',views.updateRoom,  name ='update-room'),
              path('delete-room/<str:pk>/',views.deleteRoom,  name ='delete-room'),
              path('delete-message/<str:pk>/',views.deleteMessage, name='delete-message' ),
              path('update-user/', views.update_user, name='update-user'),
              path('topics/',views.topicsPage, name='topics'),
              path('activities/',views.activitiesPage, name= 'activities')
]

