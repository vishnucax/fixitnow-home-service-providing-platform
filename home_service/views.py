from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.views.generic import View,CreateView,DetailView,DeleteView,UpdateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.http import HttpResponse
from django.urls import reverse
from HomeServiceManagement.settings import RAZOR_KEY_ID,RAZOR_KEY_SECRET
from django.conf import settings

from home_service.forms import CustomerServiceSearchForm,ServiceManSearchForm

import random
import string
from .models import *
import razorpay
import datetime

# Create your views here.

from django.shortcuts import render
from django.contrib.auth.models import User
from .models import Service_Man, Service_Category, WebsiteReview, Customer

# def Home(request):
#     error = ""
#     user = None

#     # Check if the user is authenticated before querying
#     if request.user.is_authenticated:
#         try:
#             user = User.objects.get(id=request.user.id)
#             if Customer.objects.filter(user=user).exists():
#                 error = "pat"
#         except User.DoesNotExist:
#             pass

#     # Fetch all service providers and categories
#     service_men = Service_Man.objects.all()
#     categories = Service_Category.objects.all()

#     # Count service providers per category
#     for category in categories:
#         category.total = service_men.filter(service_name=category.category).count()
#         category.save()

#     # Fetch reviews
#     user_review = None
#     last_reviews = WebsiteReview.objects.order_by('-created_at')[:2]  # Default to last two reviews

#     if request.user.is_authenticated:
#         user_review = WebsiteReview.objects.filter(user=request.user).order_by('-created_at').first()
#         last_reviews = WebsiteReview.objects.exclude(user=request.user).order_by('-created_at')[:2]

#     # Prepare the final reviews list
#     reviews = []
#     if user_review:
#         reviews.append(user_review)

#     reviews.extend(last_reviews)
#     reviews = reviews[:3]  # Ensure only 3 reviews are displayed
    

#     context = {
#         'error': error,
#         'ser': categories,
#         'reviews': reviews,
#     }

#     return render(request, 'home.html', context)

def Home(request):
    error = ""
    contact_submitted = False  # Track contact form submission
    user = None

    if request.method == "POST" and "contact_form" in request.POST:
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")
        status = Status.objects.get(status="unread")
        Contact.objects.create(status=status, name=name, email=email, message1=message)
        contact_submitted = True

    if request.user.is_authenticated:
        try:
            user = User.objects.get(id=request.user.id)
            if Customer.objects.filter(user=user).exists():
                error = "pat"
        except User.DoesNotExist:
            pass

    service_men = Service_Man.objects.all()
    categories = Service_Category.objects.all()

    for category in categories:
        category.total = service_men.filter(service_name=category.category).count()
        category.save()

    user_review = None
    last_reviews = WebsiteReview.objects.order_by('-created_at')[:2]

    if request.user.is_authenticated:
        user_review = WebsiteReview.objects.filter(user=request.user).order_by('-created_at').first()
        last_reviews = WebsiteReview.objects.exclude(user=request.user).order_by('-created_at')[:2]

    reviews = []
    if user_review:
        reviews.append(user_review)
    reviews.extend(last_reviews)
    reviews = reviews[:3]

    context = {
        'error': error,
        'ser': categories,
        'reviews': reviews,
        'contact_submitted': contact_submitted,  # pass to template
    }

    return render(request, 'home.html', context)




def contact(request):
    error=False
    if request.method=="POST":
        n = request.POST['name']
        e = request.POST['email']
        m = request.POST['message']
        status = Status.objects.get(status="unread")
        Contact.objects.create(status=status,name=n,email=e,message1=m)
        error=True
    d = {'error':error}
    return render(request,'contact.html',d)

def Admin_Home(request):
    cus = Customer.objects.all()
    ser = Service_Man.objects.all()
    cat = Service_Category.objects.all()
    count1=0
    count2=0
    count3=0
    for i in cus:
        count1+=1
    for i in ser:
        count2+=1
    for i in cat:
        count3+=1
    d = {'customer':count1,'service_man':count2,'service':count3}
    
    return render(request,'admin_home.html',d)

def about(request):
    return render(request,'about.html')

