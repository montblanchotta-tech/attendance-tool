/**
 * シンプルなアプリケーション（テスト用）
 */

// グローバル変数
let currentUser = null;
const API_BASE_URL = 'http://localhost:8001';

// 初期化
document.addEventListener('DOMContentLoaded', function() {
    console.log('アプリケーション初期化開始');
    
    // 既存のトークンをチェック
    const token = localStorage.getItem('access_token');
    const user = localStorage.getItem('user');
    
    if (token && user) {
        currentUser = JSON.parse(user);
        showMainPage();
    } else {
        showLoginPage();
    }
    
    // イベントリスナー設定
    setupEventListeners();
    
    console.log('アプリケーション初期化完了');
});

// ページ表示制御
function showLoginPage() {
    document.querySelectorAll('.page').forEach(page => page.classList.remove('active'));
    document.getElementById('login-page').classList.add('active');
}

function showMainPage() {
    document.querySelectorAll('.page').forEach(page => page.classList.remove('active'));
    document.getElementById('main-page').classList.add('active');
    
    if (currentUser) {
        document.getElementById('user-name').textContent = currentUser.full_name;
    }
}

// イベントリスナー設定
function setupEventListeners() {
    // ログインフォーム
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    
    // ログアウトボタン
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', handleLogout);
    }
}

// ログイン処理
async function handleLogin(event) {
    event.preventDefault();
    console.log('ログイン処理開始');
    
    const formData = new FormData(event.target);
    const loginData = {
        username: formData.get('username'),
        password: formData.get('password')
    };
    
    console.log('ログインデータ:', loginData);

    try {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(loginData)
        });

        console.log('APIレスポンス:', response);

        if (response.ok) {
            const data = await response.json();
            console.log('ログイン成功:', data);
            
            // トークンとユーザー情報を保存
            localStorage.setItem('access_token', data.access_token);
            localStorage.setItem('user', JSON.stringify(data.user));
            currentUser = data.user;
            
            // メインページに移動
            showMainPage();
            
            // 成功メッセージ
            alert('ログインに成功しました');
        } else {
            const error = await response.json();
            console.error('ログインエラー:', error);
            alert('ログインに失敗しました: ' + (error.detail || 'エラーが発生しました'));
        }
    } catch (error) {
        console.error('ネットワークエラー:', error);
        alert('ネットワークエラーが発生しました: ' + error.message);
    }
}

// ログアウト処理
function handleLogout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    currentUser = null;
    showLoginPage();
    alert('ログアウトしました');
}

console.log('simple-app.js読み込み完了');