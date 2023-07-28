from django.shortcuts import render,redirect
from django.http import HttpResponse
from .forms import NoticeboardForm,DepartmentnoticeForm,LeaveForm,UserProfileForm,TodayTaskForm
from .models import Notice_board,Department_notice,LeaveApply,TodayTasks,UserProfile,Paycheque
from django.contrib import messages
from accounts.models import User
from accounts.forms import UserForm
from django.shortcuts import get_object_or_404
#decoratos for authentication and aithorization
from employeemanagmentsystem.decorators import allowed_users,dashboard_authentication

from django.views.decorators.cache import never_cache
from django.urls import path
from datetime import date,timedelta
from attendence.models import AttendenceTable
import calendar

# PDF generation
from django.http import FileResponse
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Table, TableStyle,SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


# Create your views here.
#notice board view for every users 
@dashboard_authentication
def Notice_board_view(request):
    user = request.user
    if user.is_frontend:
        notice_boards = Notice_board.objects.filter(user__is_frontend=True)
        print(notice_boards)
    elif user.is_backend:
        notice_boards = Notice_board.objects.filter(user__is_backend=True)   
        print(notice_boards)
    elif user.is_testing:
        notice_boards = Notice_board.objects.filter(user__is_testing=True)
        print(notice_boards)
    else:
        notice_boards = None
    return render (request,'dashboard/notice_board.html',{'notice_boards':notice_boards})

     


#notice board creation and updation by hr
@allowed_users(allowed_roles=['HumanResource'])
def Notice_board_hr_crud(request, id=0):
    user = request.user
    if request.method == 'GET':
        if id == 0:
            form = NoticeboardForm()
        else:
            notice = Notice_board.objects.get(pk=id)
            form = NoticeboardForm(instance=notice)
        return render(request, 'dashboard/notice_board_hrcrud.html', {'form': form})
    else:
        if id == 0:
            form = NoticeboardForm(request.POST,request.FILES)
        else:
            notice = Notice_board.objects.get(pk=id)
            form = NoticeboardForm(request.POST,request.FILES,instance=notice)
   
        if form.is_valid():
            notice=form.save(commit=False)
            notice.user = request.user
            notice.save()
            
            return redirect('dashboard') 
        return HttpResponse('image size is too big')
  
  
  
#noticeboard delete by hr   
@allowed_users(allowed_roles=['HumanResource'])         
def Notice_board_hr_delete(request,id):

    if request.method =='POST':
        try:
            notice = Notice_board.objects.get(pk=id)
            notice.delete()
        except  Notice_board.DoesNotExist:
            messages.error(request,'Something Went Wrong')
        return redirect('dashboard')       
        
    return render(request,'dashboard/Delete.html')
    
 
 
 
#department notice view by users               
@dashboard_authentication
def Department_notice_view(request): 
    user = request.user 
    if user.is_frontend:     
        department_notices = Department_notice.objects.filter(assigned_to__is_frontend=True)
    elif user.is_backend:     
        department_notices = Department_notice.objects.filter(assigned_to__is_backend=True)
    else:     
        print(user)
        department_notices = Department_notice.objects.filter(assigned_to__is_testing=True)
    return render(request,'dashboard/department_notice.html',{'department_notices':department_notices})
 

    
#department notice creation and updation by the manager 
@allowed_users(allowed_roles=['manager'])         
def Department_notice_crud(request, id=0):
    user = request.user
    user_role = None
    if user.is_frontend:
        user_role = 'frontend'
    elif user.is_backend:
        user_role = 'backend'
    elif user.is_testing:
        user_role = 'testing'

    if request.method == 'POST':
        if id == 0:
            form = DepartmentnoticeForm(data=request.POST, user_role=user_role, files=request.FILES)
        else:
            department_notice = Department_notice.objects.get(pk=id)
            form = DepartmentnoticeForm(data=request.POST, user_role=user_role, instance=department_notice, files=request.FILES)
        if form.is_valid():
            department = form.save(commit=False)
            if not department.assigned_to:
                department.assigned_to = request.user
            department.save()
            return redirect('department_notice_view')
        else:
            print(form.errors)
    else:
        if id == 0:
            form = DepartmentnoticeForm(user_role=user_role)
        else:
            department_notice = Department_notice.objects.get(pk=id)
            form = DepartmentnoticeForm(user_role=user_role, instance=department_notice)

        return render(request, 'dashboard/department_notice_crud.html', {'form': form})

                         



