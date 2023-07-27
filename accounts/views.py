from django.shortcuts import render,redirect
from .forms import UserForm,LoginForm,CodeForm,DepartmentHrForm
from .models import User,FailedLoginAttempt
from django.http import HttpResponse
from django.contrib import messages
import secrets
import re
from .models import Code,User
from django.urls import path
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate,login,logout
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
# OTP Verification
from .utils import send_sms,verify_user_code
from twilio.base.exceptions import TwilioRestException
#email sending
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.core.mail import EmailMessage
from django.contrib.auth.tokens import default_token_generator
#Blocking user After 3 failed Login Attempt
# from BruteBuster.models import FailedAttempt
from employee_dashboard.models import UserProfile
# from django.utils  import timezone 

# authentication
from django.contrib.auth.models import Group
from employeemanagmentsystem.decorators import unauthenticated_user,allowed_users



from django.db.models import Max

# Create your views here.
@login_required(login_url='login')
def homePage(request):
    return render(request,'accounts/home.html')


@allowed_users(allowed_roles=['HumanResource'])
def Registration(request):
    hr_superuser = request.user.is_authenticated and request.user.is_superuser
    if request.method == 'GET':
        form = UserForm(superuser=hr_superuser)
    else:
        form = UserForm(request.POST,superuser=hr_superuser)
        print('hii4')
        
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            mobile = form.cleaned_data['mobile']
            role = form.cleaned_data['role']
            email = form.cleaned_data['email']
            # employeeCode = form.cleaned_data['username']
            print('hii')
            try:
                print('hii1')
                User.objects.get(email=email)
                messages.error(request, 'User with the same email already exists')
            except User.DoesNotExist:
                if len(mobile) <= 12 and re.match(r'^\+\d+$', mobile):
                    form.add_error('mobile', 'Please enter a valid mobile number with CountryCode (e.g., +1234567890)')
                else:
                    user = form.save(commit=False)
                    last_id = User.objects.aggregate(last_id=Max('id'))['last_id']
                    next_id = last_id+1
                    user.username = f"EMP{str(next_id).zfill(3)}"
                    user.department = request.user.department
                    if request.user.department == User.Department.FRONTEND:
                        user.is_frontend = True
                    elif request.user.department == User.Department.BACKEND:
                        user.is_backend =True
                    else:
                        user.is_testing = True
                        
                    temporary_password = secrets.token_urlsafe(10)
                    current_site = get_current_site(request)
                    mail_subject = "Welcome, Here's Your EmployeeCode and Password to Login..."
                    message = render_to_string('accounts/login_id_pass.html', {
                        'user': user,
                        'password': temporary_password,
                        'domain': current_site,
                    })
                    to_email = email
                    try:
                        send_email = EmailMessage(mail_subject, message, to=[to_email])
                        send_email.send()    
                        password = make_password(temporary_password)
                        user.password = password
                        user.save()
                        if user.role == User.Role.HR:    
                            user.is_hr = True                                                        
                            hr_group = Group.objects.get(name='HumanResource')                            
                            user.groups.add(hr_group) 
                        elif user.role == User.Role.MANAGER:
                            user.is_manager = True                            
                            manager_group = Group.objects.get(name='manager')
                            user.groups.add(manager_group)
                        else:
                            user.is_worker = True
                            worker_group = Group.objects.get(name='worker')
                            user.groups.add(worker_group)
                        user.save()
    
                        profile = UserProfile()
                        profile.user_id = user.id
                        profile.save()
                        if user.role == User.Role.HR:
                            user.is_active = False
                            user.is_testing =False
                            user.is_backend =False
                            user.is_frontend =False
                            user.save()
                           
                            return redirect('hr_departmenting',id=user.id)
                        return redirect('emailpassid')

                    except:
                        messages.error(request, 'Email not sent')
                       
                        
        else:
            print(form.errors)
    context = {
        'form': form,
    }

    return render(request, 'accounts/register.html', context)   


def Hr_departmenting(request,id=0):
    user = User.objects.get(pk=id)
    if request.method == 'POST':
        form = DepartmentHrForm(request.POST)
        if form.is_valid():
            department = form.cleaned_data['department']
            user.department = department
            user.is_active = True
            if user.department == User.Department.FRONTEND:
                user.is_frontend = True
            elif user.department == User.Department.BACKEND:
                user.is_backend =True
            else:
                user.is_testing = True
            user.save()
            return redirect('emailpassid')
        else:
            user.delete()
            return redirect('register')
    form = DepartmentHrForm()
    return render(request,'accounts/hr_departmenting.html',{'form':form})
        # department = request.POST.get('department')
        
    

