# Generated by Django 2.0.1 on 2018-02-17 21:36

from django.conf import settings
import django.contrib.postgres.fields
import django.contrib.postgres.fields.hstore
from django.contrib.postgres.operations import HStoreExtension
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        HStoreExtension(),
        migrations.CreateModel(
            name='UserAccessInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('access_token', models.CharField(max_length=100)),
                ('account_id', models.CharField(max_length=100)),
                ('dbx_user_id', models.CharField(max_length=50)),
                ('verified_status', models.BooleanField(default=False)),
                ('verified_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserUsageInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('space_allocated', models.CharField(max_length=15)),
                ('space_used', models.CharField(max_length=15)),
                ('folders_list', django.contrib.postgres.fields.ArrayField(base_field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=100), size=None), size=None)),
                ('files_list', django.contrib.postgres.fields.hstore.HStoreField()),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]