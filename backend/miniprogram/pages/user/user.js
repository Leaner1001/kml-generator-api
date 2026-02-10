// user.js
const app = getApp();
const { api } = require('../../utils/api');

Page({
  data: {
    userInfo: {
      nickname: '',
      phone: '',
      avatar: ''
    }
  },

  onLoad() {
    this.loadUserInfo();
  },

  onShow() {
    this.loadUserInfo();
  },

  // 加载用户信息
  loadUserInfo() {
    const userInfo = wx.getStorageSync('userInfo');
    if (userInfo) {
      this.setData({
        userInfo: userInfo
      });
    } else {
      // 如果本地没有用户信息，从服务器获取
      api.user.getProfile()
        .then(res => {
          this.setData({
            userInfo: res.user
          });
          // 更新本地存储
          wx.setStorageSync('userInfo', res.user);
        })
        .catch(err => {
          console.log('获取用户信息失败:', err);
        });
    }
  },

  // 导航到配置页面
  navigateToConfig() {
    wx.navigateTo({
      url: '/pages/config/config'
    });
  },

  // 关于我们
  aboutUs() {
    wx.showModal({
      title: '关于我们',
      content: '图层生成工具 v1.0.0\n\n一款专业的KML图层生成工具，支持基站扇区、RSRP点、光交/机房等多种图层类型。\n\n© 2026 图层生成工具团队',
      showCancel: false
    });
  },

  // 意见反馈
  feedback() {
    wx.showModal({
      title: '意见反馈',
      content: '如有任何建议或问题，请发送邮件至：\nsupport@example.com',
      showCancel: false
    });
  },

  // 退出登录
  logout() {
    wx.showModal({
      title: '退出登录',
      content: '确定要退出登录吗？',
      success: (res) => {
        if (res.confirm) {
          // 调用app的logout方法
          app.logout();
        }
      }
    });
  }
});
