from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_post_featured_like'),
    ]

    operations = [
        migrations.AddField(
            model_name='fileshare',
            name='like_count',
            field=models.IntegerField(default=0),
        ),
        migrations.CreateModel(
            name='FileShareLike',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.CharField(db_index=True, max_length=128)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('file_share', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='file_share_likes', to='api.fileshare')),
            ],
            options={
                'db_table': 'file_share_likes',
                'unique_together': {('file_share', 'user_id')},
            },
        ),
        migrations.CreateModel(
            name='ProfileWallMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('profile_owner_id', models.CharField(db_index=True, max_length=128)),
                ('author_id', models.CharField(db_index=True, max_length=128)),
                ('author_name', models.CharField(default='', max_length=64)),
                ('is_admin', models.BooleanField(default=False)),
                ('content', models.TextField(default='')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'profile_wall_messages',
                'ordering': ['-is_admin', '-created_at'],
            },
        ),
    ]
