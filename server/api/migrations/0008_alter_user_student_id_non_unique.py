from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_user_student_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='student_id',
            field=models.CharField(blank=True, db_index=True, max_length=32, null=True),
        ),
    ]
