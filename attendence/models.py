from django.db import models
from accounts.models import User
from django.db.models import JSONField
# Create your models here.




#Attendence for Users
class AttendenceTable(models.Model):
     
    employee = models.ForeignKey(User,on_delete=models.CASCADE)
    year = models.IntegerField()
    month = models.IntegerField()
    present_data = JSONField(default=list,null=True,blank=True)
    absent_data = JSONField(default=list,null=True,blank=True)
    