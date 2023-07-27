from django.urls import path
from . import views

urlpatterns = [
    path('register/',views.Registration,name='register'),
    path('',views.loginPage,name='login'),
    path('logout/',views.logoutPage,name='logout'),
    path('home/',views.homePage,name='home'),
    path('hr_departmenting/<int:id>/',views.Hr_departmenting,name='hr_departmenting'),
    path('resetpassword/<int:id>/',views.reset_password,name='resetpassword'),
    path('verify/<uidb64>/<token>/',views.verify,name='verify'),
    path('passwordresetemail/<int:id>/', views.EmialPassowrdreset,name='passwordresetemail'),
    path('emailpassid/', views.Login_Id_Pass_email,name='emailpassid'),
    path('resetpasswordemailverification/', views.resetpasswordemail_verificationPage,name='resetpasswordemailverification'),
    path('twoFactorAuthentication/', views.TwoFactorAuthentication,name='twoFactorAuthentication'),
    path('blocked_email/<int:id>/', views.Blocked_email,name='blocked_email'),
    path('send_blocked_email/<int:id>', views.Blocked_send_email,name='send_blocked_email'),
    path('unblock/<uid>/<token>/',views.unblock,name='unblock'),
    path('unblock_user_page/<int:id>/',views.unblock_user_page,name='unblock_user_page'),
    path('unblock_blocked_user/<int:id>/',views.unblocking_or_deleting_user,name='unblock_blocked_user'),
    path('delete_blocked_user/<int:id>/',views.unblocking_or_deleting_user,name='delete_blocked_user'),
    path('unblock_user_confirmed/',views.unblock_confirmed,name='unblock_user_confirmed'),
    path('delete_user_confirmed/',views.unblock_confirmed,name='delete_user_confirmed'),
    path('unblock_by_login/<int:id>/',views.loginPage,name='unblock_by_login'),
    path('unblocked/<uidb64>/<token>/',views.unblocked,name='unblocked'),
    path('blocked_resetpassword/<int:id>/',views.reset_password,name='blocked_resetpassword'),
]
 