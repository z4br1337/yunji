from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FileShare',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.CharField(db_index=True, max_length=128)),
                ('title', models.CharField(max_length=128)),
                ('description', models.TextField(default='')),
                ('file_url', models.CharField(max_length=512)),
                ('file_name', models.CharField(default='', max_length=256)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'file_shares',
                'ordering': ['-created_at'],
            },
        ),
    ]
