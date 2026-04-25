from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='商品标题')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='价格')),
                ('unit', models.CharField(default='天', max_length=20, verbose_name='单位')),
                ('original_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('tag', models.CharField(max_length=50, verbose_name='标签')),
                ('category', models.CharField(default='热门推荐', max_length=50, verbose_name='分类')),
                ('img_url', models.URLField(max_length=500, verbose_name='主图链接')),
                ('image_urls', models.TextField(blank=True, default='', verbose_name='图片链接列表')),
                ('is_new', models.CharField(max_length=50, verbose_name='新旧程度')),
                ('description', models.TextField(verbose_name='商品描述')),
                ('seller_name', models.CharField(default='小黄同学', max_length=50, verbose_name='卖家昵称')),
                ('seller_avatar', models.URLField(blank=True, default='', max_length=500, verbose_name='卖家头像')),
                ('seller_desc', models.CharField(blank=True, default='黄河科技学院 · 23级', max_length=100, verbose_name='卖家描述')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': '二手商品',
                'verbose_name_plural': '二手商品',
            },
        ),
    ]
