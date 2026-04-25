from rest_framework import serializers

from .models import ChatMessage, Conversation, Product

BUSINESS_TYPE_TEXT = {
    'trade': '二手交易',
    'rental': '租赁',
}

STATUS_TEXT = {
    'trade': {
        'available': '在售',
        'reserved': '交易中',
        'sold': '已售出',
    },
    'rental': {
        'available': '可租赁',
        'renting': '租赁中',
        'returned': '已归还',
    },
}


def get_status_text(product):
    return STATUS_TEXT.get(product.business_type, {}).get(product.status, product.get_status_display())


def get_action_label(product):
    if product.business_type == 'trade':
        if product.status == 'available':
            return '立即购买'
        if product.status == 'reserved':
            return '继续沟通'
        return '已售出'
    if product.status == 'available':
        return '立即租用'
    if product.status == 'renting':
        return '继续沟通'
    return '已归还'

class ProductSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()
    business_type_text = serializers.SerializerMethodField()
    status_text = serializers.SerializerMethodField()
    action_label = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id',
            'title',
            'price',
            'unit',
            'original_price',
            'tag',
            'business_type',
            'business_type_text',
            'status',
            'status_text',
            'action_label',
            'category',
            'img_url',
            'image_urls',
            'images',
            'is_new',
            'description',
            'seller_name',
            'seller_avatar',
            'seller_desc',
            'created_at',
            'updated_at',
        ]
        extra_kwargs = {
            'image_urls': {'write_only': True, 'required': False},
            'seller_avatar': {'required': False},
            'seller_desc': {'required': False},
            'original_price': {'required': False, 'allow_null': True},
            'category': {'required': False},
        }

    def get_images(self, obj):
        if obj.image_urls:
            images = [item.strip() for item in obj.image_urls.splitlines() if item.strip()]
            if images:
                return images
        return [obj.img_url] if obj.img_url else []

    def validate(self, attrs):
        image_urls = attrs.get('image_urls', '')
        if image_urls and not attrs.get('img_url'):
            first_image = next((item.strip() for item in image_urls.splitlines() if item.strip()), '')
            if first_image:
                attrs['img_url'] = first_image
        return attrs

    def get_business_type_text(self, obj):
        return BUSINESS_TYPE_TEXT.get(obj.business_type, obj.get_business_type_display())

    def get_status_text(self, obj):
        return get_status_text(obj)

    def get_action_label(self, obj):
        return get_action_label(obj)


class ConversationSerializer(serializers.ModelSerializer):
    product_title = serializers.CharField(source='product.title', read_only=True)
    product_image = serializers.CharField(source='product.img_url', read_only=True)
    status_text = serializers.CharField(source='get_status_display', read_only=True)
    business_type_text = serializers.CharField(source='get_business_type_display', read_only=True)

    class Meta:
        model = Conversation
        fields = [
            'id',
            'product',
            'product_title',
            'product_image',
            'business_type',
            'business_type_text',
            'status',
            'status_text',
            'title',
            'participant_name',
            'participant_avatar',
            'unread_count',
            'last_message',
            'last_message_at',
            'created_at',
            'updated_at',
        ]


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = [
            'id',
            'conversation',
            'sender_role',
            'sender_name',
            'sender_avatar',
            'content',
            'created_at',
        ]