#department notice deletion by the manager
@allowed_users(allowed_roles=['manager'])         
def Department_notice_delete(request,id=0):
        if request.method == 'POST':
            try:
                department_notice = Department_notice.objects.get(pk=id)
                department_notice.delete()
                return redirect('department_notice_view')
            except Department_notice.DoesNotExist:
                messages.error(request,'Something Went Wrong')
        return render(request,'dashboard/Delete.html')
    


#to apply leave for the users and also for editing
@dashboard_authentication
def Leave_user_form(request, id=0): 
    today = date.today()
    year = today.year
    month = today.month
    end_day = calendar.monthrange(year, month)[1]

    user_leave = LeaveApply.objects.filter(user=request.user, status='Pending', start_date__gte=today, end_date__lte=date(year, month, end_day))

    if user_leave.exists():
        messages.error(request, 'Your Leave Request is Pending')
        return redirect('leave_personal_view', id=request.user.id)
    else:
        if request.method == 'POST':
            if id == 0:
                form = LeaveForm(request.POST)            
            else:
                leave = LeaveApply.objects.get(pk=id)
                form = LeaveForm(request.POST, instance=leave)
            
            if form.is_valid():
                start_date = form.cleaned_data['start_date']
                end_date = form.cleaned_data['end_date']
                reason = form.cleaned_data['reason']
                leave = form.save(commit=False)

                if start_date > today:
                    leave.start_date = start_date
                else:
                    messages.error(request, 'Start date must be greater than today')
                    return redirect ('leave_form')

                if end_date:
                    if end_date > start_date and end_date <= date(year, month, end_day):
                         leave.end_date = end_date
                    else:
                        messages.error(request, 'End date must be valid and within the current month')
                        return redirect ('leave_form')
                starting_day_name =start_date.strftime('%A')
                
                if starting_day_name == 'Saturday' or starting_day_name == 'Sunday' :
                    messages.error(request,"No office on the selected date")
                    return redirect ('leave_form')
                if end_date:
                    ending_day_name =end_date.strftime('%A')
                    if ending_day_name == 'Saturday' or ending_day_name == 'Sunday' :
                        messages.error(request,"Last selected day is already leave")
                        return redirect ('leave_form')


                leave.user = request.user
                leave.save()
               
                return redirect('leave_personal_view', id=leave.user.id)
        else:
            if id == 0:
                form = LeaveForm()
            else:
                leave = LeaveApply.objects.get(pk=id)
                form = LeaveForm(instance = leave)
            return render(request,'dashboard/leave_form.html',{'form':form})
            


#to view every leave application to the specified hr and view there on leave applications
@dashboard_authentication
def Leave_user_view(request,id=0):
    user = request.user
    if id == 0:
        if user.is_hr:
            if user.is_frontend:
                leaves = LeaveApply.objects.filter(status='Pending',user__is_frontend=True)
            elif user.is_backend:
                leaves = LeaveApply.objects.filter(status='Pending',user__is_backend=True)
            elif user.is_testing:
                leaves = LeaveApply.objects.filter(status='Pending',user__is_testing=True)
        else:
            return redirect('home')
    else:
        user = get_object_or_404(User,pk=id)
        leaves = LeaveApply.objects.filter(user=user)
        
    return render(request,'dashboard/leave_view.html',{'leaves':leaves})



#leave deletion by the user
@never_cache
def Leave_user_delete(request,id=0):
    if request.method == 'POST':
        leave = LeaveApply.objects.get(pk=id)
        leave.delete()
        return redirect ('leave_form')
    return render(request,'dashboard/Delete.html')

