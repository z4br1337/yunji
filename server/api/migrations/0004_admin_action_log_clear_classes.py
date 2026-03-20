# 导生操作记录表 + 清空所有用户班级并需重新选择

from django.db import migrations, models


def clear_all_user_classes(apps, schema_editor):
    User = apps.get_model('api', 'User')
    User.objects.all().update(user_class='', profile_completed=False)


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_shop_and_fileshare_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdminActionLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('admin_id', models.CharField(db_index=True, max_length=128)),
                ('action', models.CharField(max_length=32)),
                ('target_type', models.CharField(max_length=32)),
                ('target_id', models.CharField(max_length=64)),
                ('detail', models.JSONField(default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'admin_action_logs',
                'ordering': ['-created_at'],
            },
        ),
        migrations.RunPython(clear_all_user_classes, noop_reverse),
    ]
