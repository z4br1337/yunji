# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_user_email_emailverificationcode'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='student_id',
            field=models.CharField(blank=True, db_index=True, max_length=32, null=True, unique=True),
        ),
    ]
