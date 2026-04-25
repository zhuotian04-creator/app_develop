<template>
	<view class="container" v-if="goods">
		<view class="status-bar"></view>
		<view class="nav-header">
			<text class="back-icon" @click="goBack">⬅️</text>
			<text class="nav-title">商品详情</text>
			<text class="share-icon">📤</text>
		</view>

		<scroll-view scroll-y class="detail-scroll">
			<swiper class="banner-swiper" indicator-dots autoplay>
				<swiper-item v-for="(img, index) in displayImages" :key="index">
					<image :src="img" mode="aspectFill" class="banner-img" @error="handleBannerError(index)"></image>
				</swiper-item>
			</swiper>

			<view class="info-card">
				<view class="price-section">
					<text class="currency">¥</text>
					<text class="price">{{goods.price}}</text>
					<text class="unit">/{{goods.type}}</text>
					<text v-if="goods.originalPrice" class="old-price">原价 ¥{{goods.originalPrice}}</text>
				</view>
				<text class="title">{{goods.title}}</text>
				<view class="tags-row">
					<text class="tag">{{goods.businessTypeText}}</text>
					<text class="tag">{{goods.statusText}}</text>
					<text class="tag">{{goods.isNew}}</text>
					<text class="tag">校内面交</text>
					<text class="tag">{{goods.tag}}</text>
				</view>
			</view>

			<view class="seller-card">
				<image class="seller-avatar" :src="sellerAvatarSrc" @error="handleSellerAvatarError"></image>
				<view class="seller-info">
					<text class="seller-name">{{goods.sellerName || '小黄同学'}}</text>
					<text class="seller-desc">{{goods.sellerDesc || '黄河科技学院 · 23级'}}</text>
				</view>
				<button class="follow-btn">关注</button>
			</view>

			<view class="detail-content">
				<view class="section-title">商品描述</view>
				<text class="desc-text">{{goods.desc}}</text>
			</view>
		</scroll-view>

		<view class="footer-bar">
			<view class="footer-left">
				<view class="action-item"><text class="action-icon">❤️</text><text>收藏</text></view>
				<view class="action-item" @click="openChat"><text class="action-icon">💬</text><text>留言</text></view>
			</view>
			<button class="buy-btn" :disabled="isActionDisabled || actionLoading" @click="onPrimaryAction">{{actionLoading ? '处理中...' : goods.actionLabel}}</button>
		</view>
	</view>
</template>

<script>
import { getGoodsDetail, performGoodsAction, startGoodsConversation } from '@/api/secondhand.js'

const DEFAULT_PRODUCT_IMAGE = '/static/logo.png'
const DEFAULT_AVATAR = '/static/logo.png'

export default {
	data() {
		return {
			goods: null,
			actionLoading: false,
			sellerAvatarSrc: DEFAULT_AVATAR
		}
	},
	computed: {
		displayImages() {
			if (!this.goods) {
				return [DEFAULT_PRODUCT_IMAGE];
			}
			return Array.isArray(this.goods.images) && this.goods.images.length
				? this.goods.images
				: [this.goods.img || DEFAULT_PRODUCT_IMAGE];
		},
		isActionDisabled() {
			if (!this.goods) {
				return true;
			}
			return ['sold', 'returned'].includes(this.goods.status);
		}
	},
	async onLoad(options) {
		if (options.id) {
			try {
				const res = await getGoodsDetail(options.id);
				this.goods = res.data;
				this.sellerAvatarSrc = this.goods.sellerAvatar || DEFAULT_AVATAR;
			} catch (e) {
				uni.showToast({ title: '加载失败', icon: 'none' });
			}
		}
	},
	methods: {
		goBack() { uni.navigateBack(); },
		handleBannerError(index) {
			if (!this.goods) {
				return;
			}
			const nextImages = this.displayImages.slice();
			nextImages[index] = DEFAULT_PRODUCT_IMAGE;
			this.goods = {
				...this.goods,
				images: nextImages
			};
		},
		handleSellerAvatarError() {
			this.sellerAvatarSrc = DEFAULT_AVATAR;
		},
		async openChat() {
			if (!this.goods) {
				return;
			}
			try {
				const res = await startGoodsConversation(this.goods.id);
				uni.navigateTo({ url: `/pages/secondhand/chat/chat?id=${res.conversation.id}` });
			} catch (error) {
				uni.showToast({ title: '打开聊天失败', icon: 'none' });
			}
		},
		async onPrimaryAction() {
			if (!this.goods || this.isActionDisabled) {
				return;
			}
			this.actionLoading = true;
			const actionType = this.goods.status === 'available'
				? (this.goods.businessType === 'trade' ? 'buy' : 'rent')
				: 'chat';
			try {
				const res = await performGoodsAction(this.goods.id, actionType);
				this.goods = res.product;
				uni.showToast({ title: res.notice || '操作成功', icon: 'none' });
				setTimeout(() => {
					uni.navigateTo({ url: `/pages/secondhand/chat/chat?id=${res.conversation.id}` });
				}, 300);
			} catch (error) {
				uni.showToast({ title: '操作失败', icon: 'none' });
			} finally {
				this.actionLoading = false;
			}
		}
	}
}
</script>