# class LoginUserView(View):
#     template_name = 'login.html'

#     def get(self, request):
#         return render(request, self.template_name, {'error': ''})

#     def post(self, request):
#         error = ""
#         u = request.POST.get('uname')
#         p = request.POST.get('pwd')
#         user = authenticate(username=u, password=p)
#         sign = ""

#         if user:
#             try:
#                 sign = Customer.objects.get(user=user)
#             except Customer.DoesNotExist:
#                 pass

#             if sign:
#                 login(request, user)
#                 return redirect('user_home')  # Replace 'success_redirect_url_pat1' with your desired URL
#             else:
#                 stat = Status.objects.get(status="Accept")
#                 pure = False

#                 try:
#                     pure = Service_Man.objects.get(status=stat, user=user)
#                 except Service_Man.DoesNotExist:
#                     pass

#                 if pure:
#                     login(request, user)
#                     return redirect('user_home')  # Replace 'success_redirect_url_pat2' with your desired URL
#                 else:
#                     login(request, user)
#                     return redirect('login')  # Replace 'notmember_redirect_url' with your desired URL
#         else:
#             error = "not"

#         return render(request, self.template_name, {'error': error})
    
    
from django.contrib import messages
from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .models import Customer, Service_Man, Status  # Import necessary models

class LoginUserView(View):
    template_name = 'login.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        u = request.POST.get('uname')
        p = request.POST.get('pwd')
        user = authenticate(username=u, password=p)

        if user:
            try:
                sign = Customer.objects.get(user=user)
            except Customer.DoesNotExist:
                sign = None

            if sign:
                login(request, user)
                return redirect('user_home')  # Redirect if a Customer

            try:
                stat = Status.objects.get(status="Accept")
                pure = Service_Man.objects.get(status=stat, user=user)
            except Service_Man.DoesNotExist:
                pure = None

            if pure:
                login(request, user)
                return redirect('user_home')  # Redirect if a Service_Man

            login(request, user)
            return redirect('login')  # Default redirect
        else:
            messages.error(request, "no_account")  # Show modal on login failure
            return redirect('login')

        return render(request, self.template_name)

    
class LoginAdminView(View):
    template_name = 'admin_login.html'

    def get(self, request):
        return render(request, self.template_name, {'error': ''})

    def post(self, request):
        error = ""
        u = request.POST.get('uname')
        p = request.POST.get('pwd')
        user = authenticate(username=u, password=p)

        if user and user.is_staff:
            login(request, user)
            error = "pat"
        else:
            error = "not"

        return render(request, self.template_name, {'error': error})


import datetime
from django.shortcuts import render
from django.contrib.auth.models import User
from .models import Customer, Service_Man, Status

def Signup_User(request):
    error = ""
    if request.method == 'POST':
        f = request.POST['fname']
        l = request.POST['lname']
        u = request.POST['uname']
        e = request.POST['email']
        p = request.POST['pwd']
        cp = request.POST['cpwd']  # Confirm Password
        con = request.POST['contact']
        add = request.POST['address']
        type = request.POST['type']
        im = request.FILES['image']

        if p != cp:  # Check if passwords match
            error = "Passwords do not match!"
        else:
            dat = datetime.date.today()
            user = User.objects.create_user(email=e, username=u, password=p, first_name=f, last_name=l)
            
            if type == "customer":
                Customer.objects.create(user=user, contact=con, address=add, image=im)
            else:
                stat = Status.objects.get(status='pending')
                Service_Man.objects.create(doj=dat, image=im, user=user, contact=con, address=add, status=stat)

            error = "create"

    d = {'error': error}
    return render(request, 'signup.html', d)



@method_decorator(login_required, name='dispatch')
class UserHomeView(View):
    template_name = 'service_home.html'

    def get(self, request, *args, **kwargs):
        user = request.user
        error = ""

        if user.is_authenticated:
            try:
                sign = Customer.objects.get(user=user)
                error = "pat"
            except Customer.DoesNotExist:
                pass

        context = {'error': error}
        return render(request, self.template_name, context)