@unauthenticated_user
def loginPage(request,id=0):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        EmployeeCode = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=EmployeeCode, password=password)
        print(user)
        if user is None:
            try:
                failed_user = FailedLoginAttempt.objects.get(user__username=EmployeeCode)
                if failed_user.user.is_active == False and failed_user.is_blocked == False:
                    messages.error(request,'Your account is blocked')
                    user = User.objects.get(username = EmployeeCode)
                    return redirect('blocked_email',id=user.id)
                elif failed_user.is_blocked == True:
                    messages.error(request,'Wait for the email confirmation')
                else:
                    messages.error(request,'Three failed attempt cause Account block')
            except FailedLoginAttempt.DoesNotExist or FailedLoginAttempt.MultipleObjectsReturned:
                messages.error(request,'unautharized entry ')
        else:
            if 'unblock_by_login' in request.path:
                login(request,user)
                user=User.objects.get(pk=id)
                return redirect('unblock_user_page',id=user.id)
            elif user.last_login is None and not user.is_superuser:
                # First login after registration, redirect to reset password
                return redirect('passwordresetemail', id=user.id)
            else:
                # Regular login, redirect to two-factor authentication
                request.session['pk'] = user.pk
                return redirect('twoFactorAuthentication')

        

    else:
        form = LoginForm()

    context = {'form': form}
    return render(request, 'accounts/login.html', context)





def reset_password(request,id=0):
    if request.method == 'POST':
        password = request.POST.get('password')
        Cpassword = request.POST.get('Cpassword')
        try:
            user = User.objects.get(id=id)
            if password == Cpassword and len(password)>=6:
                
                user.set_password(password)
                user.save()
                login(request,user)
                return redirect('home')
                
            else:
                messages.error(request,'invalid password')
                
        except User.DoesNotExist:
            pass
        
        
        
    return render(request,'accounts/reset_password.html')

