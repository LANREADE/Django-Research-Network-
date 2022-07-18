from email import message
from importlib.resources import read_binary
from django.shortcuts import render,redirect # redirecting users back to the home page
from django.contrib import messages  # django flash messages
from django.http import HttpResponse
from django.db.models import Q # optional serach
from django.contrib.auth.decorators import login_required # for creating restricted pages where login is required
from django.contrib.auth import authenticate,login ,logout  # general authentication for login and log out
from . models import Room, Topic,Message,User # importing Room and topic from the same app directory
from .forms import RoomForm,UserForm,MyUserCreationForm # importing Room form from forms in the same project directory


#A  function to login a user
def loginPage(request):
    page = 'login'
    if request.method =='POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = User.objects.get(email = email)
        except:
            messages.error(request, 'User does not exist')

        user = authenticate(request, email=email , password= password)

        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            messages.error(request, 'User does not exist ')

    context= {'page':page}
    return render(request, 'base/login_register.html', context)


# function to log out user
def logOutUser(request):
    logout(request)
    return redirect('home')# returns back to the home page if the user logsout

# to register as a user
def registerPage(request):
    form = MyUserCreationForm()
    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username
            user.save()
            login(request,user)
            return redirect('home')
        else:
            messages.error(request, 'An error occured during registration')
    return render(request,'base/login_register.html',{'form':form})

def home(request):
    q = request.GET.get('q') if request.GET.get('q')!= None else '' #
# search the rooms according to the topic name, name and description
    rooms = Room.objects.filter( # a condition to  filter
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )
    topics = Topic.objects.all()[0:4] # getting all the information from the topic part of the database
    room_count = rooms.count() # to get the room count in the page
    room_messages = Message.objects.all()# to get all messages in the message database
    context = {'rooms': rooms, 'topics':topics, 'room_count':room_count, 'room_messages':room_messages}
    return render(request,'base/home.html',context)

def room(request, pk):
    room = Room.objects.get(id= pk) # url routing
    room_messages =room.message_set.all().order_by('-created') # arranges the messages in the room according to how they are created
    participants = room.participants.all() # many to many realtionship  with the room and participants

    if request.method == 'POST': # logic to create method of creating messages in the room
        message = Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get('body')

        )
        room.participants.add(request.user) # adding participants
        return redirect('room', pk= room.id)

    context = {'room':room, 'room_messages': room_messages ,'participants':participants}
    return render(request, 'base/room.html',context)

def profileUser(request,pk):
    user = User.objects.get(id = pk) # dynamic url routing for users
    room_messages = user.message_set.all() # to have all the room messages a user
    topics = Topic.objects.all() # to have all topics discussed in a user profile
    rooms = user.room_set.all() # all rooms  joined by the users
    context = {'user':user, 'rooms':rooms, 'room_messages': room_messages, 'topics': topics}
    return render(request,'base/profile.html' ,context)


@login_required(login_url = 'login') # restriction,  only users that are logged in can create rooms
def createRoom(request):
    form = RoomForm() # fetching all information about room in the database in another variable
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name= topic_name)
        Room.objects.create(
            host= request.user,
            topic=topic,
            name= request.POST.get('name'),
            description = request.POST.get('description')
        )
        return redirect('home') # and redirects it back home
    context ={'form':form, 'topics':topics }
    return render(request,'base/form_room.html',context)


@login_required(login_url = 'login') # restriction, only users that have logged in can update a room
def updateRoom(request, pk):
    room =  Room.objects.get(id=pk) #  url routing
    form = RoomForm(instance = room )
    topics = Topic.objects.all()
    if request.user != room.host: # only users of the account can update a room
        return HttpResponse('You are not allowed here! ')
 # but if the  usr is the room host  , update is allowed
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name= topic_name)
        room.name =request.POST.get('name')
        room.topic = topic
        room.desription  =request.POST.get('description')

        return redirect('home')
    context = {'form':form , 'topics':topics, 'room':room }
    return render(request, 'base/form_room.html', context)



@login_required(login_url = 'login') # restriction , only users that are logged in can delete a room
def deleteRoom(request, pk):
    room  = Room.objects.get(id=pk)
    if request.user != room.host: # only users of the account can delete a room
        return HttpResponse('You are not allowed here')
        # if the user is the room host then the user is allowed to delete a room
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request,'base/delete.html', {'obj':room})


@login_required(login_url = 'login') # restriction , only users that are logged in can delete messages
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)
    if request.user != message.user: # only users of the account can delete a message
        return HttpResponse('You are not allowed here')
    if request.method == 'POST':
        message.delete()
        return redirect('home')
    return render(request,'base/delete.html', {'obj':message})

@login_required(login_url = 'login')
def update_user(request):
    user = request.user
    form = UserForm(instance = user )
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES,instance= user)
        if form.is_valid():
            form.save()
            return redirect('profile', pk = user.id )
    return render(request, 'base/update-user.html', {'form':form})


def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q')!= None else ''
    topics = Topic.objects.filter(name__icontains=q)
    return render(request, 'base/topics.html', {'topics':topics} )

def activitiesPage(request):
    room_messages =Message.objects.all()
    return render(request, 'base/activity.html', {'room_messages':room_messages} )


