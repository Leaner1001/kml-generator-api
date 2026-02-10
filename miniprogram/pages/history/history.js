// history.js
const app = getApp();
const { api } = require('../../utils/api');

Page({
  data: {
    historyList: [],
    loading: true
  },

  onLoad() {
    this.loadHistory();
  },

  onShow() {
    this.loadHistory();
  },

  // 加载历史记录
  loadHistory() {
    this.setData({ loading: true });
    
    api.kml.history()
      .then(res => {
        this.setData({
          historyList: res.data,
          loading: false
        });
      })
      .catch(err => {
        this.setData({ loading: false });
        wx.showToast({ title: '加载失败', icon: 'none' });
      });
  },

  // 格式化时间
  formatTime(timeStr) {
    if (!timeStr) return '';
    
    const date = new Date(timeStr);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    
    return `${year}-${month}-${day} ${hours}:${minutes}`;
  },

  // 下载KML文件
  downloadKML(e) {
    const filename = e.currentTarget.dataset.filename;
    const url = api.kml.download(filename.split('=')[1]);
    
    wx.showLoading({ title: '下载中...' });
    
    wx.downloadFile({
      url: url,
      success: (res) => {
        wx.hideLoading();
        if (res.statusCode === 200) {
          wx.openDocument({
            filePath: res.tempFilePath,
            success: (res) => {
              console.log('打开文档成功');
            },
            fail: (err) => {
              console.log('打开文档失败:', err);
              wx.showToast({ title: '打开文件失败', icon: 'none' });
            }
          });
        } else {
          wx.showToast({ title: '下载失败', icon: 'none' });
        }
      },
      fail: (err) => {
        wx.hideLoading();
        wx.showToast({ title: '下载失败', icon: 'none' });
      }
    });
  },

  // 跳转到上传页面
  navigateToUpload() {
    wx.navigateTo({
      url: '/pages/upload/upload'
    });
  }
});
