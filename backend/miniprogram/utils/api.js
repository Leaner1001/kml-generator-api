// api.js - API调用封装
const app = getApp();

// 请求拦截器
function request(options) {
  const token = wx.getStorageSync('token');
  
  return new Promise((resolve, reject) => {
    wx.request({
      url: app.globalData.apiBaseUrl + options.url,
      method: options.method || 'GET',
      data: options.data || {},
      header: {
        'Content-Type': 'application/json',
        'Authorization': token ? 'Bearer ' + token : ''
      },
      success(res) {
        if (res.statusCode === 200) {
          if (res.data.code === 0) {
            resolve(res.data);
          } else {
            reject(res.data);
          }
        } else if (res.statusCode === 401) {
          // token过期，跳转到登录页面
          wx.removeStorageSync('token');
          wx.removeStorageSync('userInfo');
          app.globalData.token = null;
          app.globalData.userInfo = null;
          wx.navigateTo({
            url: '/pages/login/login'
          });
          reject({ code: 401, message: '登录已过期，请重新登录' });
        } else {
          reject({ code: res.statusCode, message: '网络请求失败' });
        }
      },
      fail(err) {
        reject({ code: 500, message: '网络请求失败' });
      }
    });
  });
}

// 上传文件
function uploadFile(options) {
  const token = wx.getStorageSync('token');
  
  return new Promise((resolve, reject) => {
    wx.uploadFile({
      url: app.globalData.apiBaseUrl + options.url,
      filePath: options.filePath,
      name: options.name || 'file',
      formData: options.formData || {},
      header: {
        'Authorization': token ? 'Bearer ' + token : ''
      },
      success(res) {
        const data = JSON.parse(res.data);
        if (res.statusCode === 200) {
          if (data.code === 0) {
            resolve(data);
          } else {
            reject(data);
          }
        } else if (res.statusCode === 401) {
          // token过期，跳转到登录页面
          wx.removeStorageSync('token');
          wx.removeStorageSync('userInfo');
          app.globalData.token = null;
          app.globalData.userInfo = null;
          wx.navigateTo({
            url: '/pages/login/login'
          });
          reject({ code: 401, message: '登录已过期，请重新登录' });
        } else {
          reject({ code: res.statusCode, message: '文件上传失败' });
        }
      },
      fail(err) {
        reject({ code: 500, message: '文件上传失败' });
      }
    });
  });
}

// 下载文件
function downloadFile(url, filePath) {
  return new Promise((resolve, reject) => {
    wx.downloadFile({
      url: app.globalData.apiBaseUrl + url,
      filePath: filePath,
      success(res) {
        if (res.statusCode === 200) {
          resolve(res);
        } else {
          reject({ code: res.statusCode, message: '文件下载失败' });
        }
      },
      fail(err) {
        reject({ code: 500, message: '文件下载失败' });
      }
    });
  });
}

// API接口
const api = {
  // 认证相关
  auth: {
    sendCode: (phone) => request({ url: '/api/auth/send_code', method: 'POST', data: { phone } }),
    login: (phone, code) => request({ url: '/api/auth/login', method: 'POST', data: { phone, code } })
  },
  
  // 用户相关
  user: {
    getProfile: () => request({ url: '/api/user/profile' }),
    updateProfile: (data) => request({ url: '/api/user/profile', method: 'PUT', data })
  },
  
  // 文件上传
  upload: {
    file: (filePath) => uploadFile({ url: '/api/upload/file', filePath })
  },
  
  // KML生成
  kml: {
    generate: (fileId, layerType, config) => request({ 
      url: '/api/kml/generate', 
      method: 'POST', 
      data: { file_id: fileId, layer_type: layerType, config: JSON.stringify(config) } 
    }),
    history: () => request({ url: '/api/kml/history' }),
    download: (filename) => app.globalData.apiBaseUrl + '/api/kml/download?filename=' + filename
  }
};

module.exports = {
  request,
  uploadFile,
  downloadFile,
  api
};
