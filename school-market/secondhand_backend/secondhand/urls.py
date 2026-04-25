from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProductViewSet,
    ai_analyze,
    message_detail,
    message_list,
    profile_detail,
    send_message,
    start_conversation,
    upload_image,
)

router = DefaultRouter()
router.register(r'products', ProductViewSet)

urlpatterns = [
    path('ai-analyze/', ai_analyze),
    path('messages/', message_list),
    path('messages/start/', start_conversation),
    path('messages/<int:conversation_id>/', message_detail),
    path('messages/<int:conversation_id>/send/', send_message),
    path('profile/', profile_detail),
    path('uploads/', upload_image),
    path('', include(router.urls)),
]
