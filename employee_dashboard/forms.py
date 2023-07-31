from django import forms
from .models import Notice_board,Department_notice,LeaveApply,TodayTasks,UserProfile
from accounts.models import User
import re
from django.urls import re_path 
from django.db.models import Q

#changing dateinput
class DateInput(forms.DateInput):
    input_type = "date"


#Form for workers to let them know there dailytasks to the manager
class TodayTaskForm(forms.ModelForm):
    status = forms.CheckboxInput()
    class Meta:
        model = TodayTasks
        fields = ('comment','status','department_notice_board')

    def __init__(self, *args,user=None,user_edit=None,**kwargs):
        super(TodayTaskForm,self).__init__(*args, **kwargs)
        if user:
            assigned_task_ids = TodayTasks.objects.filter(department_notice_board__assigned_to=user).values_list('department_notice_board_id', flat=True)

            self.fields['department_notice_board'].queryset = Department_notice.objects.filter(
                Q(assigned_to=user) & ~Q(id__in=assigned_task_ids)
            )        
        elif user_edit:
            assigned_task_ids = TodayTasks.objects.filter(department_notice_board__assigned_to=user_edit).values_list('department_notice_board',flat=True)
            print(assigned_task_ids)
            self.fields['department_notice_board'].queryset = Department_notice.objects.filter(id__in=assigned_task_ids)
            



#notice board form for the hr
class NoticeboardForm(forms.ModelForm):
    image = forms.ImageField(required=False)
    class Meta:
        model = Notice_board
        fields = ("title", "subject", "content", "image")

        def __init__(self, *args, **kwargs):
            super().save(*args, **kwargs)
            self.fields["image"].required = False



#department notice form for the manager
class DepartmentnoticeForm(forms.ModelForm):
    title = forms.CharField(required=False)
    subject = forms.CharField(required=False)

    class Meta:
        model = Department_notice
        fields = ("title", "subject", "content", "image",'assigned_to')

    
    def __init__(self,*args,user_role,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields['assigned_to'].required = False       
        # self.fields['assigned_to'].queryset = User.objects.filter(is_worker=True)
        if user_role == 'frontend':
            self.fields['assigned_to'].queryset = User.objects.filter(is_worker=True,is_frontend=True)
        elif user_role == 'backend':
            self.fields['assigned_to'].queryset = User.objects.filter(is_worker=True,is_backend=True)
        elif user_role == 'testing':
            self.fields['assigned_to'].queryset = User.objects.filter(is_worker=True,is_testing=True)


#leaveform for the Users
class LeaveForm(forms.ModelForm):
    start_date = forms.DateField(widget=DateInput)
    end_date = forms.DateField(widget=DateInput,required=False)
    reason = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = LeaveApply
        fields = ("start_date", "end_date", "reason")



#form to update the userdetails
class UserProfileForm(forms.ModelForm):
    profile_picture = forms.ImageField(required=False, widget=forms.FileInput)
    income = forms.FloatField()

    class Meta:
        model = UserProfile
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["user"].required = False

    def clean_alternative_number(self):
        alternative_number = self.cleaned_data["alternative_number"]
        if not re.match(r"^\+[0-9]+$", alternative_number):
            raise forms.ValidationError(
                'Alternative number should start with "+" and contain only digits.'
            )
        return alternative_number

    def clean_city(self):
        city = self.cleaned_data["city"]
        if not re.match(r"^[a-zA-Z]+$", city):
            raise forms.ValidationError(
                "City should only contain alphabetic characters."
            )
        return city

    def clean_state(self):
        state = self.cleaned_data["state"]
        if not re.match(r"^[a-zA-Z]+$", state):
            raise forms.ValidationError(
                "State should only contain alphabetic characters."
            )
        return state

    def clean_country(self):
        country = self.cleaned_data["country"]
        if not re.match(r"^[a-zA-Z]+$", country):
            raise forms.ValidationError(
                "Country should only contain alphabetic characters."
            )
        return country