def Service_home(request):
    user= User.objects.get(id=request.user.id)
    error=""
    try:
        sign = Customer.objects.get(user=user)
        error = "pat"
    except:
        sign = Service_Man.objects.get(user=user)
        pass
    terro=""
    if None == sign.service_name:
        terro = "message"
    else:
        if sign.status.status == "pending":
            terro="message1"
    d = {'error':error,'terro':terro}
    return render(request,'service_home.html',d)

def Service_Order(request):
    user= User.objects.get(id=request.user.id)
    error=""
    try:
        sign = Customer.objects.get(user=user)
        error = "pat"
    except:
        sign = Service_Man.objects.get(user=user)
        pass
    terro=""
    if None == sign.service_name:
        terro = "message"
    else:
        if sign.status.status == "pending":
            terro="message1"
    order = Order.objects.filter(service=sign)
    d = {'error':error,'terro':terro,'order':order}
    return render(request,'service_order.html',d)

def Admin_Order(request):
    order = Order.objects.all()
    d = {'order':order}
    return render(request,'admin_order.html',d)

def Customer_Order(request):
    user= User.objects.get(id=request.user.id)
    error=""
    try:
        sign = Customer.objects.get(user=user)
        error = "pat"
    except:
        sign = Service_Man.objects.get(user=user)
        pass
    order = Order.objects.filter(customer=sign)
    d = {'error':error,'order':order}
    return render(request,'customer_order.html',d)

def Confirm_order(request):
    user= User.objects.get(id=request.user.id)
    error=""
    try:
        sign = Customer.objects.get(user=user)
        error = "pat"
    except:
        sign = Service_Man.objects.get(user=user)
        pass
    order = Order.objects.filter(customer=sign)
    d = {'error':error,'order':order}
    return render(request,'customer_order.html',d)


def Customer_Booking(request, pid):
    if not request.user.is_authenticated:
        return redirect('login')
    
    user = User.objects.get(id=request.user.id)
    error = ""
    
    try:
        sign = Customer.objects.get(user=user)
        error = "pat"
    except:
        sign = Service_Man.objects.get(user=user)
    
    terror = False
    ser1 = Service_Man.objects.get(id=pid)
    print(ser1.price)
    
    if request.method == "POST":
        n = request.POST['name']
        c = request.POST['contact']
        add = request.POST['add']
        dat = request.POST['date']
        
        # Set static values
        da = 1  # Static day = 1
        ho = 8  # Static hour = 8
        price = ser1.price * ho  # Calculate price based on static hours
        
        print(price)
        st = Status.objects.get(status="pending")
        
        Order.objects.create(
            status=st,
            service=ser1,
            customer=sign,
            book_date=dat,
            book_days=da,
            book_hours=ho,
            price=price
        )
        terror = True
    
    d = {'error': error, 'ser': sign, 'terror': terror}
    return render(request, 'booking.html', d)


def Booking_detail(request,pid):
    user= User.objects.get(id=request.user.id)
    error=""
    try:
        sign = Customer.objects.get(user=user)
        error = "pat"
    except:
        sign = Service_Man.objects.get(user=user)
        pass
    order = Order.objects.get(id=pid)
    d = {'error':error,'order':order}
    return render(request,'booking_detail.html',d)

def All_Service(request):
    user = ""
    error = ""
    try:
        user = User.objects.get(id=request.user.id)
        try:
            sign = Customer.objects.get(user=user)
            error = "pat"
        except:
            pass
    except:
        pass
    ser1 = Service_Man.objects.all()
    ser = Service_Category.objects.all()
    for i in ser:
        count=0
        for j in ser1:
            if i.category==j.service_name:
                count+=1
        i.total = count
        i.save()
    d = {'error': error,'ser':ser}
    return render(request,'services.html',d)

def Explore_Service(request,pid):
    if not request.user.is_authenticated:
        return redirect('login')
    user = ""
    error = ""
    try:
        user = User.objects.get(id=request.user.id)
        try:
            sign = Customer.objects.get(user=user)
            error = "pat"
        except:
            pass
    except:
        pass
    ser = Service_Category.objects.get(id=pid)
    sta = Status.objects.get(status="Accept")
    order = Service_Man.objects.filter(service_name=ser.category,status=sta)
    d = {'error': error,'ser':ser,'order':order}
    return render(request,'explore_services.html',d)

