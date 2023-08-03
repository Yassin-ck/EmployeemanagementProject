from .models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from employee_dashboard.models import UserProfile
@receiver(post_save, sender=User)
def post_save_generator_code(sender,instance,created,*args,**kwargs):
#when superuser is created then automatically his profile will be created by using signals
    if created:
        if instance.is_superuser:
            user = UserProfile.objects.create(user=instance)
            user.profile_picture = 'userprofile/default.profilepicture.jpg'
            user.save()
