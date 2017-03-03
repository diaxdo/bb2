from django.shortcuts import render, HttpResponse, redirect
from .models import User, Poke
from django.contrib import messages
from datetime import datetime
from django.utils import timezone

# Create your views here.
def index(request):
    request.session['success'] = False
    return render(request, 'exam/index.html')

def register(request):
    if request.method == "GET":
        messages.error(request, "Nice try. Register first.")
        return redirect('/')
    user = User.objects.register(request.POST)
    if 'errors' in user:
        error = user['errors']
        for one in error:
            messages.error(request, one)
        return redirect('/')
    if user['register'] == True:
        user = User.objects.filter(email = request.POST['email'])
        request.session['userid'] = user[0].id
        request.session['alias'] = user[0].alias
        request.session['success'] = 'registered'
    return redirect('/success')

def success(request):
    if ('success' not in request.session) or (request.session['success'] == False) or ('userid' not in request.session):
        print 'session success:' + str(request.session['success'])
        print 'req.sess userid: ' + str(request.session['userid'])
        messages.error(request, "Register or log in first.")
        return redirect('/')


    user = User.objects.filter(alias=request.session['alias'])[0]
    all_pokes_to_user = Poke.objects.filter(pokee=user).order_by('-count')

    context = {
    'alias': request.session['alias'],
    'times_poked': len(all_pokes_to_user),
    'all_pokes_from_people': all_pokes_to_user,
    'users': User.objects.all().exclude(alias= request.session['alias'])
    }
    return render(request, 'exam/success.html', context)


def login(request):
    if request.method == "GET":
        messages.error(request, "Nice try. Log in first.")
        return redirect('/')
    user = User.objects.login(request.POST)
    if 'errors' in user:
        error = user['errors']
        for one in error:
            messages.error(request, one)
        return redirect('/')
    if user['login'] == True:
        user = User.objects.filter(email = request.POST['email'])
        request.session['userid'] = user[0].id
        request.session['success'] = True
        request.session['alias'] = user[0].alias
        print "this is alias " + user[0].alias
    return redirect('/success')

def delete(request, id):
    if request.method == "GET":
        messages.error(request, "Nice try. Are you a hacker?")
        return redirect('/')
    User.objects.filter(id=id).delete()
    return redirect('/success')

def logout(request):
    if request.method == "GET":
        messages.error(request, "How can you log out without having logged in?")
        return redirect('/')
    request.session['success'] = False
    del request.session['userid']
    return redirect('/')

def poke(request):
    Poke.objects.poking(request.POST)
    request.session['success'] = True
    return redirect('/success')
