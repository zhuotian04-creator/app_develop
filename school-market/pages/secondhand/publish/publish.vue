<template>
	<view class="container">
		<view class="status-bar"></view>
		<view class="page-title">发布</view>

		<view class="tab-header">
			<text class="tab-item" :class="{ active: businessType === 'trade' }" @click="switchBusinessType('trade')">二手交易</text>
			<text class="tab-item" :class="{ active: businessType === 'rental' }" @click="switchBusinessType('rental')">租赁</text>
		</view>

		<view class="content">
			<view class="steps-row">
				<view class="step">
					<view class="step-num active">1</view>
					<text class="step-txt">上传照片</text>
				</view>
				<view class="step-line"></view>
				<view class="step">
					<view class="step-num highlight">2</view>
					<text class="step-txt highlight">语音识别</text>
				</view>
				<view class="step-line"></view>
				<view class="step">
					<view class="step-num">3</view>
					<text class="step-txt">确认发布</text>
				</view>
			</view>

			<view class="upload-box" @click="uploadImg">
				<text class="camera-icon">📷</text>
				<text class="upload-tip">{{ uploadText }}</text>
			</view>

			<view class="ai-card">
				<view class="ai-header">
					<view class="ai-title-box">
						<text class="zap-icon">⚡</text>
						<text class="ai-title">智能发布助手</text>
					</view>
					<text class="ai-subtitle">说完后会自动识别并填充下方字段，也支持手动输入和修改</text>
				</view>

				<view class="voice-btn" :class="{ recording: isRecording }" @touchstart="startRecord" @touchend="endRecord">
					<text v-if="!isRecording" class="voice-icon">🎙️</text>
					<text v-else class="voice-icon animate-pulse">⭕</text>
					<text class="voice-text">{{ isRecording ? '正在录音，松手后自动识别' : '按住说话，描述品类、成色、使用月数、价格' }}</text>
				</view>

				<view class="edit-section">
					<view class="section-header">
						<text class="section-title">识别文字 / 手动输入</text>
						<text class="clear-btn" @click="clearTranscript">清空</text>
					</view>
					<textarea
						class="transcript-editor"
						v-model="transcript"
						placeholder="例如：我要卖一台联想小新笔记本，9成新，用了8个月，卖2600元，平时就写作业用。"
						maxlength="300"
					/>
					<button class="analyze-trigger-btn" :disabled="!transcript.trim() || isAnalyzing" @click="startAIAnalyze()">
						<text class="zap-icon-mini">⚡</text>
						{{ isAnalyzing ? '正在提取信息...' : '重新识别并自动填写' }}
					</button>
				</view>

				<view v-if="aiResult" class="result-box">
					<view class="ai-status-tag">请核对提取结果，可手动修改：</view>

					<view class="res-item">
						<text class="res-label">商品标题</text>
						<input class="res-input" v-model="aiResult.title" placeholder="请输入商品标题" />
					</view>

					<view class="res-row">
						<view class="res-item-half">
							<text class="res-label">分类</text>
							<picker @change="onCategoryChange" :range="categories" :value="categories.indexOf(aiResult.category)">
								<view class="picker-val">{{ aiResult.category || '请选择分类' }} ▽</view>
							</picker>
						</view>
						<view class="res-item-half">
							<text class="res-label">成色</text>
							<picker @change="onConditionChange" :range="conditions" :value="conditions.indexOf(aiResult.condition)">
								<view class="picker-val">{{ aiResult.condition || '请选择成色' }} ▽</view>
							</picker>
						</view>
					</view>

					<view class="res-row">
						<view class="res-item-half">
							<text class="res-label">{{ businessType === 'trade' ? '交易价格' : '日租金' }}</text>
							<view class="price-input-box">
								<input class="res-input price" type="digit" v-model="aiResult.priceValue" placeholder="输入价格" />
								<text class="unit-txt">/{{ aiResult.unit }}</text>
							</view>
						</view>
						<view class="res-item-half">
							<text class="res-label">使用时长（月）</text>
							<input class="res-input" type="number" v-model="aiResult.usedMonths" placeholder="例如 8" />
						</view>
					</view>

					<view class="res-item">
						<text class="res-label">商品描述</text>
						<textarea class="desc-editor" v-model="aiResult.description" placeholder="补充商品用途、配件、面交地点等信息" maxlength="500" />
					</view>
				</view>
			</view>
		</view>

		<button class="next-btn" :disabled="!canPublish || isSubmitting" @click="publishGoods">
			{{ isSubmitting ? '同步中...' : '确认无误，立即发布' }}
		</button>
	</view>