def Logout(request):
    logout(request)
    return redirect('home')

def Edit_Profile(request):
    user = User.objects.get(id=request.user.id)
    error = ""
    try:
        sign = Customer.objects.get(user=user)
        error = "pat"
    except:
        sign = Service_Man.objects.get(user=user)
    terror = False
    ser = Service_Category.objects.all()
    if request.method == 'POST':
        f = request.POST['fname']
        l = request.POST['lname']
        u = request.POST['uname']
        try:
            i = request.FILES['image']
            sign.image=i
            sign.save()
        except:
            pass
        ad = request.POST['address']
        e = request.POST['email']
        con = request.POST['contact']
        sign.address = ad
        sign.contact=con
        user.first_name = f
        user.last_name = l
        user.email = e
        user.save()
        sign.save()
        terror = True
    d = {'terror':terror,'error':error,'pro':sign,'ser':ser}
    return render(request, 'edit_profile.html',d)


# def Edit_Service_Profile(request):
#     user = User.objects.get(id=request.user.id)
#     error = ""
#     try:
#         sign = Customer.objects.get(user=user)
#         error = "pat"
#     except:
#         sign = Service_Man.objects.get(user=user)
#     terror = False
#     ser = Service_Category.objects.all()
#     car = ID_Card.objects.all()
#     city = City.objects.all()
#     if request.method == 'POST':
#         f = request.POST['fname']
#         l = request.POST['lname']
#         u = request.POST['uname']
#         try:
#             i = request.FILES['image']
#             sign.image=i
#             sign.save()
#         except:
#             pass
#         try:
#             i1 = request.FILES['image1']
#             sign.id_card=i1
#             sign.save()
#         except:
#             pass
#         ad = request.POST['address']
#         e = request.POST['email']
#         con = request.POST['contact']
#         se = request.POST['service']
#         card = request.POST['card']
#         cit = request.POST['city']
#         ex = request.POST['exp']
#         dob = request.POST['dob']
#         if dob:
#             sign.dob=dob
#             sign.save()
#         ci=City.objects.get(city=cit)
#         sign.address = ad
#         sign.contact=con
#         sign.city=ci
#         user.first_name = f
#         user.last_name = l
#         user.email = e
#         sign.id_type = card
#         sign.experience = ex
#         sign.service_name = se
#         user.save()
#         sign.save()
#         terror = True
#     d = {'city':city,'terror':terror,'error':error,'pro':sign,'car':car,'ser':ser}
#     return render(request, 'edit_service_profile.html',d)

from datetime import date
from django.contrib import messages
from django.shortcuts import render

def Edit_Service_Profile(request):
    user = User.objects.get(id=request.user.id)
    error = ""
    try:
        sign = Customer.objects.get(user=user)
        error = "pat"
    except:
        sign = Service_Man.objects.get(user=user)

    ser = Service_Category.objects.all()
    car = ID_Card.objects.all()
    city = City.objects.all()

    if request.method == 'POST':
        f = request.POST['fname']
        l = request.POST['lname']
        u = request.POST['uname']
        
        try:
            i = request.FILES['image']
            sign.image = i
            sign.save()
        except:
            pass
        
        try:
            i1 = request.FILES['image1']
            sign.id_card = i1
            sign.save()
        except:
            pass
        
        ad = request.POST['address']
        e = request.POST['email']
        con = request.POST['contact']
        se = request.POST['service']
        card = request.POST['card']
        cit = request.POST['city']
        ex = request.POST['exp']
        dob = request.POST['dob']

        # Validate Date of Birth
        if dob:
            dob_date = date.fromisoformat(dob)  # Convert string to date
            today = date.today()
            age = today.year - dob_date.year - ((today.month, today.day) < (dob_date.month, dob_date.day))

            if age < 18:  # If under 18, show error and stay on page
                messages.error(request, "You must be at least 18 years old.")
                return render(request, 'edit_service_profile.html', {
                    'city': city, 'error': error, 'pro': sign, 'car': car, 'ser': ser
                })

            sign.dob = dob_date  # Only update DOB if valid

        ci = City.objects.get(city=cit)
        sign.address = ad
        sign.contact = con
        sign.city = ci
        user.first_name = f
        user.last_name = l
        user.email = e
        sign.id_type = card
        sign.experience = ex
        sign.service_name = se
        user.save()
        sign.save()
        
        messages.success(request, "Update Successfully")
        return redirect('service_profile')  # Redirect only for valid age
    
    d = {'city': city, 'error': error, 'pro': sign, 'car': car, 'ser': ser}
    return render(request, 'edit_service_profile.html', d)






