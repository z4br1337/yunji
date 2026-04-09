from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_file_like_wall_boutique'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='topics',
            field=models.JSONField(default=list),
        ),
    ]