<style>
/* 样式保持不变 */
.container { background: #f8f8f8; min-height: 100vh; padding-bottom: 120rpx; }
.status-bar { height: var(--status-bar-height); background: #fff; }
.nav-header { height: 88rpx; background: #fff; display: flex; align-items: center; justify-content: space-between; padding: 0 30rpx; border-bottom: 1rpx solid #eee; }
.nav-title { font-weight: bold; font-size: 32rpx; }
.banner-swiper { height: 750rpx; }
.banner-img { width: 100%; height: 100%; }
.info-card { background: #fff; padding: 30rpx; margin-bottom: 20rpx; }
.price-section { margin-bottom: 20rpx; }
.price { font-size: 48rpx; color: #ef4444; font-weight: bold; }
.currency { color: #ef4444; font-size: 28rpx; }
.unit { color: #999; font-size: 24rpx; }
.old-price { color: #999; font-size: 24rpx; text-decoration: line-through; margin-left: 20rpx; }
.title { font-size: 34rpx; font-weight: bold; color: #333; line-height: 1.4; }
.tags-row { display: flex; gap: 20rpx; margin-top: 20rpx; }
.tag { font-size: 22rpx; background: #f3f4f6; color: #666; padding: 4rpx 16rpx; border-radius: 6rpx; }
.seller-card { background: #fff; padding: 30rpx; display: flex; align-items: center; margin-bottom: 20rpx; }
.seller-avatar { width: 80rpx; height: 80rpx; border-radius: 40rpx; margin-right: 20rpx; }
.seller-info { flex: 1; }
.seller-name { font-size: 28rpx; font-weight: bold; color: #333; display: block; }
.seller-desc { font-size: 22rpx; color: #999; }
.follow-btn { width: 120rpx; height: 50rpx; line-height: 50rpx; font-size: 24rpx; border: 1rpx solid #ef4444; color: #ef4444; background: #fff; border-radius: 100rpx; padding: 0; }
.detail-content { background: #fff; padding: 30rpx; }
.section-title { font-weight: bold; margin-bottom: 20rpx; font-size: 30rpx; border-left: 8rpx solid #ef4444; padding-left: 20rpx; }
.desc-text { font-size: 28rpx; color: #666; line-height: 1.6; }
.footer-bar { position: fixed; bottom: 0; left: 0; right: 0; height: 110rpx; background: #fff; border-top: 1rpx solid #eee; display: flex; align-items: center; padding: 0 30rpx; padding-bottom: env(safe-area-inset-bottom); }
.footer-left { display: flex; gap: 50rpx; margin-right: 40rpx; }
.action-item { display: flex; flex-direction: column; align-items: center; font-size: 20rpx; color: #666; }
.action-icon { font-size: 40rpx; margin-bottom: 4rpx; }
.buy-btn { flex: 1; background: #ef4444; color: #fff; border-radius: 100rpx; height: 80rpx; line-height: 80rpx; font-weight: bold; font-size: 30rpx; }
</style>