def Edit_Admin_Profile(request):
    error = False
    user = User.objects.get(id=request.user.id)
    pro = Customer.objects.get(user=user)
    if request.method == 'POST':
        f = request.POST['fname']
        l = request.POST['lname']
        u = request.POST['uname']
        try:
            i = request.FILES['image']
            pro.image=i
            pro.save()
        except:
            pass
        ad = request.POST['address']
        e = request.POST['email']
        con = request.POST['contact']
        pro.address = ad
        pro.contact=con
        user.first_name = f
        user.last_name = l
        user.email = e
        user.save()
        pro.save()
        error = True
    d = {'error':error,'pro':pro}
    return render(request, 'edit_admin_profile.html',d)

def profile(request):
    user = User.objects.get(id=request.user.id)
    error = ""
    try:
        sign = Customer.objects.get(user=user)
        error = "pat"
    except:
        sign = Service_Man.objects.get(user=user)
    terror = False
    d = {'pro':sign,'error':error}
    return render(request,'profile.html',d)

def service_profile(request):
    user = User.objects.get(id=request.user.id)
    error = ""
    try:
        sign = Customer.objects.get(user=user)
        error = "pat"
    except:
        sign = Service_Man.objects.get(user=user)
    terror = False
    d = {'pro':sign,'error':error}
    return render(request,'service_profile.html',d)

def admin_profile(request):
    
    user = User.objects.get(id=request.user.id)
    pro = Customer.objects.get(user=user)
    d = {'pro':pro}
    return render(request,'admin_profile.html',d)



def Admin_Change_Password(request):
    terror = ""
    if request.method=="POST":
        n = request.POST['pwd1']
        c = request.POST['pwd2']
        o = request.POST['pwd3']
        if c == n:
            u = User.objects.get(username__exact=request.user.username)
            u.set_password(n)
            u.save()
            terror = "yes"
        else:
            terror = "not"
    d = {'terror':terror}
    return render(request,'admin_change_password.html',d)

def New_Service_man(request):
    status = Status.objects.get(status="pending")
    ser = Service_Man.objects.filter(status=status)
    d = {'ser':ser}
    return render(request,'new_service_man.html',d)

def All_Service_man(request):

    ser = Service_Man.objects.all()
    d = {'ser':ser}
    return render(request,'all_service_man.html',d)

def All_Customer(request):

    ser = Customer.objects.all()
    d = {'ser':ser}
    return render(request,'all_customer.html',d)



def Add_Service(request):

    error=False
    if request.method == "POST":
        n = request.POST['cat']
        i = request.FILES['image']
        de = request.POST['desc']
        Service_Category.objects.create(category=n,image=i,desc=de)
        error=True
    d = {'error':error}
    return render(request,'add_service.html',d)



def Edit_Service(request,pid):

    error=False
    ser = Service_Category.objects.get(id=pid)
    if request.method == "POST":
        n = request.POST['cat']
        try:
            i = request.FILES['image']
            ser.image = i
            ser.save()
        except:
            pass
        de = request.POST['desc']
        ser.category = n
        ser.desc = de
        ser.save()
        error=True
    d = {'error':error,'ser':ser}
    return render(request,'edit_service.html',d)

def View_Service(request):

    ser = Service_Category.objects.all()
    d = {'ser':ser}
    return render(request,'view_service.html',d)

def Add_City(request):
    error=False
    if request.method == "POST":
        c = request.POST['ci']
        City.objects.create(city=c)
        error=True
    d = {'error':error}
    return render(request,'add_city.html',d)


