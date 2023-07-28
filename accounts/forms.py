from django import forms
from django.forms import PasswordInput
from .models import User,Code
import re
from django.urls import path

#Registration and user profileUpdattion Form
class UserForm(forms.ModelForm):
    mobile = forms.CharField(max_length=13)
    is_superuser = forms.CheckboxInput()
    is_staff = forms.CheckboxInput()
    is_worker = forms.CheckboxInput()
    
    class Meta:
        model = User
        exclude = ['password']
        
        fields = ('first_name','last_name','email','role','mobile','username','department')
                  
        error_messages = {
            'username':{
                'unique':'User with this EmployeeCode already exists'
            },
            'mobile':{
                'unique':'User with this  Mobile Number  already exists.'
            },
        }
        labels = {
            'first_name' : 'First Name',
            'last_name' : 'Last Name',
            'email':'Email',
            'role':'Role',
            'mobile':'Mobile Number',
            'username':'Employee-Code',
            'department':'Department',
            'is_superuser':'Human Resource',
            'is_manager' : 'Manager',
            'is_worker':'Worker',
       
        }
        def clean_first_name(self):
            first_name = self.cleaned_data['first_name']
            if not re.match(r'^[a-zA-Z]+$', first_name):
                raise forms.ValidationError('First name should only contain alphabetic characters.')
            return first_name

        def clean_last_name(self):
            last_name = self.cleaned_data['last_name']
            if not re.match(r'^[a-zA-Z]+$', last_name):
                raise forms.ValidationError('Last name should only contain alphabetic characters.')
            return last_name
        
        def clean_mobile(self):
            mobile = self.cleaned_data['mobile']
            if not re.match(r'^\+[0-9]+$', mobile):
                raise forms.ValidationError('Mobile number should start with "+" and contain only digits.')
            return mobile

        
    def __init__(self, *args, **kwargs):
        superuser = kwargs.pop('superuser',False)        
        super().__init__(*args, **kwargs)
        self.fields['department'].required = False
        self.fields['role'].widget.choices[0] = ('', 'Select')
        if not superuser:
            self.fields['role'].choices = [choice for choice in self.fields['role'].choices if choice[0] !=User.Role.HR ]
    
  
 
#selecting department for new registerd hr 
class DepartmentHrForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('department',)

 
   
#user login form         
class LoginForm(forms.ModelForm):
    username = forms.CharField(required=True)
    password = forms.CharField(widget=forms.PasswordInput)


    widgets = {
            'password': PasswordInput(attrs={'type': 'password'})
        }
    class Meta:
        model = User
        fields = ('username','password')
        error_messages = {
            'username':{
                'unique':''
            }
        }
        labels ={
            'username':'Employee-Code',
            'password':'Password'
        }
        

#two factor authentication form          
class CodeForm(forms.ModelForm):
    number =  forms.CharField(label='Code',required=False)
   
    class Meta:
        model = Code
        fields = ('number',)
            
           