from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Job, Application
from django.core.validators import FileExtensionValidator

class CustomUserCreationForm(UserCreationForm):
    role = forms.ChoiceField(choices=User.ROLE_CHOICES)
    company_name = forms.CharField(max_length=255, required=False, label="Company Name (Employers)")
    industry = forms.CharField(max_length=100, required=False, label="Industry (Employers)")
    skills = forms.CharField(max_length=500, required=False, label="Skills (Employees)", help_text="Enter skills separated by commas")
    first_name = forms.CharField(max_length=30, required=False, label="First Name")
    last_name = forms.CharField(max_length=30, required=False, label="Last Name")

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'role', 'company_name', 'industry', 'skills')

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        company_name = cleaned_data.get('company_name')
        industry = cleaned_data.get('industry')
        skills = cleaned_data.get('skills')
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')

        if role == 'employer':
            if not company_name:
                self.add_error('company_name', 'Company name is required for employers.')
            if not industry:
                self.add_error('industry', 'Industry is required for employers.')
        elif role == 'employee':
            if not skills:
                self.add_error('skills', 'Skills are required for employees.')
            if not first_name:
                self.add_error('first_name', 'First name is required for employees.')
            if not last_name:
                self.add_error('last_name', 'Last name is required for employees.')
        return cleaned_data

class EmployerProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('company_name', 'industry')

class EmployeeProfileForm(forms.ModelForm):
    skills = forms.CharField(max_length=500, required=True, help_text="Enter skills separated by commas")
    first_name = forms.CharField(max_length=30, required=True, label="First Name")
    last_name = forms.CharField(max_length=30, required=True, label="Last Name")

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'skills')

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ('title', 'description', 'location', 'salary', 'expiry_date', 'is_published', 'category')
        widgets = {
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
        }

class ApplicationForm(forms.ModelForm):
    resume = forms.FileField(
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
        help_text='Upload a PDF resume (max 2MB)'
    )

    class Meta:
        model = Application
        fields = ('resume',)

    def clean_resume(self):
        resume = self.cleaned_data.get('resume')
        if resume.size > 2 * 1024 * 1024:  # 2MB limit
            raise forms.ValidationError('Resume file size must be under 2MB.')
        return resume