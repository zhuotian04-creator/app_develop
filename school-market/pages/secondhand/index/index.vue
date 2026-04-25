<template>
	<view class="container">
		<view class="header-box">
			<view class="status-bar"></view>
			<view class="header-content">
				<view class="location-box">
					<view class="avatar-mini">黄</view>
					<text class="location-text">黄河科技学院</text>
				</view>
				<view class="icon-bell">🔔</view>
			</view>
			
			<view class="search-bar">
				<text class="search-icon">🔍</text>
				<input class="search-input" v-model="keyword" confirm-type="search" @confirm="loadData" placeholder="搜索商品、租赁或问问校园助手..." />
				<view class="divider"></view>
				<text class="mic-icon">🎙️</text>
			</view>
		</view>

		<view class="grid-nav">
			<view class="nav-item" :class="{ active: activeBusinessType === 'trade' }" @click="filterType('trade')">
				<view class="nav-icon bg-orange">📦</view>
				<text class="nav-title">二手交易</text>
				<text class="nav-desc">省钱环保</text>
			</view>
			<view class="nav-item" :class="{ active: activeBusinessType === 'rental' }" @click="filterType('rental')">
				<view class="nav-icon bg-blue">⚡</view>
				<text class="nav-title">租赁专区</text>
				<text class="nav-desc">免押金更省心</text>
			</view>
			<view class="nav-item" @click="clearBusinessType">
				<view class="nav-icon bg-purple">🤖</view>
				<text class="nav-title">校园助手</text>
				<text class="nav-desc">查看全部</text>
			</view>
		</view>

		<scroll-view scroll-x class="category-scroll">
			<text v-for="cat in categories" :key="cat" :class="['cat-item', activeCat === cat ? 'active' : '']" @click="setCategory(cat)">{{cat}}</text>
		</scroll-view>

		<view class="product-grid">
			<sh-goods-card 
				v-for="item in displayProducts" 
				:key="item.id" 
				:goods="item"
				@click="goToDetail(item)"
			></sh-goods-card>
			<view v-if="displayProducts.length === 0" class="empty">暂无相关商品</view>
		</view>
	</view>
</template>

<script>
import shGoodsCard from '@/components/sh-goods-card/sh-goods-card.vue'
import { getGoodsList } from '@/api/secondhand.js'

export default {
	components: { shGoodsCard },
	data() {
		return {
			keyword: '',
			activeBusinessType: '',
			activeCat: '热门推荐',
			categories: ['热门推荐', '电动车', '二手书', '数码', '生活'],
			products: []
		}
	},
	onLoad() {
		this.applyExternalFilter();
		this.loadData();
	},
	onShow() {
		this.applyExternalFilter();
		this.loadData();
	},
	computed: {
		displayProducts() { return this.products; }
	},
	methods: {
		applyExternalFilter() {
			const savedType = uni.getStorageSync('homeBusinessType');
			if (savedType) {
				this.activeBusinessType = savedType === 'all' ? '' : savedType;
				uni.removeStorageSync('homeBusinessType');
			}
		},
		async loadData() {
			try {
				const category = this.activeCat === '热门推荐' ? '' : this.activeCat;
				const res = await getGoodsList(this.keyword, category, this.activeBusinessType);
				this.products = res.data || [];
			} catch (e) {
				uni.showToast({ title: '加载失败', icon: 'none' });
			}
		},
		filterType(type) {
			this.activeBusinessType = this.activeBusinessType === type ? '' : type;
			this.loadData();
		},
		clearBusinessType() {
			this.activeBusinessType = '';
			this.loadData();
		},
		setCategory(cat) {
			this.activeCat = cat;
			this.loadData();
		},
		goToDetail(goods) {
			uni.navigateTo({ url: `/pages/secondhand/detail/detail?id=${goods.id}` });
		}
	}
}
</script>

<style>
.container { background-color: #f8f8f8; min-height: 100vh; padding-bottom: 50rpx; }
.header-box { background: linear-gradient(to bottom, #ef4444, #f43f5e); border-bottom-left-radius: 60rpx; border-bottom-right-radius: 60rpx; padding: 0 30rpx 40rpx; }
.status-bar { height: var(--status-bar-height); }
.header-content { display: flex; justify-content: space-between; align-items: center; padding: 20rpx 0; }
.location-box { display: flex; align-items: center; background: rgba(0,0,0,0.1); padding: 10rpx 20rpx; border-radius: 100rpx; }
.avatar-mini { width: 40rpx; height: 40rpx; background: #fff; color: #ef4444; border-radius: 50%; display: flex; justify-content: center; align-items: center; font-size: 24rpx; font-weight: bold; margin-right: 15rpx; }
.location-text { color: #fff; font-size: 28rpx; font-weight: bold; }
.icon-bell { color: #fff; font-size: 36rpx; }
.search-bar { background: #fff; height: 80rpx; border-radius: 40rpx; display: flex; align-items: center; padding: 0 30rpx; margin-top: 20rpx; box-shadow: 0 4rpx 10rpx rgba(0,0,0,0.05); }
.search-icon { font-size: 28rpx; color: #999; margin-right: 15rpx; }
.search-input { flex: 1; font-size: 26rpx; color: #333; }
.divider { width: 1rpx; height: 30rpx; background: #eee; margin: 0 20rpx; }
.mic-icon { color: #ef4444; font-size: 32rpx; }
.grid-nav { display: flex; justify-content: space-between; padding: 0 30rpx; margin-top: -30rpx; }
.nav-item { width: 30%; background: #fff; border-radius: 24rpx; padding: 20rpx 10rpx; display: flex; flex-direction: column; align-items: center; box-shadow: 0 4rpx 10rpx rgba(0,0,0,0.05); }
.nav-item.active { outline: 3rpx solid #fecaca; }
.nav-icon { width: 80rpx; height: 80rpx; border-radius: 50%; display: flex; justify-content: center; align-items: center; font-size: 40rpx; margin-bottom: 10rpx; }
.bg-orange { background: #fff7ed; }
.bg-blue { background: #eff6ff; }
.bg-purple { background: #faf5ff; }
.nav-title { font-size: 26rpx; font-weight: bold; color: #333; }
.nav-desc { font-size: 20rpx; color: #999; margin-top: 4rpx; }
.category-scroll { white-space: nowrap; padding: 30rpx; }
.cat-item { font-size: 28rpx; color: #666; margin-right: 40rpx; padding-bottom: 10rpx; }
.cat-item.active { color: #333; font-weight: bold; border-bottom: 4rpx solid #ef4444; }
.product-grid { display: flex; flex-wrap: wrap; padding: 0 20rpx; justify-content: space-between; }
.empty { width: 100%; text-align: center; padding: 100rpx 0; color: #999; font-size: 28rpx; }
</style>
