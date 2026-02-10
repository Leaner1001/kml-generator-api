// upload.js
const app = getApp();
const { api } = require('../../utils/api');

Page({
  data: {
    selectedFile: null,
    layerType: '',
    uploading: false
  },

  // 选择文件
  chooseFile() {
    wx.chooseMessageFile({
      count: 1,
      type: 'file',
      extension: ['.xlsx', '.xls', '.csv'],
      success: (res) => {
        const file = res.tempFiles[0];
        
        // 验证文件大小
        if (file.size > 5 * 1024 * 1024) {
          wx.showToast({ title: '文件大小不超过5MB', icon: 'none' });
          return;
        }
        
        this.setData({
          selectedFile: file
        });
      },
      fail: (err) => {
        console.log('选择文件失败:', err);
      }
    });
  },

  // 删除文件
  deleteFile() {
    this.setData({
      selectedFile: null
    });
  },

  // 选择图层类型
  selectLayerType(e) {
    const type = e.currentTarget.dataset.type;
    this.setData({
      layerType: type
    });
  },

  // 格式化文件大小
  formatFileSize(size) {
    if (size < 1024) {
      return size + 'B';
    } else if (size < 1024 * 1024) {
      return (size / 1024).toFixed(2) + 'KB';
    } else {
      return (size / (1024 * 1024)).toFixed(2) + 'MB';
    }
  },

  // 上传文件
  uploadFile() {
    const { selectedFile, layerType } = this.data;
    
    if (!selectedFile) {
      wx.showToast({ title: '请选择文件', icon: 'none' });
      return;
    }
    
    if (!layerType) {
      wx.showToast({ title: '请选择图层类型', icon: 'none' });
      return;
    }
    
    this.setData({ uploading: true });
    
    // 上传文件
    api.upload.file(selectedFile.path)
      .then(res => {
        const fileId = res.file_id;
        // 生成KML
        return api.kml.generate(fileId, layerType, null);
      })
      .then(res => {
        this.setData({ uploading: false });
        wx.showToast({ title: '生成成功', icon: 'success' });
        
        // 跳转到历史页面查看
        wx.navigateTo({
          url: '/pages/history/history'
        });
      })
      .catch(err => {
        this.setData({ uploading: false });
        wx.showToast({ title: err.message || '操作失败', icon: 'none' });
      });
  }
});
