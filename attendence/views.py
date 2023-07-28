from django.shortcuts import render, redirect
import calendar
import datetime
from django.http import HttpResponse
from accounts.models import User
from .models import AttendenceTable
from django.contrib import messages
from employeemanagmentsystem.decorators import allowed_users, dashboard_authentication


#first function works when user select the attendence 
def Attendence_url(request):
    today = datetime.date.today()
    year = today.year
    month = today.month
    user = request.user
    if user.is_hr:
        return redirect('attendence_view',year=year,month=month,id=user.id)
    return redirect('attendence_table', year=year, month=month, id=user.id)



#Atttendence table for marking the attendence of users
@dashboard_authentication
def Attendence_table(request, year, month, *args, **kwargs):
    user = request.user
    month_day = calendar.month_name[int(month)]
    num_days = calendar.monthrange(year, int(month))[1]
    nums = range(1, num_days + 1)

    # Get the abbreviated day names (Sun, Mon, Tue, etc.)
    weekdays = calendar.day_abbr

    # Get the first day of the month
    first_day = datetime.date(year, int(month), 1)

    # Get the day of the week for the first day (0: Monday, 6: Sunday)
    first_day_weekday = first_day.weekday()

   
    days = [''] * first_day_weekday + list(range(1, num_days + 1))

    # Group the days into rows with 7 days in each row
    num_rows = (num_days + first_day_weekday + 6) // 7  # Add 6 to ensure all days are included in rows
    rows = [days[i * 7 : (i + 1) * 7] for i in range(num_rows)]
    weekends = []
    for row in rows:
        for row_num in row:
            if row_num :
                date_obj = datetime.date(year,month,int(row_num))
                if date_obj.strftime('%A') in ['Saturday','Sunday']:
                    weekends.append(row_num)
                    
    absent_list = []
    try:
        attendence = AttendenceTable.objects.get(employee=user,year=year,month=month)
        display_list = attendence.present_data
        
        absent_list = attendence.absent_data
        
    except AttendenceTable.DoesNotExist:
        display_list = request.session.get('display_list', [])
        absent_list = request.session.get('absent_list', [])
    
    return render(request, 'attendence/attendence_table.html', {
        'user': user,
        'year': year,
        'month': month_day,
        'rows': rows,
        'weekdays': weekdays,
        'present': display_list,
        'absent': absent_list,
        'weekends':weekends
    })



#marked attendence go through here save to the database
@dashboard_authentication
def Attendence_table_marks(request, number,id):
    user = request.user
    today = datetime.date.today()
    year = today.year
    month = today.month

    # Get the selected day
    selected_day_date = datetime.date(year, month, number)
    selected_day_number = selected_day_date.weekday()

    # Get all dates with the same weekday as the selected day in the given month
    selected_day_list = []
    month_days = calendar.monthrange(year, month)[1]
    for day in range(1, month_days + 1):
        date = datetime.date(year, month, day)
        if date.weekday() == selected_day_number:
            selected_day_list.append(date)

    if len(selected_day_list) > 0:
        selected_day = selected_day_list[-1]

        # Check if the selected day is a weekend (Saturday or Sunday)
        if selected_day.strftime('%A') in ['Saturday', 'Sunday']:
            return redirect('attendence_table', year=year, month=month, id= user.id)
        else:
            try:
                attendence_table = AttendenceTable.objects.get(employee=request.user, year=year, month=month)
            except AttendenceTable.DoesNotExist:
                attendence_table = AttendenceTable(employee=request.user, year=year, month=month)

            # Update the attendance data
            present_list = attendence_table.present_data
            absent_list = attendence_table.absent_data
            if number not in absent_list :
                if number in present_list :
                    present_list.remove(number)
                
                else:
 
                    present_list.append(number)
            
            # Save the updated attendance data to the database
            attendence_table.present_data = present_list
            attendence_table.absent_data = absent_list
            attendence_table.save()
        
            return redirect('attendence_table', year=year, month=month,id = user.id )





#table for viewing the whole attendence of the employees to their department Hr
@allowed_users(allowed_roles=['HumanResource'])
def Attendence_hr_view(request,year,month,id):
    
    month_days = calendar.monthrange(year, int(month))[1]
    
    month_name = calendar.month_name[month]
    days = [day for day in range(1,month_days+1)]
    user = User.objects.get(pk=id)
    if user.is_frontend:
        attendence_data = AttendenceTable.objects.filter(employee__is_frontend=True,year=year,month=month)
    elif user.is_backend:
        attendence_data = AttendenceTable.objects.filter(employee__is_backend=True,year=year,month=month)
    elif user.is_testing:
        attendence_data = AttendenceTable.objects.filter(employee__is_testing=True,year=year,month=month)
    return render(request,'attendence/attendence_view.html',{
        'attendence_data':attendence_data,
        'year':year,
        'month':month,
        'month_name':month_name,
        'id':id,
        'days':days
        })
    
    
    
    

   
  
  
  
    
    
    
    
