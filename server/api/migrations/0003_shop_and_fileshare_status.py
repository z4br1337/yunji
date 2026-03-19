from django.db import migrations, models


def seed_shop_items(apps, schema_editor):
    ShopItem = apps.get_model('api', 'ShopItem')
    defaults = [
        ('file_bag', '青春哲法-文件袋', 200, 5),
        ('brooch', '青春哲法-胸针', 350, 5),
        ('fridge_magnet', '青春哲法-冰箱贴', 400, 5),
        ('fan', '青春哲法-团扇', 500, 5),
        ('mousepad', '灋灋鼠标垫', 1000, 5),
    ]
    for i, (key, title, price, stock) in enumerate(defaults):
        ShopItem.objects.get_or_create(item_key=key, defaults={
            'title': title, 'price': price, 'stock': stock, 'sort_order': i
        })


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_add_file_share'),
    ]

    operations = [
        migrations.AddField(
            model_name='fileshare',
            name='status',
            field=models.CharField(default='approved', max_length=16),
        ),
        migrations.CreateModel(
            name='ShopItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_key', models.CharField(db_index=True, max_length=64, unique=True)),
                ('title', models.CharField(max_length=128)),
                ('image_url', models.CharField(default='', max_length=512)),
                ('price', models.IntegerField(default=0)),
                ('stock', models.IntegerField(default=0)),
                ('sort_order', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'shop_items',
                'ordering': ['sort_order', 'price'],
            },
        ),
        migrations.CreateModel(
            name='ExchangeRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.CharField(db_index=True, max_length=128)),
                ('item_key', models.CharField(max_length=64)),
                ('item_title', models.CharField(max_length=128)),
                ('price', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'exchange_records',
                'ordering': ['-created_at'],
            },
        ),
        migrations.RunPython(seed_shop_items, migrations.RunPython.noop),
    ]
