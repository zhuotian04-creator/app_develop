<template>
	<view class="container">
		<!-- 用户头部 -->
		<view class="user-header">
			<view class="status-bar"></view>
			<view class="top-icons">
				<text>🔔</text>
				<text>⚙️</text>
			</view>
			<view class="user-info">
				<image class="avatar" :src="profile.avatar" mode="aspectFill" @error="handleAvatarError"></image>
				<view class="info-right">
					<text class="nickname">{{profile.nickname}}</text>
					<view class="tag-row">
						<text class="user-tag">学号 {{profile.studentId}}</text>
						<text class="user-tag verified">🛡️ {{profile.verifyStatus}}</text>
					</view>
				</view>
			</view>
		</view>

		<!-- 信用分卡片 -->
		<view class="credit-card">
			<view class="credit-left">
				<text class="credit-label">信用分 ❔</text>
				<view class="score-row">
					<text class="score-num">{{profile.creditScore}}</text>
					<text class="score-tag">{{profile.creditLevel}}</text>
				</view>
				<text class="credit-tip">{{profile.creditTip}}</text>
			</view>
			<view class="credit-right">
				<text>信用中心 ></text>
			</view>
		</view>

		<!-- 快捷入口 -->
		<view class="nav-row">
			<view class="nav-item" @click="goToPublished">
				<text class="nav-icon color-orange">📝</text>
				<text class="nav-label">我的发布</text>
				<text class="nav-sub">{{profile.published_count}} 件商品</text>
			</view>
			<view class="nav-item">
				<text class="nav-icon color-gray">❤️</text>
				<text class="nav-label">我的收藏</text>
				<text class="nav-sub">{{profile.favoriteCount}} 个收藏</text>
			</view>
		</view>

		<!-- 消息中心 (新) -->
		<view class="section">
			<view class="section-title">消息中心</view>
			<view class="message-card">
				<view class="msg-menu-item" @click="goToMessage('trade')">
					<view class="msg-menu-left">
						<view class="msg-icon-box bg-red">💬</view>
						<text class="msg-menu-label">交易消息</text>
					</view>
					<view class="msg-menu-right">
						<text class="msg-menu-sub">{{profile.tradeCount}} 个会话</text>
						<text class="arrow">></text>
					</view>
				</view>
				<view class="msg-menu-item" @click="goToMessage('rental')">
					<view class="msg-menu-left">
						<view class="msg-icon-box bg-blue">⚡</view>
						<text class="msg-menu-label">租赁消息</text>
					</view>
					<view class="msg-menu-right">
						<text class="msg-menu-sub">{{profile.rentalCount}} 个会话</text>
						<text class="arrow">></text>
					</view>
				</view>
				<view class="msg-menu-item" @click="goToMessage('')">
					<view class="msg-menu-left">
						<view class="msg-icon-box bg-gray">🔔</view>
						<text class="msg-menu-label">全部消息</text>
					</view>
					<view class="msg-menu-right">
						<text class="msg-menu-sub">{{profile.conversationCount}} 个通知</text>
						<text class="arrow">></text>
					</view>
				</view>
			</view>
		</view>

		<!-- 资产区 -->
		<view class="section">
			<view class="section-title">资产</view>
			<view class="asset-grid">
				<view class="asset-item">
					<view class="asset-icon bg-blue">🛡️</view>
					<view class="asset-info">
						<text class="asset-label">押金余额</text>
						<text class="asset-val">¥{{profile.depositBalance}}</text>
					</view>
				</view>
				<view class="asset-item">
					<view class="asset-icon bg-orange">🎫</view>
					<view class="asset-info">
						<text class="asset-label">聊天会话</text>
						<text class="asset-val">{{profile.conversationCount}} 个进行中</text>
					</view>
				</view>
			</view>
		</view>
	</view>
</template>

<script>
import { getMyProfile } from '@/api/secondhand.js'

const DEFAULT_AVATAR = '/static/logo.png'

export default {
	data() {
		return {
			profile: {
				avatar: DEFAULT_AVATAR,
				nickname: '小黄同学',
				studentId: '2023XXXX',
				verifyStatus: '已实名认证',
				creditScore: 682,
				creditLevel: '良好',
				creditTip: '信用优秀可享免押金特权',
				depositBalance: '1200.00',
				couponText: '3张可用',
				tradeCount: 0,
				rentalCount: 0,
				conversationCount: 0,
				published_count: 0,
				favoriteCount: 0
			}
		}
	},
	onShow() {
		this.loadProfile();
	},
	methods: {
		handleAvatarError() {
			this.profile.avatar = DEFAULT_AVATAR;
		},
		async loadProfile() {
			try {
				const res = await getMyProfile();
				this.profile = {
					...this.profile,
					...(res.data || {})
				};
			} catch (error) {
				uni.showToast({ title: '个人信息加载失败', icon: 'none' });
			}
		},
		goToMessage(type) {
			uni.setStorageSync('messageBusinessType', type);
			uni.switchTab({ url: '/pages/secondhand/message/message' });
		},
		goToPublished() {
			uni.setStorageSync('homeBusinessType', 'all');
			uni.switchTab({ url: '/pages/secondhand/index/index' });
		}
	}
}
</script>