</template>

<script>
import { createGoods, uploadGoodsImage, analyzeGoodsText } from '@/api/secondhand.js'

let manager = null
try {
	var plugin = requirePlugin('WechatSI')
	manager = plugin.getRecordRecognitionManager()
} catch (e) {
	console.warn('微信同声传译插件未加载，将启用手动输入模式', e)
}

const DEFAULT_SELLER_AVATAR = ''

const createEmptyResult = (businessType = 'trade') => ({
	title: '',
	priceValue: '',
	category: '数码',
	condition: '9成新',
	usedMonths: '',
	unit: businessType === 'trade' ? '件' : '天',
	description: ''
})

export default {
	data() {
		return {
			businessType: 'trade',
			isRecording: false,
			transcript: '',
			aiResult: null,
			imageFiles: [],
			isSubmitting: false,
			isAnalyzing: false,
			categories: ['数码', '电动车', '二手书', '生活', '办公', '体育'],
			conditions: ['全新', '95新', '9成新', '8成新', '7成新', '6成新']
		}
	},
	onLoad() {
		if (manager) {
			this.initRecord()
		}
	},
	computed: {
		uploadText() {
			if (!this.imageFiles.length) return '上传照片，AI识别更精准'
			return `已选 ${this.imageFiles.length} 张，点击重选`
		},
		canPublish() {
			return !!(
				this.aiResult &&
				this.aiResult.title.trim() &&
				String(this.aiResult.priceValue).trim()
			)
		}
	},
	methods: {
		resetAiResult() {
			this.aiResult = createEmptyResult(this.businessType)
		},
		clearTranscript() {
			this.transcript = ''
			this.aiResult = null
		},
		initRecord() {
			manager.onRecognize = (res) => {
				this.transcript = (res.result || '').trim()
			}
			manager.onStop = async (res) => {
				this.transcript = (res.result || this.transcript || '').trim()
				this.isRecording = false
				uni.hideLoading()
				if (!this.transcript) {
					uni.showToast({ title: '未能识别文字', icon: 'none' })
					return
				}
				await this.startAIAnalyze({ auto: true })
			}
			manager.onError = () => {
				this.isRecording = false
				uni.hideLoading()
				uni.showToast({ title: '语音识别失败，请手动输入', icon: 'none' })
			}
		},
		startRecord() {
			if (!manager) {
				uni.showToast({ title: '插件不可用，请手动输入', icon: 'none' })
				return
			}
			this.isRecording = true
			this.transcript = ''
			this.aiResult = null
			uni.vibrateShort()
			manager.start({ duration: 30000, lang: 'zh_CN' })
			uni.showLoading({ title: '正在录音...' })
		},
		endRecord() {
			if (!this.isRecording) return
			this.isRecording = false
			if (manager) manager.stop()
		},
		async startAIAnalyze(options = {}) {
			const text = this.transcript.trim()
			if (!text || this.isAnalyzing) return
			this.isAnalyzing = true
			uni.showLoading({ title: options.auto ? '识别完成，正在填表...' : '正在提取信息...' })
			try {
				const res = await analyzeGoodsText(text, this.businessType)
				this.aiResult = {
					...createEmptyResult(this.businessType),
					...res,
					category: this.categories.includes(res.category) ? res.category : '数码',
					condition: this.conditions.includes(res.condition) ? res.condition : '9成新',
					unit: res.unit || (this.businessType === 'trade' ? '件' : '天'),
					usedMonths: String(res.usedMonths || '').trim()
				}
				uni.showToast({ title: options.auto ? '已自动填充' : '提取成功', icon: 'none' })
			} catch (e) {
				uni.showToast({ title: '提取失败，请手动填写', icon: 'none' })
			} finally {
				this.isAnalyzing = false
				uni.hideLoading()
			}
		},
		onCategoryChange(e) {
			this.aiResult.category = this.categories[e.detail.value]
		},
		onConditionChange(e) {
			this.aiResult.condition = this.conditions[e.detail.value]
		},
		switchBusinessType(type) {
			if (this.businessType === type) return
			this.businessType = type
			this.transcript = ''
			this.aiResult = null
			this.imageFiles = []
		},
		uploadImg() {
			uni.chooseImage({
				count: 9,
				success: (res) => {
					this.imageFiles = res.tempFilePaths || []
					uni.showToast({ title: '照片已上传', icon: 'none' })
				}
			})
		},
		buildConditionText() {
			if (!this.aiResult) return '9成新'
			if (this.aiResult.usedMonths) {
				return `${this.aiResult.condition} · 已用${this.aiResult.usedMonths}个月`
			}
			return this.aiResult.condition || '9成新'
		},
		buildDescription() {
			if (!this.aiResult) return ''
			const parts = []
			if (this.aiResult.description && this.aiResult.description.trim()) {
				parts.push(this.aiResult.description.trim())
			}
			if (this.aiResult.condition && !parts.join(' ').includes(this.aiResult.condition)) {
				parts.push(`成色：${this.aiResult.condition}`)
			}
			if (this.aiResult.usedMonths && !parts.join(' ').includes(`${this.aiResult.usedMonths}`)) {
				parts.push(`使用时长：约 ${this.aiResult.usedMonths} 个月`)
			}
			return parts.join('；')
		},
		async publishGoods() {
			if (!this.canPublish) return
			this.isSubmitting = true
			uni.showLoading({ title: '发布中...' })
			try {
				let imageUrls = []
				if (this.imageFiles.length > 0) {
					try {
						const uploadedUrl = await uploadGoodsImage(this.imageFiles[0])
						if (uploadedUrl) imageUrls.push(uploadedUrl)
					} catch (e) {
						console.error(e)
					}
				}
				if (imageUrls.length === 0) {
					imageUrls = [
						this.businessType === 'trade'
							? 'https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=800'
							: 'https://images.unsplash.com/photo-1620054702581-220f8c37107d?w=800'
					]
				}
				await createGoods({
					title: this.aiResult.title.trim(),
					price: parseFloat(this.aiResult.priceValue) || 0,
					unit: this.aiResult.unit,
					original_price: (parseFloat(this.aiResult.priceValue || 0) * 1.2 || 0).toFixed(2),
					tag: this.businessType === 'trade' ? '面交优先' : '信用免押',
					business_type: this.businessType,
					category: this.aiResult.category,
					img_url: imageUrls[0],
					image_urls: imageUrls,
					status: 'available',
					is_new: this.buildConditionText(),
					description: this.buildDescription(),
					seller_name: '小黄同学',
					seller_avatar: DEFAULT_SELLER_AVATAR,
					seller_desc: '黄河科技学院 · 23级'
				})
				uni.hideLoading()
				uni.showToast({ title: '发布成功', icon: 'success' })
				setTimeout(() => {
					uni.setStorageSync('homeBusinessType', this.businessType)
					uni.switchTab({ url: '/pages/secondhand/index/index' })
				}, 1200)
			} catch (error) {
				uni.hideLoading()
				uni.showModal({ title: '发布失败', content: '数据异常，请重试。', showCancel: false })
			} finally {
				this.isSubmitting = false
			}
		}
	}
}
</script>

