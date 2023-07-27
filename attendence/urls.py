from django.urls import path
from . import views

urlpatterns = [
    path('attendence_url/', views.Attendence_url, name='attendence_url'),
    path('attendence_table/<int:year>/<int:month>/<int:id>/', views.Attendence_table, name='attendence_table'),
    path('attendence_table_marking/<int:number>/<int:id>', views.Attendence_table_marks, name='attendence_table_marking'),
    path('attendence_view/<int:year>/<int:month>/<int:id>', views.Attendence_hr_view, name='attendence_view'),
]
