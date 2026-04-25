from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('secondhand', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='business_type',
            field=models.CharField(choices=[('trade', '二手交易'), ('rental', '租赁')], default='trade', max_length=20, verbose_name='业务类型'),
        ),
        migrations.AddField(
            model_name='product',
            name='status',
            field=models.CharField(choices=[('available', '可用'), ('reserved', '交易中'), ('renting', '租赁中'), ('sold', '已售出'), ('returned', '已归还')], default='available', max_length=20, verbose_name='商品状态'),
        ),
        migrations.AddField(
            model_name='product',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='Conversation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('business_type', models.CharField(choices=[('trade', '二手交易'), ('rental', '租赁'), ('system', '系统')], default='trade', max_length=20, verbose_name='会话类型')),
                ('status', models.CharField(choices=[('active', '进行中'), ('closed', '已结束')], default='active', max_length=20, verbose_name='会话状态')),
                ('title', models.CharField(max_length=200, verbose_name='会话标题')),
                ('participant_name', models.CharField(max_length=50, verbose_name='对方昵称')),
                ('participant_avatar', models.URLField(blank=True, default='', max_length=500, verbose_name='对方头像')),
                ('unread_count', models.PositiveIntegerField(default=0, verbose_name='未读数量')),
                ('last_message', models.CharField(blank=True, default='', max_length=255, verbose_name='最后一条消息')),
                ('last_message_at', models.DateTimeField(blank=True, null=True, verbose_name='最后消息时间')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='conversations', to='secondhand.product')),
            ],
            options={
                'verbose_name': '聊天会话',
                'verbose_name_plural': '聊天会话',
                'ordering': ['-last_message_at', '-updated_at'],
            },
        ),
        migrations.CreateModel(
            name='ChatMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sender_role', models.CharField(choices=[('self', '自己'), ('other', '对方'), ('system', '系统')], default='self', max_length=20, verbose_name='发送方类型')),
                ('sender_name', models.CharField(max_length=50, verbose_name='发送方昵称')),
                ('sender_avatar', models.URLField(blank=True, default='', max_length=500, verbose_name='发送方头像')),
                ('content', models.TextField(verbose_name='消息内容')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('conversation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='secondhand.conversation')),
            ],
            options={
                'verbose_name': '聊天消息',
                'verbose_name_plural': '聊天消息',
                'ordering': ['created_at'],
            },
        ),
    ]