def Leave_approval_rejection(request, id):
    today = date.today()
    year = today.year
    month = today.month
    leave_request = LeaveApply.objects.get(pk=id)
    
    if 'leave_approval' in request.path:
        leave_request.status = 'Approved'
        leave_request.approved_by_hr = request.user
        if leave_request.end_date:
            absent_data = []
            current_date = leave_request.start_date
            while current_date <= leave_request.end_date:
                absent_data.append(current_date.day)
                current_date += timedelta(days=1)
        else:
            absent_data = [leave_request.start_date.day]
        try:
            attendence = AttendenceTable.objects.get(employee=leave_request.user, year=year, month=month)
        except:
            attendence = AttendenceTable.objects.create(employee=leave_request.user, year=year, month=month)
        if attendence.absent_data:
            attendence.absent_data += absent_data           
        else:
            attendence.absent_data = absent_data
        attendence.absent_data = list(set(attendence.absent_data))
        attendence.present_data = list(set(attendence.present_data) - set(attendence.absent_data))
        absent_dates_copy = list(attendence.absent_data)  # Create a copy to avoid modifying the list while iterating

        for nums in absent_dates_copy:
            date_obj = date(year,month,nums)
            if date_obj.strftime('%A') in ['Saturday','Sunday']:
                attendence.absent_data.remove(nums)
        attendence.save()
    else:
        leave_request.status = 'Rejected'
        leave_request.approved_by_hr = request.user
    leave_request.save()
    
    return redirect('leave_view')
        
    




#to view the daily tasks to assigned worker and submitted tasks to teh specified manager
@allowed_users(allowed_roles=['worker','manager'])
def Today_task_view(request,id=0):
    user = request.user
    if id == 0:
        if user.is_frontend:
            today_task = TodayTasks.objects.filter(user__is_frontend=True).order_by('-created_at')
        elif user.is_backend:
            today_task = TodayTasks.objects.filter(user__is_backend=True).order_by('-created_at')
        elif user.is_testing:
            today_task = TodayTasks.objects.filter(user__is_testing=True).order_by('-created_at')
    else:
        user = User.objects.get(pk=id)
        
        today_task = TodayTasks.objects.filter(user=user) 

    return render(request,'dashboard/today_task_view.html',{'today_task':today_task})
    
   
 
#to submit the updation about the daily task of worker assigned by the manager   
@allowed_users(allowed_roles=['worker'])
@dashboard_authentication
def Today_task_personal(request, id=0):
    user = request.user
    department_tasks = Department_notice.objects.filter(assigned_to=user)
    today_tasks = TodayTasks.objects.all()

    unmatched_tasks = []

    for task in department_tasks:
        if not today_tasks.filter(department_notice_board=task).exists():
            unmatched_tasks.append(task)

    form = TodayTaskForm(user=request.user)

    if request.method == 'POST':
        form = TodayTaskForm(request.POST)
        if form.is_valid():
            department_task = form.cleaned_data['department_notice_board']
            comment = form.save(commit=False)
            comment.user = request.user 
            if comment.department_notice_board is None:
                messages.error('department_notice_board', 'Task should be selected')
                return redirect('today_task_personal_form',id=request.user.id)
            if not today_tasks.filter(department_notice_board=department_task).exists():
                comment.save()
                return redirect('today_task_single_view', id=user.id)
            else:
                return redirect('home')
        else:
            print(form.errors) 

    return render(request, 'dashboard/today_task_form.html', {'department_task': unmatched_tasks, 'form': form})


#edit the daily task which already submitted by worker
def Today_task_edit(request,id=0):
    user_edit=request.user
    today_task = TodayTasks.objects.get(pk=id)
    form = TodayTaskForm(user_edit=user_edit,instance=today_task)

    if request.method == 'POST':
        form = TodayTaskForm(user_edit=user_edit,data=request.POST,instance=today_task)
        
        print('notsave')
        if form.is_valid():
            task = form.save(commit=False)
            task.department_notice_board = today_task.department_notice_board
            task.save()
            # print(task.department_notice_board)
            
            print('save')
            return redirect('today_task_single_view',id=request.user.id)
        else:
            print(form.errors)
    return render(request,'dashboard/today_task_form.html',{'form':form})
 
 
#delete the dailiy task which is alredy submitted  by the user
def Today_task_delete(request,id=0):
    if request.method == 'POST':
        tasks = TodayTasks.objects.get(pk=id)
        tasks.delete()  
        return redirect('today_task_single_view',id=request.user.id)  
    return render(request,'dashboard/Delete.html')
            



