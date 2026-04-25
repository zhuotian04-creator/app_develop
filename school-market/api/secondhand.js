// 校园二手交易模块接口封装 (Django 后端版)
const BASE_URL = 'http://192.168.195.46:8000/api/secondhand';

const DEFAULT_AVATAR = '/static/logo.png';

const request = ({ url, method = 'GET', data = {} }) => {
	return new Promise((resolve, reject) => {
		uni.request({
			url: `${BASE_URL}${url}`,
			method,
			data,
			success: (res) => {
				if (res.statusCode >= 200 && res.statusCode < 300) {
					resolve(res.data);
					return;
				}
				reject(res.data || new Error(`Request failed with status ${res.statusCode}`));
			},
			fail: reject
		});
	});
};

const adaptProduct = (item) => ({
	id: item.id,
	title: item.title,
	price: item.price,
	type: item.unit,
	tag: item.tag,
	businessType: item.business_type,
	businessTypeText: item.business_type_text,
	status: item.status,
	statusText: item.status_text,
	actionLabel: item.action_label,
	category: item.category,
	img: item.img_url,
	isNew: item.is_new,
	desc: item.description,
	originalPrice: item.original_price,
	sellerName: item.seller_name,
	sellerAvatar: item.seller_avatar || DEFAULT_AVATAR,
	sellerDesc: item.seller_desc,
	images: Array.isArray(item.images) && item.images.length ? item.images : [item.img_url]
});

const adaptConversation = (item) => ({
	id: item.id,
	productId: item.product,
	productTitle: item.product_title,
	productImage: item.product_image,
	businessType: item.business_type,
	businessTypeText: item.business_type_text,
	status: item.status,
	statusText: item.status_text,
	title: item.title,
	name: item.participant_name,
	avatar: item.participant_avatar || DEFAULT_AVATAR,
	unread: item.unread_count,
	msg: item.last_message,
	time: item.last_message_at,
});

export const getGoodsList = async (keyword = '', category = '', businessType = '') => {
	const data = await request({
		url: '/products/',
		data: { keyword, category, business_type: businessType }
	});
	const list = Array.isArray(data) ? data : (data.results || []);
	return { data: list.map(adaptProduct) };
};

export const getGoodsDetail = async (id) => {
	const item = await request({ url: `/products/${id}/` });
	return { data: adaptProduct(item) };
};

export const uploadGoodsImage = (filePath) => {
	return new Promise((resolve, reject) => {
		uni.uploadFile({
			url: `${BASE_URL}/uploads/`,
			filePath,
			name: 'file',
			success: (res) => {
				try {
					const data = JSON.parse(res.data || '{}');
					if (res.statusCode >= 200 && res.statusCode < 300 && data.url) {
						resolve(data.url);
						return;
					}
					reject(data);
				} catch (error) {
					reject(error);
				}
			},
			fail: reject
		});
	});
};

export const createGoods = async (payload) => {
	const item = await request({
		url: '/products/',
		method: 'POST',
		data: {
			...payload,
			image_urls: Array.isArray(payload.image_urls) ? payload.image_urls.join('\n') : (payload.image_urls || '')
		}
	});
	return { data: adaptProduct(item) };
};

export const performGoodsAction = async (id, actionType) => {
	const data = await request({
		url: `/products/${id}/action/`,
		method: 'POST',
		data: { action_type: actionType }
	});
	return {
		notice: data.notice,
		product: adaptProduct(data.product),
		conversation: adaptConversation(data.conversation)
	};
};

export const startGoodsConversation = async (productId) => {
	const data = await request({
		url: '/messages/start/',
		method: 'POST',
		data: { product_id: productId }
	});
	return { conversation: adaptConversation(data.conversation) };
};

export const getMessages = async (businessType = '') => {
	const data = await request({
		url: '/messages/',
		data: { business_type: businessType }
	});
	return {
		stats: data.stats || { trade: 0, rental: 0, system: 0 },
		data: (data.results || []).map(adaptConversation)
	};
};

export const getConversationDetail = async (id) => {
	const data = await request({ url: `/messages/${id}/` });
	return {
		conversation: adaptConversation(data.conversation),
		messages: data.messages || []
	};
};

export const sendConversationMessage = async (id, content) => {
	const data = await request({
		url: `/messages/${id}/send/`,
		method: 'POST',
		data: { content }
	});
	return {
		conversation: adaptConversation(data.conversation),
		messages: data.messages || []
	};
};

export const getMyProfile = async () => {
	const data = await request({ url: '/profile/' });
	return { data };
};

export const analyzeGoodsText = async (text, businessType) => {
	const data = await request({
		url: '/ai-analyze/',
		method: 'POST',
		data: { text, business_type: businessType }
	});
	return data;
};
