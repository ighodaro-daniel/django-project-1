
from base64 import urlsafe_b64decode, urlsafe_b64encode
from email.message import EmailMessage
from django.shortcuts import redirect, render
from django.http import HttpResponse
from datetime import datetime
from django.views.generic import TemplateView
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from webserver import settings
from django.core.mail import send_mail,BadHeaderError
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes,force_str
from .token import generate_token
def home(request):
    context ={'today':datetime.today()}

    return render( request,'home\index.html',context)


def signup(request):
    users = None

    if request.method == "POST":
        fname = request.POST['fname']
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']
        pwd2 = request.POST['pwd2']

        if password != pwd2:
            messages.error(request,'password do not match')
            return redirect('signup')
        
        if User.objects.filter(username=username).exists():
            messages.error(request,"username already exists")
            return redirect('signup')
        
        if User.objects.filter(email=email).exists():
            messages.error(request,"email already exists")
            return redirect('signup')


        users = User.objects.create_user(fname,email,username)  
        users.first_name = fname
        users.last_name = username
        users.is_active = False
         

        users.save() 
        
        messages.success(request,"your account has been created succesfully")

        subject = "welcome to my forum"
        message = "hello" + users.first_name + " \n" + "you are welcome to my website"
        from_email = settings.EMAIL_HOST_USER
        to_list = [users.email]
        try:
            send_mail(subject,message,from_email,to_list,fail_silently=False)
        except BadHeaderError as e:
              print('error sending email',{e})    

        # email confirmation
        current_site = get_current_site(request)    
        email_subject = "confirm your email"
        message2 = render_to_string("email_confirm.html",{
            'name':users.first_name,
            'domain': current_site.domain,
            'uid': urlsafe_b64encode(force_bytes(users.pk)),
            'token':generate_token.make_token(users)
        })
        
        email = EmailMessage(email_subject,message2,settings.EMAIL_HOST_USER,[users.email])
        email.fail_silently=True
        email.send()

        return redirect('signin')
        
    return render(request,'home/signup.html')

def signin(request):
    user = None
    if request.method == 'POST' :
        username = request.POST['username']
        password = request.POST['pwd']

        user = authenticate( request,username=username,password=password)
        
        if user is not None:
            login(request,user)
            fname = user.first_name
            return render(request,'home/index.html',{'fname':fname})
        else:
            messages.error( request,'invalid username or password')
            return redirect('home')

    return render(request,'home/signin.html')


def signout(request):
    logout(request)
    messages.success(request,"logout successfully")
    return redirect('home')
    
def activate(request,uidb64,token):
    try:    
           uid = force_str(urlsafe_b64decode(uidb64))
           users = User.objects.get(pk=uid)
    except(TypeError,ValueError,OverflowError,User.DoesNotExist):
           users = None

 
    if users is not None and generate_token.check_token(users,token):
              users.is_active = True
              users.save()
              login(request,users)
              return redirect('home')
    else:
         return render(request,'activation_failed.html')