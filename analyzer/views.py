from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.views.generic import View
from dropbox import DropboxOAuth2Flow, oauth, Dropbox
import logging
from .models import UserAccessInfo, UserUsageInfo
from rest_framework import generics
from .serializers import UserUsageInfoSerializer
import dropbox
import itertools


class UserCreateForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(UserCreateForm, self).__init__(*args, **kwargs)

        for fieldname in ['username', 'password1', 'password2']:
            self.fields[fieldname].help_text = None


def index(request):
    return render(request, 'analyzer/index.html')


redirect_uri = "https://dropboxanalyzer.herokuapp.com/dropbox-auth-finish/"
# redirect_uri = "http://localhost:8000/dropbox-auth-finish/"
APP_KEY = ''
APP_SECRET = ''


def make_connection_to_user_dbx(request):
    current_user = UserAccessInfo.objects.get(user_id=request.user.id)
    user_token = current_user.access_token
    dbx_connection = Dropbox(user_token)
    return dbx_connection


def get_user_space_info(request):
    dbx = make_connection_to_user_dbx(request)
    used_space = dbx.users_get_space_usage().used
    if dbx.users_get_current_account().team is None:
        allocated_space = dbx.users_get_space_usage().allocation.get_individual().allocated
    else:
        allocated_space = dbx.users_get_space_usage().allocation.get_team().allocated
    return used_space, allocated_space


def get_user_files_info(request):
    folders = list()
    files = dict()
    files_hash = dict()

    dbx = make_connection_to_user_dbx(request)
    result = dbx.files_list_folder("", recursive=True)

    def process_entries(entries):
        for entry in entries:
            if isinstance(entry, dropbox.files.FileMetadata):
                files[entry.id + "___" + entry.name] = entry.size
                files_hash[entry.id + "___" + entry.name] = entry.content_hash
            elif isinstance(entry, dropbox.files.FolderMetadata):
                folders.append(entry.id + "___" + entry.name)

    process_entries(result.entries)

    while result.has_more:
        result = dbx.files_list_folder_continue(result.cursor)
        process_entries(result.entries)

    used_space, allocated_space = get_user_space_info(request)

    UserUsageInfo.objects.create(user=request.user,
                                 space_used=used_space,
                                 space_allocated=allocated_space,
                                 folders_list=folders,
                                 files_list=files,
                                 files_hash_list=files_hash,
                                 data_available_or_not=True
                                 )


def get_dropbox_auth_flow(web_app_session):
    return DropboxOAuth2Flow(
        APP_KEY, APP_SECRET, redirect_uri, web_app_session, "dropbox-auth-csrf-token")


def dropbox_auth_start(request):
    try:
        verified_or_no = UserAccessInfo.objects.get(user_id=request.user.id).verified_status
    except Exception:  # not a good practice, fix at later stage!
        verified_or_no = False
    if not verified_or_no:
        web_app_session = request.session
        authorize_url = get_dropbox_auth_flow(web_app_session).start()
        return redirect(authorize_url)
    else:
        message = messages.warning(request, message='Only one dropbox account allowed!')
        return render(request, 'analyzer/index.html', {'message': message})


def dropbox_auth_finish(request):
    try:
        oa_auth = get_dropbox_auth_flow(request.session).finish(request.GET)
        if request.method == 'GET':
            user_info_instance = UserAccessInfo(user=request.user, access_token=oa_auth.access_token,
                                                account_id=oa_auth.account_id, dbx_user_id=oa_auth.user_id,
                                                verified_status=True)
            user_info_instance.save()
            get_user_files_info(request)
            return render(request, 'analyzer/dashboard.html')
    except oauth.BadRequestException as e:
        return HttpResponse(e)
    except oauth.BadStateException as e:
        # Start the auth flow again.
        return redirect('home')
    except oauth.CsrfException as e:
        HttpResponse(e)
    except oauth.NotApprovedException as e:
        message = messages.warning(request, message='Oh an approval is required to continue!')
        return render(request, 'analyzer/index.html', {'message': message})
    except oauth.ProviderException as e:
        logger = logging.getLogger(__name__)
        logger.error("Auth error: {}".format(e))
        return HttpResponse(e)


class DashboardData(generics.ListAPIView):
    serializer_class = UserUsageInfoSerializer

    def get_queryset(self, *args, **kwargs):
        queryset = UserUsageInfo.objects.filter(user_id=self.request.user.id)
        return queryset


def get_duplicate_files(request):
    reversed_dict = dict()

    hash_data = UserUsageInfo.objects.get(user_id=request.user.id).files_hash_list

    for key, value in hash_data.items():
        reversed_dict.setdefault(value, list()).append(key)

    list_of_dupes = [file_ids for file_hash, file_ids in reversed_dict.items() if len(file_ids) > 1]

    number_of_dupes = len(list_of_dupes)

    dbx = make_connection_to_user_dbx(request)
    dupe_dict = dict()
    dupe_list = list()
    splitted_items_list = list()
    result = dbx.files_list_folder('', recursive=True)

    def process_entries(entries):
        for item in itertools.chain.from_iterable(list_of_dupes):
            splitted_items = item.split("___")
            splitted_items_list.append(splitted_items[0])

    process_entries(list_of_dupes)

    def check_in_m1(splitted_list, m1):
        for item in splitted_list:
            for entry in m1.entries:
                if isinstance(entry, dropbox.files.FileMetadata):
                    if item == entry.id:
                        dupe_list.append(entry.path_display)
                        dupe_dict[entry.path_display] = [entry.content_hash, entry.client_modified]

    check_in_m1(splitted_items_list, result)

    while result.has_more:
        result = dbx.files_list_folder_continue(result.cursor)
        check_in_m1(splitted_items_list, result)

    return JsonResponse(dupe_dict)


class Dashboard(View):
    def get(self, request, *args, **kwargs):
        try:
            verified_or_no = UserAccessInfo.objects.get(user_id=request.user.id).verified_status
        except Exception:
            verified_or_no = False
        if not verified_or_no:
            return render(request, 'analyzer/index.html')
        else:
            try:
                data_available_or_not = UserUsageInfo.objects.get(user_id=request.user.id).data_available_or_not
            except Exception:
                data_available_or_not = False
            if not data_available_or_not:
                get_user_files_info(request)
                return render(request, 'analyzer/dashboard.html')
            else:
                return render(request, 'analyzer/dashboard.html')
