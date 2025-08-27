/**
 * 認証関連のモジュール
 */
import CONFIG from '../config.js';
import { showPage, showMessage } from '../utils.js';

class AuthManager {
    constructor() {
        this.currentUser = null;
    }

    // ユーザー情報を取得
    getCurrentUser() {
        return this.currentUser;
    }

    // ユーザー情報を設定
    setCurrentUser(user) {
        this.currentUser = user;
        localStorage.setItem(CONFIG.USER_KEY, JSON.stringify(user));
    }

    // トークンを保存
    saveToken(token) {
        localStorage.setItem(CONFIG.TOKEN_KEY, token);
    }

    // トークンを取得
    getToken() {
        return localStorage.getItem(CONFIG.TOKEN_KEY);
    }

    // 認証ヘッダーを取得
    getAuthHeaders() {
        const token = this.getToken();
        if (!token) return {};
        
        return {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        };
    }

    // ログイン処理
    async handleLogin(event) {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        const loginData = {
            username: formData.get('username'),
            password: formData.get('password')
        };

        try {
            const response = await fetch(`${CONFIG.API_BASE_URL}/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(loginData)
            });

            if (response.ok) {
                const data = await response.json();
                this.saveToken(data.access_token);
                this.setCurrentUser(data.user);
                
                showMessage('ログインに成功しました');
                showPage('main-page');
                
                // メインページの初期化をイベント発火で通知
                window.dispatchEvent(new CustomEvent('userLogin', { detail: data.user }));
            } else {
                const error = await response.json();
                showMessage(error.detail || 'ログインに失敗しました', 'error');
            }
        } catch (error) {
            console.error('Login error:', error);
            showMessage('ネットワークエラーが発生しました', 'error');
        }
    }

    // ユーザー登録処理
    async handleRegister(event) {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        const password = formData.get('password');
        const confirmPassword = formData.get('confirm_password');

        if (password !== confirmPassword) {
            showMessage('パスワードが一致しません', 'error');
            return;
        }

        const registerData = {
            username: formData.get('username'),
            email: formData.get('email'),
            password: password,
            full_name: formData.get('full_name')
        };

        try {
            const response = await fetch(`${CONFIG.API_BASE_URL}/auth/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(registerData)
            });

            if (response.ok) {
                showMessage('ユーザー登録が完了しました。ログインしてください。');
                showPage('login-page');
                event.target.reset();
            } else {
                const error = await response.json();
                showMessage(error.detail || 'ユーザー登録に失敗しました', 'error');
            }
        } catch (error) {
            console.error('Register error:', error);
            showMessage('ネットワークエラーが発生しました', 'error');
        }
    }

    // ログアウト処理
    logout() {
        localStorage.removeItem(CONFIG.TOKEN_KEY);
        localStorage.removeItem(CONFIG.USER_KEY);
        this.currentUser = null;
        showPage('login-page');
        showMessage('ログアウトしました');
    }

    // 初期化時の認証チェック
    checkAuthentication() {
        const token = this.getToken();
        const user = localStorage.getItem(CONFIG.USER_KEY);
        
        if (token && user) {
            this.currentUser = JSON.parse(user);
            return true;
        }
        
        return false;
    }
}

export default new AuthManager();