from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User, auth
from django.contrib import messages
from .models import Profile, Post, Like, Follow, Comment
from django.contrib.auth.decorators import login_required
from itertools import chain

# Create your views here.
def home(request):
    return render(request, 'home.html')

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email taken')
                return redirect('register')
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username taken')
                return redirect('register')
            else:
                user = User.objects.create_user(username=username, email=email, password=password1)
                user.save()
                user_logged = auth.authenticate(username=username, password=password1)
                auth.login(request, user_logged)
                user_model = User.objects.get(username=username)
                profile = Profile.objects.create(user=user_model, id_user=user_model.id)
                profile.save()
                return redirect('settings')
        else:
            messages.info(request, 'Password does not match')
            return redirect('register')
    else:
        return render(request, 'register.html')
    
def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('home')
        else:
            messages.info(request, 'Credentials invalid')
            return redirect('login')
    else:
        return render(request, 'login.html')
    
@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    return redirect('home')

@login_required(login_url='login')
def settings(request):
    user_settings = Profile.objects.get(user=request.user)
    if request.method == 'POST':
        if request.FILES.get('image') == None:
            image = user_settings.profile_img
            bio = request.POST['bio']
            user_settings.profile_img = image
            user_settings.bio = bio
            user_settings.save()
        if request.FILES.get('image') != None:
            image = request.FILES.get('image')
            bio = request.POST['bio']
            user_settings.profile_img = image
            user_settings.bio = bio
            user_settings.save()
        return redirect('settings')
    return render(request, 'settings.html', {'user_settings':user_settings})

@login_required(login_url='login')
def feed(request):
    user_object = User.objects.get(username=request.user.username)
    user_feed = Profile.objects.get(user=user_object)
    posts = Post.objects.all()
    user_following_list = []
    feed = []

    user_following = Follow.objects.filter(follower=request.user.username)

    for users in user_following:
        user_following_list.append(users.user)

    for usernames in user_following_list:
        feed_lists = Post.objects.filter(user=usernames)
        feed.append(feed_lists)

    feed_list = list(chain(*feed))
    return render(request, 'feed.html', {'user_feed':user_feed, 'posts':posts, 'feed_list':feed_list})

@login_required(login_url='login')
def upload(request):
    if request.method == 'POST':
        user = request.user.username
        image = request.FILES.get('post_image')
        caption = request.POST['caption']

        post = Post.objects.create(user=user, image=image, caption=caption)
        post.save()
        return redirect('feed')
    else:
        return redirect('feed')
    
@login_required(login_url='login')
def like(request):
    username = request.user.username
    post_id = request.GET.get('post_id')
    post = Post.objects.get(id=post_id)
    like_filter = Like.objects.filter(post_id=post_id, username=username).first()
    if like_filter == None:
        like = Like.objects.create(post_id=post_id, username=username)
        like.save()
        post.likes_no = post.likes_no + 1
        post.save()
        return redirect('feed')
    else:
        like_filter.delete()
        post.likes_no = post.likes_no - 1
        post.save()
        return redirect('feed')
    
@login_required
def comment(request):
    if request.method == 'POST':
        username = request.user.username
        post_id = request.POST.get('post_id')
        content = request.POST.get('content')
        post = Post.objects.get(id=post_id)
        comment = Comment.objects.create(post_id=post_id, username=username, content=content)
        comment.save()
        if post.comments is None:
            post.comments = f"{username}   {content}\n"
        else:
            post.comments += f"{username}   {content}\n"
        post.save()
        return redirect('feed')
    else:
        return redirect('feed')

@login_required(login_url='login')
def profile(request, pk):
    user_object = User.objects.get(username=pk)
    user_profile = Profile.objects.get(user=user_object)
    user_posts = Post.objects.filter(user=pk)
    follower = request.user.username
    user = pk
    if Follow.objects.filter(follower=follower, user=user).first():
        follow_button_text = 'Unfollow'
    else:
        follow_button_text = 'Follow'
    user_followers = len(Follow.objects.filter(user=pk))
    user_following = len(Follow.objects.filter(follower=pk))
    
    context = {
        'user_object' : user_object,
        'user_profile' : user_profile,
        'user_posts': user_posts,
        'follow_button_text': follow_button_text,
        'user_followers': user_followers,
        'user_following': user_following,
    }
    return render(request, 'profile.html', context)

@login_required(login_url='login')
def follow(request):
    if request.method == 'POST':
        user = request.POST['user']
        follower = request.POST['follower']
        if Follow.objects.filter(user=user, follower=follower).first():
            follower_delete = Follow.objects.get(follower=follower, user=user)
            follower_delete.delete()
            return redirect('/profile/'+user)
        else:
            follower = Follow.objects.create(follower=follower, user=user)
            follower.save()
            return redirect('/profile/'+user)
    else:
        return redirect('/')
    
@login_required(login_url='login')
def search(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)
    if request.method == 'POST':
        username = request.POST['username']
        username_object = User.objects.filter(username__icontains=username)
        username_profile = []
        username_profile_list = []
        for users in username_object:
            username_profile.append(users.id)

        for ids in username_profile:
            profile_lists = Profile.objects.filter(id_user=ids)
            username_profile_list.append(profile_lists)
        
        username_profile_list = list(chain(*username_profile_list))
    return render(request, 'search.html', {'user_profile':user_profile, 'username_profile_list':username_profile_list})