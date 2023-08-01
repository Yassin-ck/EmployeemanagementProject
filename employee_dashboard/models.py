from django.db import models
from accounts.models import User
from PIL import Image
from storages.backends.s3boto3 import S3Boto3Storage
from django.core.files import File
import io
# Create your models here.


#notice board model 
class Notice_board(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    title = models.CharField(max_length=150)
    subject = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='images/',blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    
    class Meta:
        ordering = ['-updated_at','-created_at']
    
    def save(self,*args,**kwargs):
        super().save(*args,**kwargs)
        if self.image:
            storage = S3Boto3Storage()
            with storage.open(self.image.name, 'rb') as image_file:
                img = Image.open(image_file)
                if img.height > 85 or img.width > 85:
                    output_size = (85, 85)
                    img.thumbnail(output_size)
                    # Save the resized image back to the S3 bucket
                    in_memory_file = io.BytesIO()
                    img.save(in_memory_file, format=img.format)
                    in_memory_file.seek(0)
                    # Use the storage backend's save() method to save the resized image
                    storage.save(self.image.name, File(in_memory_file))
        
    
    def __str__(self):
        return self.title



#department model
class Department_notice(models.Model):
    title = models.CharField(max_length=150)
    subject = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='department/',blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    assigned_to = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    class Meta:
        ordering = ['-updated_at','-created_at']
        
        
    def __str__(self):
        return str(self.id)
    
    def save(self,*args,**kwargs):
        super().save(*args,**kwargs)
        if self.image:
            storage = S3Boto3Storage()
            with storage.open(self.image.name, 'rb') as image_file:
                img = Image.open(image_file)
                if img.height > 85 or img.width > 85:
                    output_size = (85, 85)
                    img.thumbnail(output_size)
                    # Save the resized image back to the S3 bucket
                    in_memory_file = io.BytesIO()
                    img.save(in_memory_file, format=img.format)
                    in_memory_file.seek(0)
                    # Use the storage backend's save() method to save the resized image
                    storage.save(self.image.name, File(in_memory_file))

            
#leave model to apply for leave            
class LeaveApply(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True,blank=True)
    reason = models.TextField()  
    approved_by_hr =models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name='approved_leaves_hr',blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES,blank =True,default='Pending') 

 

    class Meta:
        ordering = ['-updated_at','-created_at']
        
        
        
    def __str__(self) :
        return f"{self.user.username}'s Leave Request"
    
    
   

#daily task model for workers and to manager
class TodayTasks(models.Model):
    STATUS_CHOICES = [
        ('Completed', 'Completed'),
        ('Pending', 'Pending'),
    ]
    department_notice_board = models.ForeignKey(Department_notice, on_delete=models.CASCADE, null=True,related_name='department_comment')
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True)
    comment = models.TextField(null=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,blank=True,default="Pending")
    class Meta:
        ordering = ['-updated_at','-created_at']
    
    
    
    def __str__(self):
            return  self.status
       
    





#to update teh user details 
class UserProfile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    income = models.FloatField(null=True)
    address1 = models.TextField()
    address2 = models.TextField()
    city = models.CharField(max_length=20, unique=False)
    state = models.CharField(max_length=20, unique=False)
    country = models.CharField(max_length=20, unique=False)
    alternative_contact_number = models.CharField(max_length=10)
    profile_picture = models.ImageField(upload_to="userprofile/",null=True,blank=True)
    experience = models.CharField(max_length=255)
    
    
    
    
    
    def __str__(self):
        return self.user.username 
    
    def save(self,*args,**kwargs):
        super().save(*args,**kwargs)
        if self.profile_picture:
            storage = S3Boto3Storage()
            with storage.open(self.image.name, 'rb') as image_file:
                img = Image.open(image_file)
                if img.height > 85 or img.width > 85:
                    output_size = (85, 85)
                    img.thumbnail(output_size)
                    # Save the resized image back to the S3 bucket
                    in_memory_file = io.BytesIO()
                    img.save(in_memory_file, format=img.format)
                    in_memory_file.seek(0)
                    # Use the storage backend's save() method to save the resized image
                    storage.save(self.image.name, File(in_memory_file))
        
            
    

#for paycheque
class Paycheque(models.Model):
    employee = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    year = models.IntegerField()
    month = models.IntegerField()
    incentives = models.PositiveIntegerField(default=0)
    deductions = models.PositiveIntegerField(default=0)
    gross_month_salary = models.PositiveIntegerField(default=0)
    month_salary = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    
    
    
    class Meta:
        ordering = ['-updated_at','-created_at']

   
    def __str__(self):
        return self.employee.username
   
            