<style>
.container { background-color: #f8f8f8; min-height: 100vh; }
.user-header { background: linear-gradient(to bottom, #ef4444, #f43f5e); padding: 0 40rpx 100rpx; border-bottom-left-radius: 60rpx; border-bottom-right-radius: 60rpx; }
.status-bar { height: var(--status-bar-height); }
.top-icons { display: flex; justify-content: flex-end; padding: 20rpx 0; color: #fff; font-size: 40rpx; gap: 30rpx; }
.user-info { display: flex; align-items: center; margin-top: 20rpx; }
.avatar { width: 120rpx; height: 120rpx; border-radius: 60rpx; border: 4rpx solid rgba(255,255,255,0.3); background: #eee; }
.info-right { margin-left: 30rpx; }
.nickname { color: #fff; font-size: 36rpx; font-weight: bold; }
.tag-row { display: flex; gap: 10rpx; margin-top: 10rpx; }
.user-tag { font-size: 20rpx; background: rgba(0,0,0,0.1); color: #fff; padding: 4rpx 12rpx; border-radius: 100rpx; }
.user-tag.verified { background: rgba(255,255,255,0.2); }

.credit-card { margin: -60rpx 30rpx 0; background: #fffaf5; border-radius: 24rpx; padding: 30rpx; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 4rpx 15rpx rgba(0,0,0,0.05); }
.credit-label { font-size: 24rpx; color: #666; }
.score-row { display: flex; align-items: baseline; margin: 10rpx 0; }
.score-num { font-size: 44rpx; font-weight: bold; color: #333; }
.score-tag { font-size: 20rpx; background: #f97316; color: #fff; padding: 2rpx 10rpx; border-radius: 6rpx; margin-left: 15rpx; }
.credit-tip { font-size: 22rpx; color: #999; }
.credit-right { font-size: 24rpx; color: #f97316; font-weight: 500; }

.nav-row { display: flex; justify-content: space-around; background: #fff; padding: 40rpx 0; margin-top: 20rpx; }
.nav-item { display: flex; flex-direction: column; align-items: center; }
.nav-icon { font-size: 48rpx; margin-bottom: 10rpx; }
.nav-label { font-size: 24rpx; color: #333; }
.nav-sub { font-size: 20rpx; color: #999; margin-top: 4rpx; }
.color-red { color: #ef4444; }
.color-blue { color: #3b82f6; }
.color-orange { color: #f97316; }
.color-gray { color: #999; }

.section { padding: 30rpx; }
.section-title { font-weight: bold; margin-bottom: 20rpx; font-size: 30rpx; }
.message-card { background: #fff; border-radius: 20rpx; padding: 10rpx 20rpx; }
.msg-menu-item { display: flex; justify-content: space-between; align-items: center; padding: 30rpx 10rpx; border-bottom: 1rpx solid #f5f5f5; }
.msg-menu-item:last-child { border-bottom: none; }
.msg-menu-left { display: flex; align-items: center; }
.msg-icon-box { width: 70rpx; height: 70rpx; border-radius: 20rpx; display: flex; justify-content: center; align-items: center; font-size: 36rpx; margin-right: 24rpx; }
.bg-red { background: #fef2f2; }
.bg-blue { background: #eff6ff; }
.bg-gray { background: #f9fafb; }
.msg-menu-label { font-size: 28rpx; color: #333; font-weight: 500; }
.msg-menu-right { display: flex; align-items: center; }
.msg-menu-sub { font-size: 24rpx; color: #999; margin-right: 10rpx; }
.arrow { color: #ccc; font-size: 24rpx; }

.asset-grid { display: flex; gap: 20rpx; }
.asset-item { flex: 1; background: #fff; padding: 24rpx; border-radius: 20rpx; display: flex; align-items: center; }
.asset-icon { width: 70rpx; height: 70rpx; border-radius: 50%; display: flex; justify-content: center; align-items: center; margin-right: 20rpx; font-size: 32rpx; }
.asset-info { display: flex; flex-direction: column; }
.asset-label { font-size: 22rpx; color: #999; }
.asset-val { font-size: 26rpx; font-weight: bold; color: #333; }
</style>