#to update the user details ,crud only by the hr
@allowed_users(allowed_roles=['HumanResource'])         
def user_profile_form(request, id=0):
    hr_superuser = request.user.is_authenticated and request.user.is_hr 
    if request.method == 'POST':
        userprofile = get_object_or_404(UserProfile, pk=id)
        userprofile_user = userprofile.user
        userform = UserForm(request.POST,superuser=hr_superuser,instance=userprofile_user)
        profileform = UserProfileForm(request.POST, request.FILES, instance=userprofile)
        if userform.is_valid() and profileform.is_valid():
            empcode = userform.cleaned_data['username']
            if len(empcode) < 5:
                userform.add_error('username', 'Username should be at least 5 characters long.')
            if not userform.errors and not profileform.errors :
                   
                user_instance = userform.save(commit=False)
                profile_instance = profileform.save(commit=False)
                if user_instance.department == User.Department.BACKEND:
                    user_instance.is_backend=True
                    user_instance.is_frontend=False
                    user_instance.is_testing=False
                elif user_instance.department == User.Department.FRONTEND:
                    user_instance.is_backend=False
                    user_instance.is_frontend=True
                    user_instance.is_testing=False
                elif user_instance.department == User.Department.TESTING:
                    user_instance.is_backend=False
                    user_instance.is_frontend=False
                    user_instance.is_testing=True
                user_instance.save()
                profile_instance.user = user_instance
                user_instance.save()
                profile_instance.save()
                return redirect('user_profile_single_view',id)
            else:
                print(userform.errors)
                print(profileform.errors)
                return render(request, 'dashboard/user_profile_form.html', {'userform': userform, 'profileform': profileform})
        else:
            print(userform.errors)
            print(profileform.errors)
            return render(request, 'dashboard/user_profile_form.html', {'userform': userform, 'profileform': profileform})
    else:
        userprofile = get_object_or_404(UserProfile, pk=id)
        userprofile_user = userprofile.user
        profileform = UserProfileForm(instance=userprofile)
        userform = UserForm(superuser=hr_superuser,instance=userprofile_user)
        return render(request, 'dashboard/user_profile_form.html', {'userform': userform, 'profileform': profileform})




#to view the profile of every users by their hr and there own profile to everyone
@dashboard_authentication
def user_profile_view(request,id=0):
    user = request.user
    if id==0:
        if user.is_hr:
            if user.is_frontend:
                user_profiles = UserProfile.objects.filter(user__is_frontend=True)
                print('frontend',user_profiles)
            elif user.is_backend:
                user_profiles = UserProfile.objects.filter(user__is_backend=True)
                print('back',user_profiles)
            else :
                user_profiles = UserProfile.objects.filter(user__is_testing=True)
                print('test',user_profiles)
            return render (request,'dashboard/user_profile_view.html',{'user_profiles':user_profiles})
        else:
            return redirect('home')
    else:
        user_profile = UserProfile.objects.get(pk=id)
        print(user_profile)
        return render (request,'dashboard/user_profile_single_view.html',{'user_profile':user_profile})



#userprofile deletion by the hr
@allowed_users(allowed_roles=['HumanResource'])         
def user_profile_delete(request,id=0):
    if request.method =='POST':
        userprofile = UserProfile.objects.get(pk=id)
        userprofile_user = User.objects.get(email=userprofile.user.email)
        userprofile_user.delete()
        return redirect ('user_profile_view')
    return render (request,'dashboard/Delete.html')