def View_City(request):
    
    ser = City.objects.all()
    d = {'ser':ser}
    return render(request,'view_city.html',d)

def accept_confirmation(request,pid):
    ser = Order.objects.get(id=pid)
    sta = Status.objects.get(status='Accept')
    ser.status = sta
    ser.save()
    return redirect('service_order')

def pending_confirmation(request, pid):
    ser = Order.objects.get(id=pid)
    sta = Status.objects.get(status='pending')
    ser.status = sta
    ser.save()
    return redirect('service_order')


def confirm_message(request,pid):
    ser = Contact.objects.get(id=pid)
    sta = Status.objects.get(status='read')
    ser.status = sta
    ser.save()
    return redirect('new_message')

def delete_service(request,pid):
    ser = Service_Category.objects.get(id=pid)
    ser.delete()
    return redirect('view_service')

def delete_city(request,pid):
    ser = City.objects.get(id=pid)
    ser.delete()
    return redirect('view_city')

def delete_admin_order(request,pid):
    ser = Order.objects.get(id=pid)
    ser.delete()
    return redirect('admin_order')

def delete_Booking(request,pid):
    ser = Order.objects.get(id=pid)
    ser.delete()
    return redirect('customer_order')

def delete_service_man(request,pid):
    ser = Service_Man.objects.get(id=pid)
    ser.delete()
    return redirect('all_service_man')

def delete_customer(request,pid):
    ser = Customer.objects.get(id=pid)
    ser.delete()
    return redirect('all_customer')

def Change_status(request,pid):
    
    error = False
    pro1 = Service_Man.objects.get(id=pid)
    if request.method == "POST":
        stat = request.POST['stat']
        sta = Status.objects.get(status=stat)
        pro1.status=sta
        pro1.save()
        error=True
    d = {'pro':pro1,'error':error}
    return render(request,'status.html',d)

def Order_status(request,pid):
    
    error = False
    pro1 = Order.objects.get(id=pid)
    if request.method == "POST":
        stat = request.POST['stat']
        sta = Status.objects.get(status=stat)
        pro1.status=sta
        pro1.save()
        error=True
    d = {'pro':pro1,'error':error}
    return render(request,'order_status.html',d)

def Order_detail(request,pid):

    pro1 = Order.objects.get(id=pid)
    d = {'pro':pro1}
    return render(request,'order_detail.html',d)

def service_man_detail(request,pid):
    
    pro1 = Service_Man.objects.get(id=pid)
    d = {'pro':pro1}
    return render(request,'service_man_detail.html',d)

def search_cities(request):
    error=""
    try:
        user = User.objects.get(id=request.user.id)
        error = ""
        try:
            sign = Customer.objects.get(user=user)
            error = "pat"
        except:
            pass
    except:
        pass
   
    terror=False
    pro=""
    car = City.objects.all()
    count1=0
    car1 = Service_Category.objects.all()
    c=""
    c1=""
    if request.method=="POST":
        c=request.POST['city']
        c1 = request.POST['cat']
        ser = City.objects.get(city=c)
        ser1 = Service_Category.objects.get(category=c1)
        pro = Service_Man.objects.filter(service_name=ser1,city=ser)
        for i in pro:
            count1+=1
        terror = True
    d = {'c':c,'c1':c1,'count1':count1,'car1':car1,'car':car,'order':pro,'error':error,'terror':terror}
    return render(request,'search_cities.html',d)

def search_services(request):

    error=False
    pro=""
    car = Service_Category.objects.all()
    c=""
    if request.method=="POST":
        c=request.POST['cat']
        ser = Service_Category.objects.get(category=c)
        pro = Service_Man.objects.filter(service_name=ser)
        error=True
    d = {'service':c,'car':car,'order':pro,'error':error}
    return render(request,'search_services.html',d)

def new_message(request):
    
    sta = Status.objects.get(status='unread')
    pro1 = Contact.objects.filter(status=sta)
    d = {'ser':pro1}
    return render(request,'new_message.html',d)

def read_message(request):

    sta = Status.objects.get(status='read')
    pro1 = Contact.objects.filter(status=sta)
    d = {'ser':pro1}
    return render(request,'read_message.html',d)



