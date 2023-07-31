from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils  import timezone 
from django.contrib.auth.models import Group
# Create your models here.

#model for registering users
class User(AbstractUser) :
    class Role(models.TextChoices):
        HR = 'HR','Hr'
        MANAGER = 'MANAGER','Manager'
        WORKER = 'WORKER','Worker'
    class Department(models.TextChoices):
        FRONTEND = 'FRONTEND','Frontend'
        BACKEND = 'BACKEND','Backend'
        TESTING = 'TESTING','Testing'        
            
    base_role = Role.HR 
    
    username = models.CharField(max_length=150,null=True,unique=True,blank=True)
    email = models.EmailField(unique=True)
    mobile = models.CharField(default=None,max_length=13)
    role = models.CharField(max_length=50,choices=Role.choices)
    department = models.CharField(max_length=50,choices=Department.choices)
    date_joined = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_manager = models.BooleanField(default=False)
    is_worker = models.BooleanField(default=False)
    is_hr = models.BooleanField(default=False)
    is_frontend = models.BooleanField(default=False)
    is_backend = models.BooleanField(default=False)
    is_testing = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email','department','mobile']
    
    
    
    
    def save(self, *args, **kwargs):
        if self.is_superuser and self.department in [self.Department.FRONTEND, self.Department.BACKEND,self.Department.TESTING]:
            self.is_hr = True
            self.role = self.base_role
            self.is_superuser = True
            if self.department == self.Department.FRONTEND:
                self.is_frontend = True
            elif self.department == self.Department.BACKEND:
                self.is_backend = True
            elif self.department == self.Department.TESTING:
                self.is_testing = True
            super().save(*args, **kwargs)  # Save the user before adding to the group
            hr_group = Group.objects.get(name='HumanResource')
            self.groups.add(hr_group)     
        else:
            
            super().save(*args, **kwargs)  
        
        
#model for twofactorauthentication        
class Code(models.Model):
    number = models.CharField(max_length=255,blank=True,null=True)
    user = models.OneToOneField(User,on_delete=models.CASCADE)  
    
    def __str__(self):
        return str(self.number)   
    

   
        
        

#model for blocked users
class FailedLoginAttempt(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    attempt_count = models.PositiveIntegerField(default=1)
    last_attempt_time = models.DateTimeField(auto_now_add=True)
    block_after_attempts = models.PositiveIntegerField(default=3)
    is_blocked = models.BooleanField(default=False)
    
    
    def __str__(self):
        return f"{self.user} - Attempts : {self.attempt_count}"



