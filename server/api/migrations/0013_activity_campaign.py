from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0012_post_topics'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActivityCampaign',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=120)),
                ('intro', models.TextField(blank=True, default='')),
                ('background_url', models.CharField(blank=True, default='', max_length=512)),
                ('tag', models.CharField(db_index=True, max_length=24)),
                ('is_active', models.BooleanField(db_index=True, default=False)),
                ('updated_by', models.CharField(blank=True, default='', max_length=128)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'activity_campaigns',
                'ordering': ['-updated_at'],
            },
        ),
    ]
