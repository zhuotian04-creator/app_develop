import json
import os
import re

import requests
from django.conf import settings
from django.core.files.storage import default_storage
from django.db.models import Q
from django.db.utils import OperationalError, ProgrammingError
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, parser_classes
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from .constants import CURRENT_USER
from .models import ChatMessage, Conversation, Product
from .sample_data import CONVERSATION_SEED_DATA, PRODUCT_SEED_DATA, PROFILE_DATA
from .serializers import ChatMessageSerializer, ConversationSerializer, ProductSerializer


def sync_conversation_preview(conversation):
    last_message = conversation.messages.order_by('-created_at').first()
    if last_message:
        conversation.last_message = last_message.content[:255]
        conversation.last_message_at = last_message.created_at
        conversation.save(update_fields=['last_message', 'last_message_at', 'updated_at'])


def add_message(conversation, sender_role, sender_name, content, sender_avatar=''):
    message = ChatMessage.objects.create(
        conversation=conversation,
        sender_role=sender_role,
        sender_name=sender_name,
        sender_avatar=sender_avatar,
        content=content,
    )
    sync_conversation_preview(conversation)
    return message


def build_auto_reply(product, content):
    text = content.strip()
    if '价格' in text or '便宜' in text:
        return '价格已经是校友价了，如果确定要的话我可以优先给你留着。'
    if product.business_type == 'trade':
        return '还在的，我们可以约在图书馆或者宿舍楼下面交。'
    return '可以租的，时间和取还方式都可以在这里继续商量。'


