const express = require('express');
const cors = require('cors');
const app = express();
const port = 3000;

app.use(cors());
app.use(express.json());

// 模拟数据库
let products = [
    { id: 1, title: '九号 N70C 智能电动车', price: '28', type: '天', originalPrice: '3299', tag: '信用免押', img: 'https://images.unsplash.com/photo-1620054702581-220f8c37107d?w=400', images: ['https://images.unsplash.com/photo-1620054702581-220f8c37107d?w=800'], isNew: '9.5成新', desc: '校内通勤神器，续航50km+，支持手机开锁。' },
    { id: 2, title: '高等数学 第七版 上下册', price: '30', type: '本', tag: '8.5成新', img: 'https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=400', images: ['https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=800'], isNew: '8.5成新', desc: '期末复习神器，有少量笔记。' },
    { id: 3, title: '大疆 Mini 3 Pro', price: '60', type: '天', tag: '免押金', img: 'https://images.unsplash.com/photo-1579829366248-204fe8413f31?w=400', images: ['https://images.unsplash.com/photo-1579829366248-204fe8413f31?w=800'], isNew: '9成新', desc: '带屏遥控器版，校内航拍首选。' },
    { id: 4, title: '联想拯救者 R9000P', price: '45', type: '天', tag: '减免¥150', img: 'https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=400', images: ['https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=800'], isNew: '9成新', desc: '配置：R7-5800H/RTX3060/16G/512G，成色极好。' }
];

// 获取列表
app.get('/api/goods', (req, res) => {
    const { keyword } = req.query;
    let list = [...products];
    if (keyword) {
        list = list.filter(p => p.title.includes(keyword) || p.desc.includes(keyword));
    }
    res.json({ code: 200, data: list });
});

// 获取详情
app.get('/api/goods/:id', (req, res) => {
    const product = products.find(p => p.id == req.params.id);
    if (product) {
        res.json({ code: 200, data: product });
    } else {
        res.status(404).json({ code: 404, message: '商品不存在' });
    }
});

// 发布商品
app.post('/api/goods', (req, res) => {
    const newProduct = {
        id: products.length + 1,
        ...req.body,
        img: 'https://images.unsplash.com/photo-1581235720704-06d3acfcb36f?w=400', // 默认占位图
        images: ['https://images.unsplash.com/photo-1581235720704-06d3acfcb36f?w=800']
    };
    products.unshift(newProduct);
    res.json({ code: 200, data: newProduct });
});

app.listen(port, () => {
    console.log(`校园二手后端服务运行在 http://localhost:${port}`);
});
