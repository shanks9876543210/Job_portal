from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('employer/dashboard/', views.employer_dashboard, name='employer_dashboard'),
    path('employee/dashboard/', views.employee_dashboard, name='employee_dashboard'),
    path('employer/profile/', views.employer_profile, name='employer_profile'),
    path('employee/profile/', views.employee_profile, name='employee_profile'),
    path('job/create/', views.job_create, name='job_create'),
    path('job/<int:job_id>/edit/', views.job_edit, name='job_edit'),
    path('job/<int:job_id>/delete/', views.job_delete, name='job_delete'),
    path('job/<int:job_id>/applicants/', views.job_applicants, name='job_applicants'),
    path('application/<int:application_id>/resume/', views.download_resume, name='download_resume'),
    path('job/<int:job_id>/apply/', views.job_apply, name='job_apply'),
    path('job/<int:job_id>/', views.job_detail, name='job_detail'),
    path('applied-jobs/', views.applied_jobs, name='applied_jobs'),
    path('job/<int:job_id>/bookmark/', views.bookmark_job, name='bookmark_job'),
    path('bookmarks/', views.bookmarks, name='bookmarks'),
]