def verify(request,uidb64,token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
         
        print(user)
    except (User.DoesNotExist,TypeError,ValueError,OverflowError):
        user = None
        
    if user is not None and default_token_generator.check_token(user,token):
        return redirect('resetpassword',id=user.id)
    else:
        messages.error(request,'Error occurred while Activating')
        return redirect ('login')
 
 
def EmialPassowrdreset(request,id=0):
    if request.method == 'POST' and 'passwordresetemail' in request.path:
        email = request.POST.get('email')
        user = User.objects.get(pk=id)
        print(user)
        if email == user.email:
            try:
                user=User.objects.get(pk=id)
                current_site = get_current_site(request)
                mail_subject = 'reset password' 
                message = render_to_string('accounts/reset_password_verification.html',{
                    'user':user,
                    'domain':current_site,
                    'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                    'token':default_token_generator.make_token(user)    #creating the token for specific user      
                    })
                to_email = email
                send_email = EmailMessage(mail_subject,message,to=[to_email])
                send_email.send()
                return redirect('resetpasswordemailverification')
            except User.DoesNotExist:
                messages.error(request,'Unauthorized Entry caught')
        else:
            user.save()
            return redirect ('login')
            
        
    return render(request,'accounts/email_reset_password.html')

def Login_Id_Pass_email(request):
    messages.success(request,'Email Sended Succesfully') 

    return render(request,'accounts/confirmation_messages.html')


def resetpasswordemail_verificationPage(request):
    messages.success(request,'We Send You a Verification Link to your mail address , please confirm that ')

    return render(request,'accounts/confirmation_messages.html') 



# Two-Factor Authentication view
def TwoFactorAuthentication(request):
    pk = request.session.get('pk')

    if pk:
        user = User.objects.get(pk=pk)
        form = CodeForm(request.POST or None)

        if not request.POST:
            try:
                verification_sid = send_sms(user.mobile)
                print('veri_sid',verification_sid)
                code = Code.objects.create(
                    number=verification_sid,
                    user=user
                )
                messages.success(request, 'We send you an OTP to the registered Mobile Number')
            except TwilioRestException as e:
                messages.error(request, f'Error occurred while sending the OTP: {e}')

        if form.is_valid():
            number = form.cleaned_data.get('number')

            # Retrieve the stored verification SID
            try:
                verification_sid = Code.objects.get(user=user).number
                print(verification_sid)
                # Verify the user-entered code against the stored verification SID
                verification_status = verify_user_code(verification_sid, number)
                print('status',verification_status)
                if verification_status == 'approved':
                    # Verification is successful, proceed with authentication
                    user.is_active = True
                    user.save()
                    login(request, user)
                    print('codeee')
                    Code.objects.filter(user=user).delete()
                    print('codeee_delete')

                    return redirect('home')
                else:
                    messages.error(request, 'Invalid OTP number')

            except Code.DoesNotExist:
                messages.error(request, 'Verification code not found')
            except TwilioRestException as e:
                messages.error(request, f'Error occurred while verifying the OTP: {e}')

    else:
        messages.error(request, 'User not found')

    return render(request, 'accounts/twofactor_auth.html', {'form': form})
          
def logoutPage(request):
    logout(request)
    return redirect('login')
    



def Blocked_email(request,id):
    user = User.objects.get(pk=id)
    return render (request,'accounts/confirmation_messages.html',{'user':user})


def Blocked_send_email(request,id):
    user_blocked = User.objects.get(pk=id)
    if user_blocked.is_frontend:
        hr_users = User.objects.filter(is_frontend=True,is_hr=True)
    elif user_blocked.is_backend:
        hr_users = User.objects.filter(is_backend=True,is_hr=True)
    else:
        hr_users = User.objects.filter(is_testing=True,is_hr=True)
        print(hr_users)
    current_site = get_current_site(request)
    mail_subject = 'Account Blocked' 
    for hr_user in hr_users:
        message = render_to_string('accounts/blocked.html',{
            'user':user_blocked,
            'domain':current_site,
            'uid':user_blocked.email,
            'token':default_token_generator.make_token(user_blocked)    #creating the token for specific user      
            })  
        to_email = hr_user.email
        send_email = EmailMessage(mail_subject,message,to=[to_email])
        failed_user = FailedLoginAttempt.objects.get(user_id=user_blocked.id)
        failed_user.is_blocked=True
        failed_user.save()      
        send_email.send()
        messages.success(request,'You will get an email if its confirmed by the hr')
        return redirect('login')

def unblock(request,uid,token):
    try:
        user = User.objects.get(email=uid)
        print(user)
        print(uid)
        print(token)
        if user is not None and default_token_generator.check_token(user,token):
            if request.user.is_authenticated:
                return redirect('unblock_user_page',id=user.id)
            else:
                return redirect('unblock_by_login',id=user.id)
            
        return HttpResponse('User not exist')
    except:
        return redirect ('home')
    
 
def unblock_user_page(request,id):
    user = User.objects.get(pk=id)
    print('jhgf',user)
    return render(request,'accounts/unblock_user.html',{'user':user}) 

def unblocking_or_deleting_user(request,id):
    
    if 'unblock_blocked_user' in request.path:
        try:
            user = User.objects.get(pk=id)
            failed = FailedLoginAttempt.objects.get(user_id=user.id)
            failed.delete()
            current_site = get_current_site(request)
            mail_subject = 'Account Unblocked' 
            message = render_to_string('accounts/unblock_user_mail.html',{
                'user':user,
                'domain':current_site,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':default_token_generator.make_token(user)    #creating the token for specific user      
                })  
            to_email = user.email
            send_email = EmailMessage(mail_subject,message,to=[to_email])
            send_email.send()
            messages.success(request,'user unblocked') 
            return redirect('unblock_user_confirmed')
        except:
            return HttpResponse('Something went wrong')
    else:
        try:
            user = User.objects.get(pk=id) 
            if FailedLoginAttempt.objects.filter(user_id=user.id).exists():     
                user.delete()
                messages.success(request,'user deleted')
                return redirect('delete_user_confirmed')
        except:
            return HttpResponse('something went wrong')
    
def unblock_confirmed(request):
    return render(request,'accounts/confirmation_unblock_delete.html')


def unblocked(request,uidb64,token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist,TypeError,ValueError,OverflowError):
        user = None
        
    if user is not None and default_token_generator.check_token(user,token): 
        user.is_active = True
        user.save()
        return redirect('blocked_resetpassword',id=user.id)
    else:
        return redirect('login')