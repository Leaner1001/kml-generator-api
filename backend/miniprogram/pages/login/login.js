// login.js
const app = getApp();
const { validatePhone, validateCode } = require('../../utils/auth');
const { api } = require('../../utils/api');

Page({
  data: {
    phone: '',
    code: '',
    countdown: 0,
    loading: false,
    errors: {}
  },

  // 手机号输入
  bindPhoneInput(e) {
    this.setData({
      phone: e.detail.value,
      'errors.phone': ''
    });
  },

  // 验证码输入
  bindCodeInput(e) {
    this.setData({
      code: e.detail.value,
      'errors.code': ''
    });
  },

  // 发送验证码
  sendCode() {
    const { phone } = this.data;
    const errors = {};

    // 验证手机号
    if (!phone) {
      errors.phone = '请输入手机号';
    } else if (!validatePhone(phone)) {
      errors.phone = '手机号格式错误';
    }

    if (Object.keys(errors).length > 0) {
      this.setData({ errors });
      return;
    }

    // 发送验证码
    wx.showLoading({ title: '发送中...' });
    api.auth.sendCode(phone)
      .then(res => {
        wx.hideLoading();
        wx.showToast({ title: '验证码发送成功', icon: 'success' });
        // 开始倒计时
        this.startCountdown();
      })
      .catch(err => {
        wx.hideLoading();
        wx.showToast({ title: err.message || '发送失败', icon: 'none' });
      });
  },

  // 倒计时
  startCountdown() {
    let countdown = 60;
    this.setData({ countdown });

    const timer = setInterval(() => {
      countdown--;
      this.setData({ countdown });

      if (countdown <= 0) {
        clearInterval(timer);
      }
    }, 1000);
  },

  // 登录
  login() {
    const { phone, code } = this.data;
    const errors = {};

    // 验证手机号
    if (!phone) {
      errors.phone = '请输入手机号';
    } else if (!validatePhone(phone)) {
      errors.phone = '手机号格式错误';
    }

    // 验证验证码
    if (!code) {
      errors.code = '请输入验证码';
    } else if (!validateCode(code)) {
      errors.code = '验证码格式错误';
    }

    if (Object.keys(errors).length > 0) {
      this.setData({ errors });
      return;
    }

    // 登录
    this.setData({ loading: true });
    api.auth.login(phone, code)
      .then(res => {
        this.setData({ loading: false });
        wx.showToast({ title: '登录成功', icon: 'success' });
        // 跳转到首页
        wx.switchTab({
          url: '/pages/index/index'
        });
      })
      .catch(err => {
        this.setData({ loading: false });
        wx.showToast({ title: err.message || '登录失败', icon: 'none' });
      });
  }
});