def get_or_create_conversation(product, seed_messages=False):
    conversation = Conversation.objects.filter(product=product, status='active').order_by('-updated_at').first()
    if conversation:
        return conversation, False

    conversation = Conversation.objects.create(
        product=product,
        business_type=product.business_type,
        status='active',
        title=f"{product.title}沟通",
        participant_name=product.seller_name,
        participant_avatar=product.seller_avatar,
    )
    if seed_messages:
        add_message(conversation, 'system', '系统通知', '已建立新的沟通会话。')
        add_message(conversation, 'other', product.seller_name, '你好，可以先和我说下你的需求。', product.seller_avatar)
        conversation.unread_count = 1
        conversation.save(update_fields=['unread_count', 'updated_at'])
    return conversation, True

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by('-created_at')
    serializer_class = ProductSerializer

    def get_queryset(self):
        if not ensure_seed_data():
            return Product.objects.none()
        queryset = super().get_queryset()
        keyword = self.request.query_params.get('keyword', None)
        category = self.request.query_params.get('category', None)
        business_type = self.request.query_params.get('business_type', None)
        status_value = self.request.query_params.get('status', None)
        if keyword:
            queryset = queryset.filter(
                Q(title__icontains=keyword) |
                Q(description__icontains=keyword) |
                Q(category__icontains=keyword) |
                Q(tag__icontains=keyword)
            )
        if category and category != '热门推荐':
            queryset = queryset.filter(Q(category=category) | Q(title__icontains=category))
        if business_type:
            queryset = queryset.filter(business_type=business_type)
        if status_value:
            queryset = queryset.filter(status=status_value)
        return queryset

    def create(self, request, *args, **kwargs):
        if not ensure_seed_data():
            return Response({'detail': '请先执行数据库迁移后再发布商品'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        image_urls = self.request.data.get('image_urls', [])
        if isinstance(image_urls, list):
            serializer.save(image_urls='\n'.join(image_urls), status='available')
            return
        serializer.save(status='available')

    @action(detail=True, methods=['post'])
    def action(self, request, pk=None):
        if not ensure_seed_data():
            return Response({'detail': '请先执行数据库迁移后再操作'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        product = self.get_object()
        action_type = request.data.get('action_type', 'chat')
        conversation, _ = get_or_create_conversation(product, seed_messages=False)
        notice = ''

        if action_type == 'buy':
            if product.business_type != 'trade':
                return Response({'detail': '当前商品不是交易类型'}, status=status.HTTP_400_BAD_REQUEST)
            if product.status == 'available':
                product.status = 'reserved'
                product.save(update_fields=['status', 'updated_at'])
                add_message(conversation, 'system', '系统通知', '你已发起购买请求，请和卖家确认面交时间。')
                add_message(conversation, 'self', CURRENT_USER['nickname'], '你好，我想购买这个商品。', CURRENT_USER['avatar'])
                add_message(conversation, 'other', product.seller_name, '收到，我们可以继续沟通面交细节。', product.seller_avatar)
                conversation.unread_count = 1
                conversation.save(update_fields=['unread_count', 'updated_at'])
            notice = '已发起购买沟通'
        elif action_type == 'rent':
            if product.business_type != 'rental':
                return Response({'detail': '当前商品不是租赁类型'}, status=status.HTTP_400_BAD_REQUEST)
            if product.status == 'available':
                product.status = 'renting'
                product.save(update_fields=['status', 'updated_at'])
                add_message(conversation, 'system', '系统通知', '你已发起租赁请求，请和卖家确认租期与押金。')
                add_message(conversation, 'self', CURRENT_USER['nickname'], '你好，我想租用这件商品。', CURRENT_USER['avatar'])
                add_message(conversation, 'other', product.seller_name, '没问题，我们来确认取件和归还时间。', product.seller_avatar)
                conversation.unread_count = 1
                conversation.save(update_fields=['unread_count', 'updated_at'])
            notice = '已发起租赁沟通'
        elif action_type == 'chat':
            if not conversation.messages.exists():
                add_message(conversation, 'other', product.seller_name, '你好，可以先和我说下你的需求。', product.seller_avatar)
                conversation.unread_count = 1
                conversation.save(update_fields=['unread_count', 'updated_at'])
            notice = '已打开聊天'
        else:
            return Response({'detail': '不支持的操作类型'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'notice': notice,
            'product': ProductSerializer(product).data,
            'conversation': ConversationSerializer(conversation).data,
        })

def ensure_seed_data():
    try:
        product_map = {}
        # 确保所有种子商品都存在
        for seed in PRODUCT_SEED_DATA:
            product = Product.objects.filter(title=seed['title']).first()
            if not product:
                product = Product.objects.create(**seed)
            else:
                # 更新现有商品以确保数据最新
                needs_save = False
                for field in ['business_type', 'status', 'category', 'tag', 'seller_name', 'seller_avatar', 'seller_desc', 'unit']:
                    value = seed.get(field)
                    if value is not None and getattr(product, field) != value:
                        setattr(product, field, value)
                        needs_save = True
                if needs_save:
                    product.save()
            product_map[seed['title']] = product

        # 确保所有种子会话都存在
        for conversation_seed in CONVERSATION_SEED_DATA:
            product = product_map.get(conversation_seed['product_title']) or Product.objects.filter(title=conversation_seed['product_title']).first()
            if not product:
                continue
            
            conversation = Conversation.objects.filter(product=product, title=conversation_seed['title']).first()
            if not conversation:
                conversation = Conversation.objects.create(
                    product=product,
                    business_type=conversation_seed['business_type'],
                    status='active',
                    title=conversation_seed['title'],
                    participant_name=conversation_seed['participant_name'],
                    participant_avatar=conversation_seed['participant_avatar'],
                )
                unread_count = 0
                for message_seed in conversation_seed['messages']:
                    avatar = ''
                    if message_seed['sender_role'] == 'self':
                        avatar = CURRENT_USER['avatar']
                    elif message_seed['sender_role'] == 'other':
                        avatar = conversation.participant_avatar
                    add_message(conversation, message_seed['sender_role'], message_seed['sender_name'], message_seed['content'], avatar)
                    if message_seed['sender_role'] == 'other':
                        unread_count += 1
                conversation.unread_count = unread_count
                sync_conversation_preview(conversation)
                conversation.save(update_fields=['unread_count', 'last_message', 'last_message_at', 'updated_at'])
        return True
    except (OperationalError, ProgrammingError):
        return False


@api_view(['GET'])
def message_list(request):
    if not ensure_seed_data():
        return Response({'stats': {'trade': 0, 'rental': 0, 'system': 0}, 'results': []})
    business_type = request.query_params.get('business_type', '')
    conversations = Conversation.objects.all()
    if business_type:
        conversations = conversations.filter(business_type=business_type)
    stats = {
        'trade': sum(conversation.unread_count for conversation in Conversation.objects.filter(business_type='trade')),
        'rental': sum(conversation.unread_count for conversation in Conversation.objects.filter(business_type='rental')),
        'system': sum(conversation.unread_count for conversation in Conversation.objects.all()),
    }
    return Response({
        'stats': stats,
        'results': ConversationSerializer(conversations, many=True).data,
    })


@api_view(['GET'])
def profile_detail(request):
    has_database = ensure_seed_data()
    nickname = PROFILE_DATA['nickname']
    published_queryset = Product.objects.filter(seller_name=nickname) if has_database else Product.objects.none()
    conversation_queryset = Conversation.objects.all() if has_database else Conversation.objects.none()
    profile = {
        **PROFILE_DATA,
        'published_count': published_queryset.count(),
        'tradeCount': conversation_queryset.filter(business_type='trade', status='active').count(),
        'rentalCount': conversation_queryset.filter(business_type='rental', status='active').count(),
        'conversationCount': conversation_queryset.filter(status='active').count(),
    }
    return Response(profile)


@api_view(['POST'])
def start_conversation(request):
    if not ensure_seed_data():
        return Response({'detail': '请先执行数据库迁移后再操作'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    product = get_object_or_404(Product, pk=request.data.get('product_id'))
    conversation, created = get_or_create_conversation(product, seed_messages=False)
    if created:
        add_message(conversation, 'self', CURRENT_USER['nickname'], '你好，我想先了解一下这个商品。', CURRENT_USER['avatar'])
        add_message(conversation, 'other', product.seller_name, '可以的，你想了解哪方面？', product.seller_avatar)
        conversation.unread_count = 1
        conversation.save(update_fields=['unread_count', 'updated_at'])
    return Response({'conversation': ConversationSerializer(conversation).data})


@api_view(['GET'])
def message_detail(request, conversation_id):
    if not ensure_seed_data():
        return Response({'detail': '请先执行数据库迁移后再查看消息'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    conversation = get_object_or_404(Conversation, pk=conversation_id)
    if conversation.unread_count:
        conversation.unread_count = 0
        conversation.save(update_fields=['unread_count', 'updated_at'])
    return Response({
        'conversation': ConversationSerializer(conversation).data,
        'messages': ChatMessageSerializer(conversation.messages.all(), many=True).data,
    })


@api_view(['POST'])
def send_message(request, conversation_id):
    if not ensure_seed_data():
        return Response({'detail': '请先执行数据库迁移后再发送消息'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    conversation = get_object_or_404(Conversation, pk=conversation_id)
    content = (request.data.get('content') or '').strip()
    if not content:
        return Response({'detail': '消息内容不能为空'}, status=status.HTTP_400_BAD_REQUEST)

    add_message(conversation, 'self', CURRENT_USER['nickname'], content, CURRENT_USER['avatar'])
    product = conversation.product
    reply_content = build_auto_reply(product, content) if product else '收到，我们继续在这里沟通。'
    add_message(conversation, 'other', conversation.participant_name, reply_content, conversation.participant_avatar)
    conversation.unread_count = 1
    conversation.save(update_fields=['unread_count', 'updated_at'])

    return Response({
        'conversation': ConversationSerializer(conversation).data,
        'messages': ChatMessageSerializer(conversation.messages.all(), many=True).data,
    })
def detect_category(text):
    category_keywords = {
        '数码': ['手机', '电脑', '笔记本', '平板', 'ipad', '耳机', '相机', '无人机', '键盘', '鼠标', '显示器', '数码'],
        '电动车': ['电动车', '自行车', '山地车', '单车', '滑板车', '踏板车'],
        '二手书': ['教材', '书', '课本', '考研书', '笔记', '题库', '二手书'],
        '生活': ['台灯', '衣架', '收纳', '风扇', '被子', '行李箱', '生活'],
        '办公': ['打印机', '办公椅', '办公桌', '订书机', '打卡机', '办公'],
        '体育': ['篮球', '足球', '羽毛球', '网球拍', '跑步机', '哑铃', '体育'],
    }
    lowered = text.lower()
    for category, keywords in category_keywords.items():
        if any(keyword in text or keyword in lowered for keyword in keywords):
            return category
    return '数码'


def detect_condition(text):
    condition_keywords = [
        ('全新', ['全新', '未拆封', '未使用', '几乎没用']),
        ('95新', ['95新', '九成五新', '9.5成新']),
        ('9成新', ['9成新', '九成新']),
        ('8成新', ['8成新', '八成新']),
        ('7成新', ['7成新', '七成新']),
        ('6成新', ['6成新', '六成新']),
    ]
    for condition, keywords in condition_keywords:
        if any(keyword in text for keyword in keywords):
            return condition
    return '9成新'


def detect_used_months(text):
    month_patterns = [
        r'用了?(\d+(?:\.\d+)?)\s*个?月',
        r'使用了?(\d+(?:\.\d+)?)\s*个?月',
        r'买了?(\d+(?:\.\d+)?)\s*个?月',
    ]
    for pattern in month_patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    if '半年' in text:
        return '6'
    year_match = re.search(r'(\d+(?:\.\d+)?)\s*年', text)
    if year_match:
        return str(int(float(year_match.group(1)) * 12))
    return ''


def detect_price(text):
    patterns = [
        r'(?:只要|售价|价格|卖|租|日租金|月租金)[^\d]{0,4}(\d+(?:\.\d+)?)',
        r'(\d+(?:\.\d+)?)\s*(?:元|块|块钱)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    return ''


def build_title_from_text(text, category):
    title_keywords = [
        '电动车', '自行车', '山地车', '笔记本', '电脑', '手机', '平板', 'ipad',
        '耳机', '相机', '教材', '课本', '篮球', '足球', '无人机', '打印机'
    ]
    for keyword in title_keywords:
        if keyword.lower() in text.lower() or keyword in text:
            return keyword

    cleaned = re.sub(r'[，。！？,.!?\s]+', ' ', text).strip()
    if not cleaned:
        return f'{category}好物'
    return cleaned[:18]


def build_description_from_text(text, condition, used_months):
    parts = [text.strip()]
    if condition and condition not in text:
        parts.append(f'成色：{condition}')
    if used_months and f'{used_months}个月' not in text:
        parts.append(f'使用时长：约 {used_months} 个月')
    return '；'.join(part for part in parts if part)


def normalize_analysis_result(result, text, business_type):
    category = result.get('category') or detect_category(text)
    condition = result.get('condition') or detect_condition(text)
    used_months = str(result.get('usedMonths') or detect_used_months(text) or '').strip()
    price_value = str(result.get('priceValue') or detect_price(text) or '').strip()
    title = (result.get('title') or '').strip() or build_title_from_text(text, category)
    description = (result.get('description') or '').strip() or build_description_from_text(text, condition, used_months)
    unit = result.get('unit') or ('件' if business_type == 'trade' else '天')
    return {
        'title': title,
        'priceValue': price_value,
        'category': category,
        'condition': condition,
        'usedMonths': used_months,
        'unit': unit,
        'description': description,
    }


def fallback_analyze_text(text, business_type):
    return normalize_analysis_result({}, text, business_type)


# 建议将此 Key 放在环境变量中，避免直接写进源码。
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', '').strip()

@api_view(['POST'])
def ai_analyze(request):
    text = request.data.get('text', '').strip()
    business_type = request.data.get('business_type', 'trade')
    
    if not text:
        return Response({'detail': '缺少分析文本'}, status=status.HTTP_400_BAD_REQUEST)

    if not DEEPSEEK_API_KEY:
        return Response(fallback_analyze_text(text, business_type))

    prompt = f"""
    你是一个校园二手市场的智能助手。请从用户的描述中提取商品信息。
    用户描述: "{text}"
    当前模式: {"二手交易" if business_type == 'trade' else "租赁"}
    
    请严格返回以下 JSON 格式，不要包含任何解释文字：
    {{
        "title": "简短吸引人的标题",
        "priceValue": "数字格式的价格",
        "category": "可选值: 数码, 电动车, 二手书, 生活, 办公, 体育",
        "condition": "例如: 全新, 95新, 9成新, 8成新",
        "usedMonths": "使用了几个月，没有就留空字符串",
        "unit": "{'件' if business_type == 'trade' else '天'}",
        "description": "基于描述生成的专业商品详情"
    }}
    """

    try:
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant that outputs JSON."},
                    {"role": "user", "content": prompt}
                ],
                "response_format": {"type": "json_object"}
            },
            timeout=15
        )
        response.raise_for_status()
        res_json = response.json()
        ai_content = json.loads(res_json['choices'][0]['message']['content'])
        return Response(normalize_analysis_result(ai_content, text, business_type))
    except Exception:
        return Response(fallback_analyze_text(text, business_type))

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def upload_image(request):
    upload = request.FILES.get('file')
    if not upload:
        return Response({'detail': '缺少上传文件'}, status=status.HTTP_400_BAD_REQUEST)

    saved_path = default_storage.save(f'products/{upload.name}', upload)
    normalized_path = saved_path.replace('\\', '/')
    file_url = request.build_absolute_uri(f"{settings.MEDIA_URL}{normalized_path}")
    return Response({'url': file_url}, status=status.HTTP_201_CREATED)
