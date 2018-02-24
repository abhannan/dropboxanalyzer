from django.db import models
from django.contrib.postgres.fields import ArrayField, JSONField
from django.contrib.auth.models import User


class UserAccessInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    access_token = models.CharField(max_length=100, blank=False)
    account_id = models.CharField(max_length=100, blank=False)
    dbx_user_id = models.CharField(max_length=50, blank=False)
    verified_status = models.BooleanField(default=False)
    verified_at = models.DateTimeField(auto_now_add=True, blank=False)


class UserUsageInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    data_available_or_not = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, blank=False)
    updated_at = models.DateTimeField(auto_now=True, blank=True)
    space_allocated = models.CharField(max_length=15, blank=False)
    space_used = models.CharField(max_length=15, blank=False)
    folders_list = ArrayField(
        ArrayField(
            models.CharField(max_length=100, blank=True),
        ),
    )
    files_list = JSONField()
    files_hash_list = JSONField(default=list)