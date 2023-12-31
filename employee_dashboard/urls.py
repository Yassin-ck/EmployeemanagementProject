from django.urls import path
from . import views


urlpatterns = [
    path('',views.Notice_board_view,name='dashboard'),
    path('notice_hr_cre ate/',views.Notice_board_hr_crud,name='notice_hr_create'),
    path('notice_hr_edit/<int:id>/',views.Notice_board_hr_crud,name='notice_hr_edit'),
    path('notice_hr_delete/<int:id>/',views.Notice_board_hr_delete,name='notice_hr_delete'),
    path('department_notice_view/',views.Department_notice_view,name='department_notice_view'),
    path('department_notice_create/',views.Department_notice_crud,name='department_notice_create'),
    path('department_notice_edit/<int:id>/',views.Department_notice_crud,name='department_notice_edit'),
    path('department_notice_delete/<int:id>/',views.Department_notice_delete,name='department_notice_delete'),
    path('leave_view/',views.Leave_user_view,name='leave_view'),
    path('leave_personal_view/<int:id>/',views.Leave_user_view,name='leave_personal_view'),
    path('leave_form/',views.Leave_user_form,name='leave_form'),
    path('leave_form_edit/<int:id>/',views.Leave_user_form,name='leave_form_edit'),
    path('leave_form_delete/<int:id>/',views.Leave_user_delete,name='leave_form_delete'),
    path('leave_approval/<int:id>/',views.Leave_approval_rejection,name='leave_approval'),
    path('leave_rejection/<int:id>/',views.Leave_approval_rejection,name='leave_rejection'),
    path('paycheque_view/<int:id>/<int:list_id>',views.Salary_slip,name='paycheque_view'),
    path('paycheque_list/<int:id>',views.paycheque_full_view,name='paycheque_list'),
    path('paycheque_pdf/<int:id>',views.Paycheque_pdf,name='paycheque_pdf'),
    path('user_profile_view/',views.user_profile_view,name='user_profile_view'),
    path('user_profile_single_view/<int:id>/',views.user_profile_view,name='user_profile_single_view'),
    path('user_profile_edit/<int:id>/',views.user_profile_form,name='user_profile_edit'),
    path('user_profile_delete/<int:id>/',views.user_profile_delete,name='user_profile_delete'),   
    path('today_task_view/',views.Today_task_view,name='today_task_view'),   
    path('today_task_single_view/<int:id>/',views.Today_task_view,name='today_task_single_view'),   
    path('today_task_personal_form/<int:id>/',views.Today_task_personal,name='today_task_personal_form'),   
    path('today_task_edit/<int:id>/',views.Today_task_edit,name='today_task_edit'),   
    path('today_task_delete/<int:id>/',views.Today_task_delete,name='today_task_delete'),   
] 



