from django.contrib import admin
from .models import UserAccessInfo, UserUsageInfo


class UserInfoAdmin(admin.ModelAdmin):
    model = UserAccessInfo
    list_display = ('user', 'access_token', 'account_id', 'dbx_user_id',
                    'verified_status', 'verified_at')


class UserDropboxDataAdmin(admin.ModelAdmin):
    model = UserUsageInfo
    list_display = ('user', 'space_allocated', 'space_used', 'files_list',
                    'folders_list', 'files_hash_list', 'data_available_or_not')

admin.site.register(UserAccessInfo, UserInfoAdmin)
admin.site.register(UserUsageInfo, UserDropboxDataAdmin)