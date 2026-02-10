// app.js
App({
  globalData: {
    userInfo: null,
    token: null,
    apiBaseUrl: 'http://localhost:8000' // 后端API基础地址
  },

  onLaunch() {
    // 初始化时检查本地存储的token
    const token = wx.getStorageSync('token');
    const userInfo = wx.getStorageSync('userInfo');
    
    if (token && userInfo) {
      this.globalData.token = token;
      this.globalData.userInfo = userInfo;
      console.log('已登录，用户信息:', userInfo);
    } else {
      console.log('未登录，跳转到登录页面');
      // 跳转到登录页面
      wx.navigateTo({
        url: '/pages/login/login'
      });
    }
  },

  // 登录方法
  login(phone, code, callback) {
    const that = this;
    wx.request({
      url: this.globalData.apiBaseUrl + '/api/auth/login',
      method: 'POST',
      data: {
        phone: phone,
        code: code
      },
      success(res) {
        if (res.data.code === 0) {
          // 登录成功，保存token和用户信息
          that.globalData.token = res.data.token;
          that.globalData.userInfo = res.data.user;
          wx.setStorageSync('token', res.data.token);
          wx.setStorageSync('userInfo', res.data.user);
          callback && callback(true, res.data);
        } else {
          callback && callback(false, res.data);
        }
      },
      fail(err) {
        callback && callback(false, err);
      }
    });
  },

  // 发送验证码
  sendCode(phone, callback) {
    wx.request({
      url: this.globalData.apiBaseUrl + '/api/auth/send_code',
      method: 'POST',
      data: {
        phone: phone
      },
      success(res) {
        if (res.data.code === 0) {
          callback && callback(true, res.data);
        } else {
          callback && callback(false, res.data);
        }
      },
      fail(err) {
        callback && callback(false, err);
      }
    });
  },

  // 退出登录
  logout() {
    this.globalData.token = null;
    this.globalData.userInfo = null;
    wx.removeStorageSync('token');
    wx.removeStorageSync('userInfo');
    wx.navigateTo({
      url: '/pages/login/login'
    });
  }
});
