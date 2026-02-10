// auth.js - 认证相关工具

// 验证手机号格式
function validatePhone(phone) {
  const phoneRegex = /^1[3-9]\d{9}$/;
  return phoneRegex.test(phone);
}

// 验证验证码格式
function validateCode(code) {
  const codeRegex = /^\d{6}$/;
  return codeRegex.test(code);
}

// 保存验证码到本地存储
function saveVerificationCode(phone, code) {
  const key = `verification_code_${phone}`;
  wx.setStorageSync(key, {
    code: code,
    timestamp: Date.now()
  });
}

// 获取验证码
function getVerificationCode(phone) {
  const key = `verification_code_${phone}`;
  const data = wx.getStorageSync(key);
  if (!data) return null;
  
  // 验证码5分钟内有效
  const now = Date.now();
  if (now - data.timestamp > 5 * 60 * 1000) {
    wx.removeStorageSync(key);
    return null;
  }
  
  return data.code;
}

// 清除验证码
function clearVerificationCode(phone) {
  const key = `verification_code_${phone}`;
  wx.removeStorageSync(key);
}

// 获取当前用户信息
function getCurrentUser() {
  return wx.getStorageSync('userInfo');
}

// 获取token
function getToken() {
  return wx.getStorageSync('token');
}

// 检查是否登录
function isLoggedIn() {
  const token = getToken();
  const userInfo = getCurrentUser();
  return !!token && !!userInfo;
}

module.exports = {
  validatePhone,
  validateCode,
  saveVerificationCode,
  getVerificationCode,
  clearVerificationCode,
  getCurrentUser,
  getToken,
  isLoggedIn
};