#autogenerating salary slip
def Salary_slip(request, id):
    print(type(id))
    
    # Get the user by ID, or return 404 if not found
    user = get_object_or_404(User, pk=id)
    user_profile = user.userprofile

    # Get the current date
    today = date.today()
   
    # Get the first day of the current month
    first_day_of_month = today.replace(day=1)

    # Get the last day of the previous month by subtracting 1 day from the first day of the current month
    last_day_of_previous_month = first_day_of_month - timedelta(days=1)

    # Get the year and month of the previous month
    year = last_day_of_previous_month.year
    month = last_day_of_previous_month.month
    month_name = calendar.month_name[month]
    print(month_name)
    # month_name = calendar.month_name['month']
    month_days = calendar.monthrange(year, month)[1]
    first_day = date(year, month, 1)
    first_day_weekday = first_day.weekday()

    # Calculate the number of Sundays and Saturdays in the month
    sundays = sum(1 for day in range(1, month_days + 1) if date(year, month, day).weekday() == calendar.SUNDAY)
    saturdays = sum(1 for day in range(1, month_days + 1) if date(year, month, day).weekday() == calendar.SATURDAY)
    print('sun',sundays)
    print('sun',saturdays)
    total_month_days = month_days - (sundays + saturdays)

    annual_income = user_profile.income
    if annual_income is not None:
        month_salary = int(annual_income) / 12
        print(month_salary)
    else:
        return HttpResponse('User Profile is not Updated yet')
    one_day_salary = month_salary / total_month_days
    print(one_day_salary)

    try:
        employee_attendance = AttendenceTable.objects.get(employee=user, year=year, month=month)
        print(month)
        print(employee_attendance)
    except AttendenceTable.DoesNotExist:
        return HttpResponse(f"No attendance data of {user} in {month} doesn't Exist")

    present_data = employee_attendance.present_data
    absent_data = employee_attendance.absent_data
   
    present_days = len(present_data)
    absent_days = len(absent_data)
  
    gross_salary = present_days * one_day_salary
    print(gross_salary)

    if user.is_hr:
        incentives = gross_salary * (1 / 25)
        print(incentives)
    elif user.is_manager:
        incentives = gross_salary * (1 / 30)
    elif user.is_worker:
        incentives = gross_salary * (1 / 35)

    total_month_salary = gross_salary + incentives
    deductions = absent_days * one_day_salary

    try:
        paycheque_slip = Paycheque.objects.get(employee=user,year=year,month=month)
    except Paycheque.DoesNotExist:
        if today.day >= 5:
            paycheque_slip = Paycheque.objects.create(
                year=year,month=month,
                employee=user,
                gross_month_salary=month_salary,
                incentives=incentives,
                deductions=deductions,
                month_salary=total_month_salary,
            )
            paycheque_slip.save()
        else:
            last_month = today.replace(day=1) - timedelta(days=1)
            prev_month_year = last_month.year
            prev_month = last_month.month

            try:
                # Retrieve the paycheque slip for the previous month
                paycheque_slip = Paycheque.objects.get(employee=user, year=prev_month_year, month=prev_month)
            except Paycheque.DoesNotExist:
                # Handle the case when the paycheque slip for the previous month does not exist
                return HttpResponse(f"Paycheque slip for the previous month doesn't exist.")
  
    
    return render (request,'dashboard/paycheque_view.html',{'paycheque_slip':paycheque_slip,'year':year,'month_name':month_name,'month':month})


#pdf download for there own salary slip using reportlab
def Paycheque_pdf(request, id):
    user = User.objects.get(pk=id)
    today = date.today()

    # Get the current year and month
    last_month = today - timedelta(days=today.day)

    # Get the last month's year and month
    year = last_month.year
    month = last_month.month

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(buffer, pagesize=letter)

    # Styling
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    heading_style = styles['Heading2']
    normal_style = styles['Normal']
    bold_style = styles['Normal']
    bold_style.fontName = 'Helvetica-Bold'

    # Fetch the Paycheque object
    try:
        paycheques = Paycheque.objects.get(employee=user, year=year, month=month)
    except Paycheque.DoesNotExist:
        return HttpResponse(f"No Paycheque data available for {last_month.strftime('%B %Y')}")

    # Content
    elements = []

    title = Paragraph("Salary Slip", title_style)
    elements.append(title)

    elements.append(Spacer(1, 24))

    data = [
        ["Employee:", user.get_full_name(), ""],
        ["Employee Code:", user.username, ""],
        ["Department:", user.department, ""],
        ["Role:", user.role, ""],
        ["Month:", last_month.strftime('%B %Y'), ""],
        ["Gross Salary:", f"${paycheques.gross_month_salary}", ""],
        ["Incentives:", f"${paycheques.incentives}", ""],
        ["Deductions:", f"${paycheques.deductions}", ""],
        ["Net Salary:", f"${paycheques.month_salary}", ""],
    ]

    table = Table(data, colWidths=[100, 200, 100])
    table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
    ]))

    elements.append(table)

    doc.build(elements)

    buffer.seek(0)

    return FileResponse(buffer, as_attachment=True, filename=f'{user.username}_slip.pdf')