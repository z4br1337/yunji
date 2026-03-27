import django.utils.timezone
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_alter_user_student_id_non_unique'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='parent_comment',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='replies',
                to='api.comment',
            ),
        ),
        migrations.AddField(
            model_name='user',
            name='interaction_reply_seen_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='user',
            name='interaction_post_comment_seen_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
