<template>
	<view class="product-card" @click="$emit('click', goods)">
		<image class="product-img" :src="imageSrc" mode="aspectFill" @error="handleImageError"></image>
		<text class="tag-new">{{goods.isNew}}</text>
		<view class="product-info">
			<text class="product-title">{{goods.title}}</text>
			<view class="meta-row">
				<text class="tag-mode">{{goods.businessTypeText}}</text>
				<text class="tag-status">{{goods.statusText}}</text>
			</view>
			<view class="price-row">
				<view class="price-box">
					<text class="currency">¥</text>
					<text class="price">{{goods.price}}</text>
					<text class="unit">/{{goods.type || '起'}}</text>
				</view>
				<text class="tag-credit">{{goods.tag || goods.actionLabel}}</text>
			</view>
		</view>
	</view>
</template>

<script>
const DEFAULT_PRODUCT_IMAGE = '/static/logo.png'

export default {
	props: {
		goods: {
			type: Object,
			default: () => ({})
		}
	},
	data() {
		return {
			imageSrc: this.goods.img || DEFAULT_PRODUCT_IMAGE
		}
	},
	watch: {
		'goods.img': {
			immediate: true,
			handler(value) {
				this.imageSrc = value || DEFAULT_PRODUCT_IMAGE
			}
		}
	},
	methods: {
		handleImageError() {
			this.imageSrc = DEFAULT_PRODUCT_IMAGE
		}
	}
}
</script>

<style scoped>
.product-card { width: 345rpx; background: #fff; border-radius: 20rpx; overflow: hidden; margin-bottom: 20rpx; position: relative; box-shadow: 0 4rpx 10rpx rgba(0,0,0,0.02); }
.product-img { width: 100%; height: 345rpx; background: #eee; }
.tag-new { position: absolute; top: 310rpx; right: 10rpx; background: rgba(0,0,0,0.5); color: #fff; font-size: 20rpx; padding: 2rpx 10rpx; border-radius: 6rpx; }
.product-info { padding: 15rpx; }
.product-title { font-size: 26rpx; color: #333; line-height: 36rpx; height: 72rpx; display: -webkit-box; -webkit-box-orient: vertical; -webkit-line-clamp: 2; overflow: hidden; }
.meta-row { display: flex; gap: 10rpx; margin-top: 12rpx; }
.tag-mode, .tag-status { font-size: 20rpx; padding: 2rpx 10rpx; border-radius: 999rpx; }
.tag-mode { color: #ef4444; background: #fff1f2; }
.tag-status { color: #2563eb; background: #eff6ff; }
.price-row { display: flex; justify-content: space-between; align-items: flex-end; margin-top: 15rpx; }
.price { font-size: 32rpx; color: #ef4444; font-weight: bold; }
.currency, .unit { font-size: 22rpx; color: #ef4444; }
.unit { color: #999; font-weight: normal; margin-left: 4rpx; }
.tag-credit { font-size: 20rpx; color: #10b981; background: #f0fdf4; padding: 2rpx 8rpx; border-radius: 6rpx; border: 1rpx solid #d1fae5; }
</style>
