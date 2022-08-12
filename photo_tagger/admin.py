from django.contrib import admin

from .models import Photo, Submission, TagRequest


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ["id", "camera_folder"]
    list_display_links = ["id", "camera_folder"]


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    readonly_fields = ["submission"]


@admin.register(TagRequest)
class TagRequestAdmin(admin.ModelAdmin):
    pass