<style>
.container { background-color: #f8f8f8; min-height: 100vh; padding-bottom: 220rpx; }
.status-bar { height: var(--status-bar-height); background: #fff; }
.page-title { text-align: center; font-weight: bold; padding: 30rpx; background: #fff; font-size: 34rpx; }
.tab-header { display: flex; justify-content: center; background: #fff; padding-bottom: 20rpx; border-bottom: 1rpx solid #f5f5f5; }
.tab-item { font-size: 30rpx; color: #999; margin: 0 40rpx; padding-bottom: 10rpx; position: relative; }
.tab-item.active { color: #ef4444; font-weight: bold; }
.tab-item.active::after { content: ''; position: absolute; bottom: 0; left: 20%; right: 20%; height: 4rpx; background: #ef4444; border-radius: 2rpx; }

.content { padding: 30rpx; }
.steps-row { display: flex; align-items: center; justify-content: center; margin-bottom: 30rpx; }
.step { display: flex; flex-direction: column; align-items: center; }
.step-num { width: 40rpx; height: 40rpx; border-radius: 50%; background: #eee; color: #999; font-size: 22rpx; display: flex; justify-content: center; align-items: center; margin-bottom: 8rpx; }
.step-num.active { background: #333; color: #fff; }
.step-num.highlight { background: #fee2e2; color: #ef4444; font-weight: bold; }
.step-txt { font-size: 20rpx; color: #999; }
.step-txt.highlight { color: #ef4444; }
.step-line { width: 60rpx; height: 2rpx; background: #eee; margin: 0 10rpx; margin-top: -30rpx; }

.upload-box { background: #fff; border: 2rpx dashed #ddd; border-radius: 24rpx; height: 200rpx; display: flex; flex-direction: column; justify-content: center; align-items: center; margin-bottom: 30rpx; }
.camera-icon { font-size: 50rpx; color: #999; margin-bottom: 10rpx; }
.upload-tip { color: #999; font-size: 24rpx; }

.ai-card { background: #fff; border-radius: 30rpx; padding: 30rpx; border: 1rpx solid #fee2e2; }
.ai-header { margin-bottom: 20rpx; }
.ai-title-box { display: flex; align-items: center; }
.ai-title { font-weight: bold; color: #333; font-size: 28rpx; }
.ai-subtitle { display: block; font-size: 22rpx; color: #888; margin-top: 12rpx; line-height: 1.5; }
.zap-icon { color: #ef4444; margin-right: 10rpx; }

.voice-btn { background: linear-gradient(135deg, #ef4444, #f43f5e); min-height: 140rpx; border-radius: 24rpx; display: flex; flex-direction: column; justify-content: center; align-items: center; color: #fff; box-shadow: 0 10rpx 20rpx rgba(239, 68, 68, 0.2); padding: 20rpx; text-align: center; }
.voice-btn.recording { background: #fff1f2; color: #ef4444; border: 4rpx solid #fecaca; box-shadow: none; }
.voice-icon { font-size: 48rpx; margin-bottom: 6rpx; }
.voice-text { font-size: 26rpx; font-weight: bold; line-height: 1.5; }

.edit-section { margin-top: 30rpx; background: #fdf2f2; padding: 20rpx; border-radius: 20rpx; }
.section-header { display: flex; justify-content: space-between; margin-bottom: 10rpx; }
.section-title { font-size: 22rpx; color: #ef4444; }
.clear-btn { font-size: 22rpx; color: #999; }
.transcript-editor { width: 100%; height: 180rpx; font-size: 28rpx; color: #333; line-height: 1.5; }
.analyze-trigger-btn { margin-top: 20rpx; background: #ef4444; color: #fff; font-size: 26rpx; height: 80rpx; line-height: 80rpx; border-radius: 40rpx; font-weight: bold; }
.analyze-trigger-btn[disabled] { background: #fca5a5; }

.result-box { margin-top: 30rpx; border-top: 2rpx dashed #eee; padding-top: 30rpx; }
.ai-status-tag { font-size: 22rpx; color: #ef4444; font-weight: bold; margin-bottom: 20rpx; }
.res-item { margin-bottom: 20rpx; }
.res-label { font-size: 22rpx; color: #999; display: block; margin-bottom: 8rpx; }
.res-input { background: #f9f9f9; padding: 15rpx 20rpx; border-radius: 12rpx; font-size: 28rpx; font-weight: bold; width: 100%; box-sizing: border-box; min-height: 88rpx; }
.res-row { display: flex; gap: 20rpx; margin-bottom: 20rpx; }
.res-item-half { flex: 1; }
.price-input-box { display: flex; align-items: center; background: #f9f9f9; border-radius: 12rpx; padding-right: 20rpx; }
.res-input.price { flex: 1; color: #ef4444; }
.unit-txt { font-size: 24rpx; color: #999; }
.picker-val { background: #f9f9f9; padding: 20rpx; border-radius: 12rpx; font-size: 28rpx; font-weight: bold; min-height: 88rpx; box-sizing: border-box; }
.desc-editor { width: 100%; min-height: 180rpx; background: #f9f9f9; padding: 20rpx; border-radius: 12rpx; font-size: 26rpx; line-height: 1.6; box-sizing: border-box; }

.next-btn { position: fixed; bottom: 40rpx; left: 40rpx; right: 40rpx; background: #ef4444; color: #fff; border-radius: 100rpx; height: 100rpx; line-height: 100rpx; font-weight: bold; z-index: 10; box-shadow: 0 10rpx 20rpx rgba(239, 68, 68, 0.2); }
.next-btn[disabled] { background: #fca5a5; }

@keyframes pulse { 0% { opacity: 1; transform: scale(1); } 50% { opacity: 0.6; transform: scale(1.05); } 100% { opacity: 1; transform: scale(1); } }
.animate-pulse { animation: pulse 1.5s infinite; }
</style>