def customer_service_cat_search(request):
    if request.method == 'GET':
        form = CustomerServiceSearchForm(request.GET)
        if form.is_valid():
            category = form.cleaned_data.get('category')
            print(category)
            # services = Service_Category.objects.filter(category__icontains=category)
            services = Service_Category.objects.filter(category__icontains=category)
            print(services)
            if services:
                return render(request, 'search_results.html', {'services': services})
            else:
                error_message = "No services found for the provided category"
                return render(request, 'search_results.html', {'form': form, 'error_message': error_message})
        else:
            error_message = "Invalid search criteria."
            return render(request, 'search_results.html', {'form': form, 'error_message': error_message})
    else:
        form = CustomerServiceSearchForm()
        return render(request, 'search_results.html', {'form': form})
    
# with city
def customer_service_city_search(request):
    if request.method == 'GET':
        form = ServiceManSearchForm(request.GET)
        if form.is_valid():
            city = form.cleaned_data.get('city')
            print(city)
            # services = Service_Category.objects.filter(category__icontains=category)
            services = Service_Man.objects.filter(city__icontains=city)
            print(services)
            if services:
                return render(request, 'search_results.html', {'services': services})
            else:
                error_message = "No services found for the provided category"
                return render(request, 'search_results.html', {'form': form, 'error_message': error_message})
        else:
            error_message = "Invalid search criteria."
            return render(request, 'search_results.html', {'form': form, 'error_message': error_message})
    else:
        form = CustomerServiceSearchForm()
        return render(request, 'search_results.html', {'form': form})

# Forgot password
    
def generate_otp(length=6):
    """Generate a random OTP of specified length."""
    characters = string.digits
    return ''.join(random.choice(characters) for _ in range(length))    
    
def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return HttpResponse("No user with this email exists.")
        
        # Generate OTP
        otp = generate_otp()

        # Update user's profile with OTP (You might want to create a profile model)
        user.profile.otp = otp
        user.profile.save()

        # Send OTP via email
        subject = 'Password Reset OTP'
        message = f'Your OTP for password reset is: {otp}'
        from_email = 'chinchuofficialweb@gmail.com'  
        recipient_list = [email]
        send_mail(subject, message, from_email, recipient_list)

        return HttpResponse("An OTP has been sent to your email. Please check your inbox.")
    else:
        return render(request, 'forgot_password.html')
    

from django.views.generic import TemplateView
# Razorpay

# class order(TemplateView):
#     template_name=''


# def create_order(request,**kwargs):
#     id=kwargs.get('pk')
#         # Create an order in your database
#     order = Order.objects.get(
#         id=id
#     )
#     service_id = order.service
#     customer_id = order.customer
#     amount = order.price
#     if request.method == 'POST':
#         # id=kwargs.get('pk')
#         # Create an order in your database
#         order = Order.objects.get(
#             id=id
#         ) 
#         service_id = order.service
#         customer_id = order.customer
#         amount = order.price
#         # Initialize Razorpay client with your API keys
#         client = razorpay.Client(auth=(RAZORPAY_KEY_ID,RAZORPAY_SECRET_KEY))

#         # Create Razorpay order
#         razorpay_order = client.order.create({
#             'amount': int(amount) * 100,  # Amount in paisa
#             'currency': 'INR',
#             'receipt': str(order.id),  # Unique ID for the order
#             'payment_capture': '1'  # Auto capture payment
#         })

#         # Redirect user to Razorpay checkout page
#         return render(request, 'checkout.html', {'order': razorpay_order})
#     return render(request, 'create_order.html',{'service':service_id,'customer':customer_id,'amount':amount,'id':id})

@csrf_exempt
def payment_success(request):
    if request.method == 'POST':
        # Get the Razorpay order ID and payment ID from the request
        razorpay_order_id = request.POST.get('razorpay_order_id')
        razorpay_payment_id = request.POST.get('razorpay_payment_id')

        # Fetch the corresponding order from your database
        order = Order.objects.get(id=razorpay_order_id)

        # Update the order status as paid
        order.report_status = 'Payment Successful'
        order.save()

        return render(request, 'payment_success.html')

    return redirect('home')  # Redirect to home page if the request is not a POST request

