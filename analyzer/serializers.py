from rest_framework import serializers
from .models import UserUsageInfo, UserAccessInfo
from collections import Counter
import itertools
import dropbox


class UserUsageInfoSerializer(serializers.ModelSerializer):

    files_count = serializers.SerializerMethodField()
    folders_count = serializers.SerializerMethodField()
    files_categories = serializers.SerializerMethodField()
    files_categories_sizes = serializers.SerializerMethodField()

    class Meta:
        model = UserUsageInfo
        fields = (
            'space_allocated',
            'space_used',
            'files_count',
            'folders_count',
            'files_categories',
            'files_categories_sizes',
        )

    def get_files_count(self, obj):
        return len(obj.files_list)

    def get_folders_count(self, obj):
        return len(obj.folders_list)

    def get_files_categories(self, obj):
        file_categories = Counter(file.split(".")[-1] for file in obj.files_list)

        img_extns = ['ai', 'bmp', 'gif', 'ico', 'jpeg', 'jpg', 'png', 'psd', 'svg', 'tif', 'tiff', 'cr2']
        audio_extns = ['aif', 'cda', 'mid', 'midi', 'mp3', 'mpa', 'ogg', 'wav', 'wma', 'wpl']
        video_extns = ['3g2', '3gp', 'avi', 'flv', 'm4v', 'mkv', 'mov', 'mp4', 'mpg', 'mpeg', 'rm',
                       'swf', 'vob', 'wmv']
        docs_extns = ['ppt', 'pptx', 'key', 'odp', 'pps', 'ods', 'xlr', 'xls', 'xlsx', 'doc',
                      'docx', 'odt', 'pdf', 'rtf', 'txt', ]

        categories = {'Images': 0, 'Videos': 0, 'Documents': 0, 'Others': 0, 'Audios': 0}

        for key, value in file_categories.items():
            if key.lower() in img_extns:
                categories['Images'] += value
            elif key.lower() in audio_extns:
                categories['Audios'] += value
            elif key.lower() in video_extns:
                categories['Videos'] += value
            elif key.lower() in docs_extns:
                categories['Documents'] += value
            else:
                categories['Others'] += value
        return categories

    def get_files_categories_sizes(self, obj):
        img_extns = ['ai', 'bmp', 'gif', 'ico', 'jpeg', 'jpg', 'png', 'psd', 'svg', 'tif', 'tiff', 'cr2']
        audio_extns = ['aif', 'cda', 'mid', 'midi', 'mp3', 'mpa', 'ogg', 'wav', 'wma', 'wpl']
        video_extns = ['3g2', '3gp', 'avi', 'flv', 'm4v', 'mkv', 'mov', 'mp4', 'mpg', 'mpeg', 'rm',
                       'swf', 'vob', 'wmv']
        docs_extns = ['ppt', 'pptx', 'key', 'odp', 'pps', 'ods', 'xlr', 'xls', 'xlsx', 'doc',
                      'docx', 'odt', 'pdf', 'rtf', 'txt', ]
        categories_sizes_dict = dict()
        for key, value in obj.files_list.items():
            temp_keys = key.rsplit(".", 1)[-1]
            categories_sizes_dict.setdefault(temp_keys, 0)
            categories_sizes_dict[temp_keys] += value

        categories_dict = {'Images': 0, 'Videos': 0, 'Documents': 0, 'Others': 0, 'Audios': 0}

        for key, value in categories_sizes_dict.items():
            if key.lower() in img_extns:
                categories_dict['Images'] += value
            elif key.lower() in audio_extns:
                categories_dict['Audios'] += value
            elif key.lower() in video_extns:
                categories_dict['Videos'] += value
            elif key.lower() in docs_extns:
                categories_dict['Documents'] += value
            else:
                categories_dict['Others'] += value
        return categories_dict
