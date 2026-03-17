from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('openid', models.CharField(db_index=True, max_length=128, unique=True)),
                ('username', models.CharField(blank=True, db_index=True, max_length=64, null=True, unique=True)),
                ('password_hash', models.CharField(default='', max_length=256)),
                ('nickname', models.CharField(default='', max_length=64)),
                ('user_class', models.CharField(db_column='class_name', default='', max_length=64)),
                ('avatar_url', models.CharField(default='', max_length=512)),
                ('profile_completed', models.BooleanField(default=False)),
                ('role', models.CharField(default='user', max_length=16)),
                ('exp', models.IntegerField(default=10)),
                ('score', models.IntegerField(default=10)),
                ('post_count', models.IntegerField(default=0)),
                ('achievement_counts', models.JSONField(default=dict)),
                ('growth_book_public', models.BooleanField(default=False)),
                ('invite_used', models.CharField(blank=True, max_length=64, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={'db_table': 'users'},
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('author_id', models.CharField(max_length=128)),
                ('author_name', models.CharField(default='', max_length=64)),
                ('is_admin', models.BooleanField(default=False)),
                ('content', models.TextField(default='')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'db_table': 'comments', 'ordering': ['created_at']},
        ),
        migrations.CreateModel(
            name='Invite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=32, unique=True)),
                ('role', models.CharField(default='admin', max_length=16)),
                ('used_by', models.CharField(blank=True, max_length=128, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'db_table': 'invites'},
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('from_id', models.CharField(db_index=True, max_length=128)),
                ('from_name', models.CharField(default='', max_length=64)),
                ('to_id', models.CharField(db_index=True, max_length=128)),
                ('content', models.TextField(default='')),
                ('read', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'db_table': 'messages', 'ordering': ['created_at']},
        ),
        migrations.CreateModel(
            name='PointsLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.CharField(db_index=True, max_length=128)),
                ('delta', models.IntegerField(default=0)),
                ('log_type', models.CharField(db_column='type', default='exp', max_length=16)),
                ('reason', models.CharField(max_length=64)),
                ('related_id', models.CharField(default='', max_length=64)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'db_table': 'points_log', 'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_anonymous', models.BooleanField(default=False)),
                ('visible_author_name', models.CharField(default='', max_length=64)),
                ('content', models.TextField(default='')),
                ('images', models.JSONField(default=list)),
                ('category', models.CharField(default='cognition', max_length=32)),
                ('status', models.CharField(default='published', max_length=16)),
                ('pinned', models.BooleanField(default=False)),
                ('points_awarded', models.IntegerField(default=0)),
                ('notify_admin', models.BooleanField(default=False)),
                ('need_offline', models.BooleanField(default=False)),
                ('offline_time', models.CharField(default='', max_length=64)),
                ('offline_place', models.CharField(default='', max_length=128)),
                ('flagged', models.BooleanField(default=False)),
                ('flagged_words', models.JSONField(default=list)),
                ('flagged_categories', models.JSONField(default=list)),
                ('flagged_highlighted', models.TextField(default='')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='posts', to='api.user', to_field='openid')),
            ],
            options={'db_table': 'posts', 'ordering': ['-pinned', '-created_at']},
        ),
        migrations.CreateModel(
            name='Achievement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=128)),
                ('description', models.TextField(default='')),
                ('category', models.CharField(max_length=32)),
                ('dimension', models.CharField(default='', max_length=32)),
                ('subcategory', models.CharField(default='', max_length=32)),
                ('level', models.IntegerField(default=1)),
                ('points', models.IntegerField(default=0)),
                ('exp_awarded', models.IntegerField(default=0)),
                ('images', models.JSONField(default=list)),
                ('status', models.CharField(default='pending', max_length=16)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='achievements', to='api.user', to_field='openid')),
            ],
            options={'db_table': 'achievements', 'ordering': ['-created_at']},
        ),
        migrations.AddField(
            model_name='comment',
            name='post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='api.post'),
        ),
    ]
