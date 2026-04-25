<template>
	<view class="container">
		<view class="status-bar"></view>
		<view class="page-title">消息</view>
		
		<view class="msg-nav">
			<view class="nav-item" @click="selectBusinessType('trade')">
				<view class="nav-icon bg-red">💬<view v-if="stats.trade" class="badge">{{stats.trade}}</view></view>
				<text class="nav-label">交易消息</text>
			</view>
			<view class="nav-item" @click="selectBusinessType('rental')">
				<view class="nav-icon bg-blue">⚡<view v-if="stats.rental" class="badge">{{stats.rental}}</view></view>
				<text class="nav-label">租赁消息</text>
			</view>
			<view class="nav-item" @click="selectBusinessType('')">
				<view class="nav-icon bg-orange">🔔<view v-if="stats.system" class="badge">{{stats.system}}</view></view>
				<text class="nav-label">全部消息</text>
			</view>
		</view>

		<view class="msg-list">
			<view class="msg-item" v-for="msg in messages" :key="msg.id" @click="goToChat(msg)">
				<view class="avatar-box">
					<image v-if="isRemoteAvatar(msg.avatar)" class="avatar" :src="msg.avatar" @error="handleAvatarError(msg)"></image>
					<view v-else class="avatar-icon">{{msg.businessType === 'rental' ? '⚡' : '📦'}}</view>
					<view v-if="msg.unread" class="dot">{{msg.unread}}</view>
				</view>
				<view class="msg-info">
					<view class="msg-top">
						<text class="msg-name">{{msg.name}}</text>
						<text class="msg-time">{{formatTime(msg.time)}}</text>
					</view>
					<text class="msg-txt">[{{msg.businessTypeText}}] {{msg.msg}}</text>
				</view>
			</view>
		</view>
	</view>
</template>

<script>
import { getMessages } from '@/api/secondhand.js'

export default {
	data() {
		return {
			activeBusinessType: '',
			messages: [],
			stats: {
				trade: 0,
				rental: 0,
				system: 0
			}
		}
	},
	onShow() {
		this.applyMessageFilter();
		this.loadMessages();
	},
	methods: {
		applyMessageFilter() {
			const savedType = uni.getStorageSync('messageBusinessType');
			// 只有在明确设置了该缓存（包括空字符串）时才处理
			if (typeof savedType === 'string') {
				this.activeBusinessType = savedType;
				uni.removeStorageSync('messageBusinessType');
			}
		},
		selectBusinessType(type) {
			this.activeBusinessType = type;
			this.loadMessages();
		},
		isRemoteAvatar(value) {
			return /^https?:\/\//.test(value || '');
		},
		handleAvatarError(msg) {
			msg.avatar = '';
		},
		formatTime(value) {
			if (!value) {
				return '';
			}
			if (value.includes('T')) {
				return value.slice(5, 16).replace('T', ' ');
			}
			return value;
		},
		async loadMessages() {
			try {
				const res = await getMessages(this.activeBusinessType);
				this.messages = res.data || [];
				this.stats = res.stats || this.stats;
			} catch (error) {
				uni.showToast({ title: '消息加载失败', icon: 'none' });
			}
		},
		goToChat(msg) {
			uni.navigateTo({ url: `/pages/secondhand/chat/chat?id=${msg.id}` });
		}
	}
}
</script>

<style>
.container { background-color: #fff; min-height: 100vh; }
.status-bar { height: var(--status-bar-height); }
.page-title { text-align: center; font-weight: bold; padding: 30rpx; font-size: 34rpx; border-bottom: 1rpx solid #f5f5f5; }

.msg-nav { display: flex; justify-content: space-around; padding: 40rpx 0; border-bottom: 20rpx solid #f8f8f8; }
.nav-item { display: flex; flex-direction: column; align-items: center; }
.nav-icon { width: 100rpx; height: 100rpx; border-radius: 50%; display: flex; justify-content: center; align-items: center; font-size: 44rpx; margin-bottom: 15rpx; position: relative; }
.bg-red { background: #fef2f2; }
.bg-blue { background: #eff6ff; }
.bg-orange { background: #fff7ed; }
.badge { position: absolute; top: 0; right: 0; background: #ef4444; color: #fff; font-size: 20rpx; width: 32rpx; height: 32rpx; border-radius: 50%; display: flex; justify-content: center; align-items: center; border: 4rpx solid #fff; }
.nav-label { font-size: 24rpx; color: #666; }

.msg-list { padding: 0 30rpx; }
.msg-item { display: flex; align-items: center; padding: 30rpx 0; border-bottom: 1rpx solid #f5f5f5; }
.avatar-box { position: relative; width: 100rpx; height: 100rpx; margin-right: 20rpx; }
.avatar { width: 100%; height: 100%; border-radius: 50%; }
.avatar-icon { width: 100%; height: 100%; border-radius: 50%; background: #eee; display: flex; justify-content: center; align-items: center; font-size: 40rpx; }
.dot { position: absolute; top: 0; right: 0; min-width: 32rpx; height: 32rpx; padding: 0 8rpx; background: #ef4444; border-radius: 20rpx; border: 4rpx solid #fff; color: #fff; font-size: 18rpx; display: flex; align-items: center; justify-content: center; }

.msg-info { flex: 1; }
.msg-top { display: flex; justify-content: space-between; margin-bottom: 10rpx; }
.msg-name { font-size: 28rpx; font-weight: bold; color: #333; }
.msg-time { font-size: 22rpx; color: #999; }
.msg-txt { font-size: 24rpx; color: #999; display: block; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
</style>
