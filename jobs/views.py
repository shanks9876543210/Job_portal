from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, JobForm, ApplicationForm, EmployerProfileForm, EmployeeProfileForm
from .models import Job, Application, Bookmark, User
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from django.db import models

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful. Please log in.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'jobs/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'jobs/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role == 'employer':
        return redirect('employer_dashboard')
    return redirect('employee_dashboard')

@login_required
def employer_dashboard(request):
    if request.user.role != 'employer':
        raise PermissionDenied
    jobs = Job.objects.filter(employer=request.user)
    return render(request, 'jobs/employer_dashboard.html', {'jobs': jobs})

@login_required
def employee_dashboard(request):
    if request.user.role != 'employee':
        raise PermissionDenied
    
    # Get category filter and search query
    category = request.GET.get('category', '')
    search_query = request.GET.get('search', '')
    
    # Base queryset
    jobs = Job.objects.filter(is_published=True)
    
    # Apply category filter
    if category:
        jobs = jobs.filter(category=category)
    
    # Apply search filter
    if search_query:
        jobs = jobs.filter(
            models.Q(title__icontains=search_query) |
            models.Q(description__icontains=search_query) |
            models.Q(category__icontains=search_query)
        )
    
    # Recommendation algorithm
    if request.user.skills:
        # Combine job title, description, and category for vectorization
        job_texts = [f"{job.title} {job.description} {job.get_category_display()}" for job in jobs]
        user_skills = request.user.skills.lower()
        
        # Add user skills to the corpus
        corpus = job_texts + [user_skills]
        
        # Use TF-IDF to vectorize texts
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(corpus)
        
        # Compute cosine similarity between user skills and each job
        user_vector = tfidf_matrix[-1]
        job_vectors = tfidf_matrix[:-1]
        similarities = cosine_similarity(user_vector, job_vectors).flatten()
        
        # Create a list of (job, similarity) tuples
        job_similarities = [(job, sim) for job, sim in zip(jobs, similarities)]
        
        # Sort jobs by similarity (descending)
        job_similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Extract sorted jobs
        jobs = [job for job, _ in job_similarities]
    else:
        # If no skills, keep original order
        jobs = list(jobs)
    
    # Get all categories for filter dropdown
    categories = Job.CATEGORY_CHOICES
    
    return render(request, 'jobs/employee_dashboard.html', {
        'jobs': jobs,
        'categories': categories,
        'selected_category': category,
        'search_query': search_query
    })

@login_required
def employer_profile(request):
    if request.user.role != 'employer':
        raise PermissionDenied
    if request.method == 'POST':
        form = EmployerProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully')
            return redirect('employer_dashboard')
    else:
        form = EmployerProfileForm(instance=request.user)
    return render(request, 'jobs/employer_profile.html', {'form': form})

@login_required
def employee_profile(request):
    if request.user.role != 'employee':
        raise PermissionDenied
    if request.method == 'POST':
        form = EmployeeProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully')
            return redirect('employee_dashboard')
    else:
        form = EmployeeProfileForm(instance=request.user)
    return render(request, 'jobs/employee_profile.html', {'form': form})

@login_required
def job_create(request):
    if request.user.role != 'employer':
        raise PermissionDenied
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.employer = request.user
 
            job.save()
            messages.success(request, 'Job posted successfully')
            return redirect('employer_dashboard')
    else:
        form = JobForm()
    return render(request, 'jobs/job_form.html', {'form': form})

@login_required
def job_edit(request, job_id):
    if request.user.role != 'employer':
        raise PermissionDenied
    job = get_object_or_404(Job, id=job_id, employer=request.user)
    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, 'Job updated successfully')
            return redirect('employer_dashboard')
    else:
        form = JobForm(instance=job)
    return render(request, 'jobs/job_form.html', {'form': form})

@login_required
def job_delete(request, job_id):
    if request.user.role != 'employer':
        raise PermissionDenied
    job = get_object_or_404(Job, id=job_id, employer=request.user)
    if request.method == 'POST':
        job.delete()
        messages.success(request, 'Job deleted successfully')
        return redirect('employer_dashboard')
    return render(request, 'jobs/job_confirm_delete.html', {'job': job})

@login_required
def job_applicants(request, job_id):
    if request.user.role != 'employer':
        raise PermissionDenied
    job = get_object_or_404(Job, id=job_id, employer=request.user)
    applicants = Application.objects.filter(job=job)
    return render(request, 'jobs/job_applicants.html', {'job': job, 'applicants': applicants})

@login_required
def download_resume(request, application_id):
    if request.user.role != 'employer':
        raise PermissionDenied
    application = get_object_or_404(Application, id=application_id)
    if application.job.employer != request.user:
        raise PermissionDenied
    file_path = application.resume.path
    with open(file_path, 'rb') as file:
        response = HttpResponse(file.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
        return response

@login_required
def job_apply(request, job_id):
    if request.user.role != 'employee':
        raise PermissionDenied
    job = get_object_or_404(Job, id=job_id, is_published=True)
    if Application.objects.filter(job=job, applicant=request.user).exists():
        messages.error(request, 'You have already applied for this job.')
        return redirect('employee_dashboard')
    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.applicant = request.user
            application.save()
            messages.success(request, 'Application submitted successfully')
            return redirect('employee_dashboard')
    else:
        form = ApplicationForm()
    return render(request, 'jobs/job_apply.html', {'form': form, 'job': job})

@login_required
def job_detail(request, job_id):
    if request.user.role != 'employee':
        raise PermissionDenied
    job = get_object_or_404(Job, id=job_id, is_published=True)
    has_applied = Application.objects.filter(job=job, applicant=request.user).exists()
    return render(request, 'jobs/job_detail.html', {'job': job, 'has_applied': has_applied})

@login_required
def applied_jobs(request):
    if request.user.role != 'employee':
        raise PermissionDenied
    applications = Application.objects.filter(applicant=request.user)
    return render(request, 'jobs/applied_jobs.html', {'applications': applications})

@login_required
def bookmark_job(request, job_id):
    if request.user.role != 'employee':
        raise PermissionDenied
    job = get_object_or_404(Job, id=job_id, is_published=True)
    if not Bookmark.objects.filter(job=job, user=request.user).exists():
        Bookmark.objects.create(job=job, user=request.user)
        messages.success(request, 'Job bookmarked successfully')
    return redirect('employee_dashboard')

@login_required
def bookmarks(request):
    if request.user.role != 'employee':
        raise PermissionDenied
    bookmarks = Bookmark.objects.filter(user=request.user)
    return render(request, 'jobs/bookmarks.html', {'bookmarks': bookmarks})