# from django.contrib import admin
# from .models import User, Job, Application, Bookmark

# @admin.register(User)
# class UserAdmin(admin.ModelAdmin):
#     list_display = ('username', 'email', 'role', 'is_staff')
#     list_filter = ('role', 'is_staff')
#     search_fields = ('username', 'email')

# @admin.register(Job)
# class JobAdmin(admin.ModelAdmin):
#     list_display = ('title', 'employer', 'location', 'salary', 'expiry_date', 'is_published')
#     list_filter = ('is_published', 'employer')
#     search_fields = ('title', 'location')

# @admin.register(Application)
# class ApplicationAdmin(admin.ModelAdmin):
#     list_display = ('job', 'applicant', 'applied_at')
#     list_filter = ('job', 'applicant')
#     search_fields = ('job__title', 'applicant__username')

# @admin.register(Bookmark)
# class BookmarkAdmin(admin.ModelAdmin):
#     list_display = ('job', 'user', 'created_at')
#     list_filter = ('user',)
#     search_fields = ('job__title', 'user__username')