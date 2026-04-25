<template>
	<view class="container">
		<view class="status-bar"></view>
		<view class="nav-header">
			<text class="back-icon" @click="goBack">⬅️</text>
			<view class="nav-center">
				<text class="nav-title">{{conversation.name || '聊天'}}</text>
				<text class="nav-subtitle">{{conversation.businessTypeText || ''}}</text>
			</view>
			<text class="share-icon">⋯</text>
		</view>

		<scroll-view scroll-y class="chat-scroll" :scroll-into-view="scrollTarget">
			<view
				v-for="message in messages"
				:key="message.id"
				:id="`msg-${message.id}`"
				:class="['message-row', message.sender_role]"
			>
				<image
					v-if="message.sender_role !== 'system'"
					class="avatar"
					:src="message.sender_avatar || defaultAvatar"
					mode="aspectFill"
					@error="handleAvatarError(message)"
				></image>
				<view :class="['bubble', message.sender_role]">
					<text class="bubble-name" v-if="message.sender_role === 'other'">{{message.sender_name}}</text>
					<text class="bubble-text">{{message.content}}</text>
				</view>
			</view>
		</scroll-view>

		<view class="input-bar">
			<input class="chat-input" v-model="draft" placeholder="和对方聊聊成交时间、取件地点..." />
			<button class="send-btn" :disabled="!draft.trim() || sending" @click="sendMessage">{{sending ? '发送中' : '发送'}}</button>
		</view>
	</view>
</template>

<script>
import { getConversationDetail, sendConversationMessage } from '@/api/secondhand.js'

const DEFAULT_AVATAR = '/static/logo.png'

export default {
	data() {
		return {
			conversationId: null,
			conversation: {},
			messages: [],
			draft: '',
			sending: false,
			scrollTarget: '',
			defaultAvatar: DEFAULT_AVATAR
		}
	},
	onLoad(options) {
		this.conversationId = options.id;
	},
	onShow() {
		this.loadConversation();
	},
	methods: {
		handleAvatarError(message) {
			message.sender_avatar = DEFAULT_AVATAR;
		},
		goBack() {
			uni.navigateBack();
		},
		scrollToBottom() {
			if (!this.messages.length) {
				return;
			}
			this.scrollTarget = `msg-${this.messages[this.messages.length - 1].id}`;
		},
		async loadConversation() {
			if (!this.conversationId) {
				return;
			}
			try {
				const res = await getConversationDetail(this.conversationId);
				this.conversation = res.conversation || {};
				this.messages = res.messages || [];
				this.$nextTick(() => this.scrollToBottom());
			} catch (error) {
				uni.showToast({ title: '聊天加载失败', icon: 'none' });
			}
		},
		async sendMessage() {
			const content = this.draft.trim();
			if (!content) {
				return;
			}
			this.sending = true;
			try {
				const res = await sendConversationMessage(this.conversationId, content);
				this.conversation = res.conversation || this.conversation;
				this.messages = res.messages || this.messages;
				this.draft = '';
				this.$nextTick(() => this.scrollToBottom());
			} catch (error) {
				uni.showToast({ title: '发送失败', icon: 'none' });
			} finally {
				this.sending = false;
			}
		}
	}
}
</script>

<style>
.container { min-height: 100vh; background: #f8f8f8; padding-bottom: 120rpx; }
.status-bar { height: var(--status-bar-height); background: #fff; }
.nav-header { height: 88rpx; background: #fff; display: flex; align-items: center; justify-content: space-between; padding: 0 30rpx; border-bottom: 1rpx solid #eee; }
.nav-center { display: flex; flex-direction: column; align-items: center; }
.nav-title { font-size: 30rpx; font-weight: bold; color: #333; }
.nav-subtitle { font-size: 20rpx; color: #999; margin-top: 4rpx; }
.chat-scroll { height: calc(100vh - 220rpx - var(--status-bar-height)); padding: 30rpx; box-sizing: border-box; }
.message-row { display: flex; margin-bottom: 24rpx; align-items: flex-start; }
.message-row.self { flex-direction: row-reverse; }
.message-row.system { justify-content: center; }
.avatar { width: 72rpx; height: 72rpx; border-radius: 50%; margin: 0 16rpx; background: #eee; }
.bubble { max-width: 470rpx; border-radius: 24rpx; padding: 18rpx 22rpx; box-sizing: border-box; }
.bubble.self { background: #ef4444; color: #fff; border-top-right-radius: 8rpx; }
.bubble.other { background: #fff; color: #333; border-top-left-radius: 8rpx; box-shadow: 0 4rpx 12rpx rgba(0,0,0,0.04); }
.bubble.system { background: #f3f4f6; color: #666; font-size: 22rpx; border-radius: 999rpx; }
.bubble-name { font-size: 20rpx; color: #999; margin-bottom: 8rpx; display: block; }
.bubble-text { font-size: 28rpx; line-height: 1.5; }
.input-bar { position: fixed; left: 0; right: 0; bottom: 0; display: flex; align-items: center; gap: 20rpx; padding: 20rpx 24rpx calc(20rpx + env(safe-area-inset-bottom)); background: #fff; border-top: 1rpx solid #eee; }
.chat-input { flex: 1; height: 80rpx; background: #f3f4f6; border-radius: 40rpx; padding: 0 28rpx; font-size: 26rpx; }
.send-btn { width: 160rpx; height: 80rpx; line-height: 80rpx; background: #ef4444; color: #fff; border-radius: 40rpx; font-size: 28rpx; }
.send-btn[disabled] { background: #fca5a5; }
</style>
