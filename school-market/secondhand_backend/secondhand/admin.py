from django.contrib import admin

from .models import ChatMessage, Conversation, Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'business_type', 'status', 'category', 'price', 'unit', 'seller_name', 'created_at')
    search_fields = ('title', 'description', 'seller_name', 'category')
    list_filter = ('business_type', 'status', 'category', 'tag', 'is_new')


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('title', 'business_type', 'participant_name', 'unread_count', 'last_message_at', 'status')
    search_fields = ('title', 'participant_name', 'last_message')
    list_filter = ('business_type', 'status')


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('conversation', 'sender_name', 'sender_role', 'created_at')
    search_fields = ('sender_name', 'content')
    list_filter = ('sender_role',)
