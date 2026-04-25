from django.db import models


class Product(models.Model):
    BUSINESS_TYPE_CHOICES = [
        ('trade', '二手交易'),
        ('rental', '租赁'),
    ]
    STATUS_CHOICES = [
        ('available', '可用'),
        ('reserved', '交易中'),
        ('renting', '租赁中'),
        ('sold', '已售出'),
        ('returned', '已归还'),
    ]

    title = models.CharField(max_length=200, verbose_name="商品标题")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="价格")
    unit = models.CharField(max_length=20, default="天", verbose_name="单位")
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tag = models.CharField(max_length=50, verbose_name="标签")
    business_type = models.CharField(max_length=20, choices=BUSINESS_TYPE_CHOICES, default='trade', verbose_name="业务类型")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available', verbose_name="商品状态")
    category = models.CharField(max_length=50, default="热门推荐", verbose_name="分类")
    img_url = models.URLField(max_length=500, verbose_name="主图链接")
    image_urls = models.TextField(blank=True, default="", verbose_name="图片链接列表")
    is_new = models.CharField(max_length=50, verbose_name="新旧程度")
    description = models.TextField(verbose_name="商品描述")
    seller_name = models.CharField(max_length=50, default="小黄同学", verbose_name="卖家昵称")
    seller_avatar = models.URLField(max_length=500, blank=True, default="", verbose_name="卖家头像")
    seller_desc = models.CharField(max_length=100, blank=True, default="黄河科技学院 · 23级", verbose_name="卖家描述")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "二手商品"
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Conversation(models.Model):
    BUSINESS_TYPE_CHOICES = [
        ('trade', '二手交易'),
        ('rental', '租赁'),
        ('system', '系统'),
    ]
    STATUS_CHOICES = [
        ('active', '进行中'),
        ('closed', '已结束'),
    ]

    product = models.ForeignKey(Product, related_name='conversations', null=True, blank=True, on_delete=models.CASCADE)
    business_type = models.CharField(max_length=20, choices=BUSINESS_TYPE_CHOICES, default='trade', verbose_name="会话类型")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="会话状态")
    title = models.CharField(max_length=200, verbose_name="会话标题")
    participant_name = models.CharField(max_length=50, verbose_name="对方昵称")
    participant_avatar = models.URLField(max_length=500, blank=True, default="", verbose_name="对方头像")
    unread_count = models.PositiveIntegerField(default=0, verbose_name="未读数量")
    last_message = models.CharField(max_length=255, blank=True, default="", verbose_name="最后一条消息")
    last_message_at = models.DateTimeField(null=True, blank=True, verbose_name="最后消息时间")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "聊天会话"
        verbose_name_plural = verbose_name
        ordering = ['-last_message_at', '-updated_at']

    def __str__(self):
        return self.title


class ChatMessage(models.Model):
    SENDER_ROLE_CHOICES = [
        ('self', '自己'),
        ('other', '对方'),
        ('system', '系统'),
    ]

    conversation = models.ForeignKey(Conversation, related_name='messages', on_delete=models.CASCADE)
    sender_role = models.CharField(max_length=20, choices=SENDER_ROLE_CHOICES, default='self', verbose_name="发送方类型")
    sender_name = models.CharField(max_length=50, verbose_name="发送方昵称")
    sender_avatar = models.URLField(max_length=500, blank=True, default="", verbose_name="发送方头像")
    content = models.TextField(verbose_name="消息内容")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "聊天消息"
        verbose_name_plural = verbose_name
        ordering = ['created_at']

    def __str__(self):
        return f"{self.sender_name}: {self.content[:20]}"