@csrf_exempt
def payment_failure(request):
    if request.method == 'POST':
        # Get the Razorpay order ID and payment ID from the request
        razorpay_order_id = request.POST.get('razorpay_order_id')
        razorpay_payment_id = request.POST.get('razorpay_payment_id')

        # Fetch the corresponding order from your database
        order = Order.objects.get(id=razorpay_order_id)

        # Update the order status as failed
        order.report_status = 'Payment Failed'
        order.save()

        return render(request, 'payment_failure.html')

    return redirect('home')


from django.shortcuts import render
import razorpay

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest
 
 
# authorize razorpay client with API Keys.
razorpay_client = razorpay.Client(
    auth=(RAZOR_KEY_ID, RAZOR_KEY_SECRET))
 
 
def create_order(request,**kwargs):
    id=kwargs.get('pk')
    # print(id)
    order=Order.objects.get(id=id)
    currency = 'INR'
    amount = order.price * 100   # Rs. 200
 
    # Create a Razorpay Order
    razorpay_order = razorpay_client.order.create({
            'amount': amount,
            'currency': currency,
            'payment_capture': 0,
        })
 
    # order id of newly created order.
    razorpay_order_id = razorpay_order['id']
    callback_url = reverse('paymenthandler', kwargs={'pk': order.id})
    
    # print(callback_url)
    # we need to pass these details to frontend.
    context = {}
    context['razorpay_order_id'] = razorpay_order_id
    context['razorpay_merchant_key'] = RAZOR_KEY_ID
    context['razorpay_amount'] = amount
    context['currency'] = currency
    context['callback_url'] = callback_url
 
    return render(request, 'create_order.html', context=context)
 
 
# we need to csrf_exempt this url as
# POST request will be made by Razorpay
# and it won't have the csrf token.
@csrf_exempt
def paymenthandler(request,**kwargs):
 
    # only accept POST request.
    if request.method == "POST":
        try:
            id=kwargs.get('pk')
            # get the required parameters from post request.
            payment_id = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            signature = request.POST.get('razorpay_signature', '')
            print(payment_id)
            print(razorpay_order_id)
            print(signature)
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
 
            # verify the payment signature.
            result = razorpay_client.utility.verify_payment_signature(
                params_dict)
            if result is not None:
                
                print(id)
                order=Order.objects.get(id=id)
                order.razorpay_order_id=razorpay_order_id
                order.razorpay_payment_id=payment_id
                order.razorpay_signature=signature
                order.report_status = "Success"
                order.save()
                amount = order.price * 100
                print(amount)  # Rs. 200
                try:
 
                    # capture the payemt
                    razorpay_client.payment.capture(payment_id, amount)
 
                    # render success page on successful caputre of payment
                    return render(request, 'paymentsuccess.html')
                except:
 
                    # if there is an error while capturing payment.
                    order.report_status = "Failed"
                    order.save()
                    return render(request, 'paymentfail.html')
            else:
 
                # if signature verification fails.
                return render(request, 'paymentfail.html')
        except:
 
            # if we don't find the required parameters in POST data
            return HttpResponseBadRequest()
    else:
       # if other than POST request is made.
        return HttpResponseBadRequest()
    
    
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import WebsiteReview

@login_required
def website_reviews(request):
    reviews = WebsiteReview.objects.all().order_by('-created_at')  # Get all reviews

    if request.method == "POST":
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        # Prevent duplicate reviews by the same user
        if WebsiteReview.objects.filter(user=request.user).exists():
            review = WebsiteReview.objects.get(user=request.user)
            review.rating = rating
            review.comment = comment
            review.save()
        else:
            WebsiteReview.objects.create(user=request.user, rating=rating, comment=comment)

        return redirect('website_reviews')  # Redirect to avoid duplicate form submissions

    avg_rating = WebsiteReview.get_average_rating()  # Get average rating

    return render(request, 'website_reviews.html', {'reviews': reviews, 'avg_rating': avg_rating})

