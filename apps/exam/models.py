from __future__ import unicode_literals
import re
from django.db import models
from django.contrib import messages
import bcrypt
import time
from datetime import datetime, timedelta
from django.utils import timezone
Email_Regex = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
Name_Regex = re.compile(r'^[A-Za-z]+$')

# Create your models here.

class UserManager(models.Manager):

    def register(self, postData):
        status = True
        errorlist = []
        if postData['password'] != postData['confirm']:
            errorlist.append('You might want your passwords to match!')
            status = False
        if len(postData['first_name']) < 2:
            errorlist.append('Please fill in your whole name. ')
            status = False
        elif not Name_Regex.match(postData['first_name']):
            errorlist.append('Does your name really have numbers?')
            status = False
        if len(postData['alias']) < 2:
            errorlist.append('Please fill out your last name. ')
            status = False
        elif not Name_Regex.match(postData['alias']):
            errorlist.append('I bet your last name does not contain numbers.')
            status = False
        if len(postData['password']) < 1:
            errorlist.append('You need password!')
            status = False
        elif len(postData['password']) < 8:
            errorlist.append('Password must be more than 8 characters.')
            status = False
        if len(postData['email']) < 1:
            errorlist.append('Plis fill in email.')
            status = False
        elif not Email_Regex.match(postData['email']):
            errorlist.append('Email format not valid.')
            status = False
        if len(postData['confirm']) < 1:
            errorlist.append('Must fill in a password confirmation!')
            status = False
        if len(User.objects.filter(email = postData['email'])) > 0:
            errorlist.append('Email already registered, sorry! Try a new one or try login in!')
            status = False
        if (postData['birthday']) > time.strftime("%Y-%m-%d"):
            errorlist.append('Invalid birthday! You cannot be from the future!')
            status = False
        if status == False:
            return {'errors': errorlist}
        else:
            password = postData['password']
            hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
            User.objects.create(first_name= postData['first_name'], alias= postData['alias'], email = postData['email'], password = hashed)
            return {'register': True}

    def login(self, postData):
        status = True
        errorlist = []
        user = User.objects.filter(email = postData['email'])
        if len(postData['email']) < 1:
            errorlist.append('Must fill in email to sign in.')
            status = False
        if len(postData['password']) < 1:
            errorlist.append('Must fill in password to sign in.')
            status = False
        else:
            if len(user) < 1:
                errorlist.append('Email not registered. Try registering!')
                status = False
        if status == False:
            return {'errors': errorlist}
        else:
            if bcrypt.hashpw(postData['password'].encode(), user[0].password.encode()) == user[0].password:
                return {'login': True}
            else:
                status = False
                errorlist.append('Password does not match email!')
                return {'errors': errorlist}

class PokeManager(models.Manager):
    def poking(self, postData):
        print '******* POKER AND POKE IDs *******:'
        print postData['poker_id']
        print postData['pokee_id']
        poker = User.objects.filter(id=postData['poker_id'])[0]
        pokee = User.objects.filter(id=postData['pokee_id'])[0]
        pokee.poke_history += 1
        pokee.save()
        poke_pair = Poke.objects.filter(poker=poker, pokee=pokee)
        if len(poke_pair) == 0:
            Poke.objects.create(poker= poker, pokee=pokee, count = 1)
        else:
            print poker.alias + " has poked " + pokee.alias + " " + str(poke_pair[0].count) +  " many times."
            poke_pair[0].count += 1
            poke_pair[0].save()

class User(models.Model):
    first_name = models.CharField(max_length=100)
    alias = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    password = models.CharField(max_length=200)
    birthday = models.DateField(auto_now = False, auto_now_add = False, default="9999-11-29")
    poke_history = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    objects = UserManager()

class Poke(models.Model):
    poker = models.ForeignKey('User', null=True, related_name='poker')
    pokee = models.ForeignKey('User', null=True, related_name='pokee')
    count = models.IntegerField(default=0)
    objects = PokeManager()
