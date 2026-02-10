// index.js
const app = getApp();

Page({
  data: {
    userInfo: null
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
    this.setData({
      userInfo: userInfo
    });
  },

  // 导航到上传页面
  navigateToUpload() {
    wx.navigateTo({
      url: '/pages/upload/upload'
    });
  },

  // 导航到配置页面
  navigateToConfig() {
    wx.navigateTo({
      url: '/pages/config/config'
    });
  },

  // 导航到历史页面
  navigateToHistory() {
    wx.navigateTo({
      url: '/pages/history/history'
    });
  },

  // 导航到用户页面
  navigateToUser() {
    wx.navigateTo({
      url: '/pages/user/user'
    });
  }
});
