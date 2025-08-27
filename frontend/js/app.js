/**
 * メインアプリケーション
 */
import CONFIG from './config.js';
import { formatDate, formatDateJP, formatTime, showPage, showMessage } from './utils.js';
import authManager from './modules/auth.js';
import attendanceManager from './modules/attendance.js';
import correctionManager from './modules/correction.js';
import adminManager from './modules/admin.js';

class App {
    constructor() {
        this.init();
    }

    // アプリケーション初期化
    init() {
        this.setupEventListeners();
        this.initializeDateFilters();
        this.startTimers();
        
        // 認証チェック
        if (authManager.checkAuthentication()) {
            this.showMainPage();
        } else {
            showPage('login-page');
        }
    }

    // イベントリスナー設定
    setupEventListeners() {
        // ログイン・登録フォーム
        const loginForm = document.getElementById('login-form');
        if (loginForm) {
            loginForm.addEventListener('submit', (e) => authManager.handleLogin(e));
        }
        
        const registerForm = document.getElementById('register-form');
        if (registerForm) {
            registerForm.addEventListener('submit', (e) => authManager.handleRegister(e));
        }
        
        // 修正申請フォーム
        const correctionForm = document.getElementById('correction-request-form');
        if (correctionForm) {
            correctionForm.addEventListener('submit', (e) => correctionManager.submitCorrectionRequest(e));
        }
        
        // 管理者フォーム
        const editForm = document.getElementById('edit-form');
        if (editForm) {
            editForm.addEventListener('submit', (e) => adminManager.updateAttendanceRecord(e));
        }
        
        // ページ切り替え
        const showRegisterBtn = document.getElementById('show-register');
        if (showRegisterBtn) {
            showRegisterBtn.addEventListener('click', () => showPage('register-page'));
        }
        
        const showLoginBtn = document.getElementById('show-login');
        if (showLoginBtn) {
            showLoginBtn.addEventListener('click', () => showPage('login-page'));
        }
        
        const logoutBtn = document.getElementById('logout-btn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', () => authManager.logout());
        }
        
        // 管理者ページ
        const adminBtn = document.getElementById('admin-btn');
        if (adminBtn) {
            adminBtn.addEventListener('click', () => this.showAdminPage());
        }
        
        const backToMainBtn = document.getElementById('back-to-main');
        if (backToMainBtn) {
            backToMainBtn.addEventListener('click', () => this.showMainPage());
        }
        
        // フィルター更新
        const updateFilterBtn = document.getElementById('update-filter');
        if (updateFilterBtn) {
            updateFilterBtn.addEventListener('click', () => attendanceManager.loadAttendanceHistory());
        }
        
        const updateAdminFilterBtn = document.getElementById('update-admin-filter');
        if (updateAdminFilterBtn) {
            updateAdminFilterBtn.addEventListener('click', () => this.updateAdminFilter());
        }
        
        // 修正申請関連ボタン
        const newCorrectionBtn = document.getElementById('new-correction-btn');
        if (newCorrectionBtn) {
            newCorrectionBtn.addEventListener('click', () => correctionManager.openCorrectionRequestModal());
        }
        
        const closeCorrectionModalBtn = document.getElementById('close-correction-modal');
        if (closeCorrectionModalBtn) {
            closeCorrectionModalBtn.addEventListener('click', () => correctionManager.closeCorrectionRequestModal());
        }
        
        const cancelCorrectionBtn = document.getElementById('cancel-correction-btn');
        if (cancelCorrectionBtn) {
            cancelCorrectionBtn.addEventListener('click', () => correctionManager.closeCorrectionRequestModal());
        }
        
        // 承認関連ボタン
        const closeApprovalModalBtn = document.getElementById('close-approval-modal');
        if (closeApprovalModalBtn) {
            closeApprovalModalBtn.addEventListener('click', () => adminManager.closeApprovalModal());
        }
        
        const approveBtn = document.getElementById('approve-btn');
        if (approveBtn) {
            approveBtn.addEventListener('click', () => adminManager.processRequest('approved'));
        }
        
        const rejectBtn = document.getElementById('reject-btn');
        if (rejectBtn) {
            rejectBtn.addEventListener('click', () => adminManager.processRequest('rejected'));
        }
        
        const cancelApprovalBtn = document.getElementById('cancel-approval-btn');
        if (cancelApprovalBtn) {
            cancelApprovalBtn.addEventListener('click', () => adminManager.closeApprovalModal());
        }
        
        // モーダル外クリックで閉じる
        window.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                e.target.style.display = 'none';
            }
        });
        
        // ユーザーログイン後の処理
        window.addEventListener('userLogin', () => {
            this.showMainPage();
        });
    }

    // 日付フィルターの初期化
    initializeDateFilters() {
        const today = new Date();
        const oneMonthAgo = new Date(today.getFullYear(), today.getMonth() - 1, today.getDate());
        
        document.getElementById('start-date').value = formatDate(oneMonthAgo);
        document.getElementById('end-date').value = formatDate(today);
        document.getElementById('admin-start-date').value = formatDate(oneMonthAgo);
        document.getElementById('admin-end-date').value = formatDate(today);
    }

    // タイマー開始
    startTimers() {
        // 現在時刻更新
        this.updateCurrentTime();
        setInterval(() => this.updateCurrentTime(), 1000);
    }

    // 現在時刻更新
    updateCurrentTime() {
        const now = new Date();
        const dateElement = document.getElementById('current-date');
        const timeElement = document.getElementById('current-time');
        
        if (dateElement) dateElement.textContent = formatDateJP(now);
        if (timeElement) timeElement.textContent = formatTime(now);
    }

    // メインページ表示
    showMainPage() {
        const user = authManager.getCurrentUser();
        if (!user) {
            showPage('login-page');
            return;
        }

        showPage('main-page');
        document.getElementById('user-name').textContent = user.full_name;
        
        // 管理者ボタンの表示制御
        const adminBtn = document.getElementById('admin-btn');
        if (user.is_admin) {
            adminBtn.style.display = 'inline-flex';
        } else {
            adminBtn.style.display = 'none';
        }
        
        // データ読み込み
        attendanceManager.loadTodayAttendance();
        attendanceManager.loadAttendanceHistory();
        correctionManager.loadCorrectionRequests();
    }

    // 管理者ページ表示
    showAdminPage() {
        const user = authManager.getCurrentUser();
        if (!user || !user.is_admin) {
            showMessage('管理者権限が必要です', 'error');
            return;
        }

        showPage('admin-page');
        adminManager.loadAllUsers();
        adminManager.loadAdminCorrectionRequests();
    }

    // 管理者フィルター更新
    updateAdminFilter() {
        if (adminManager.selectedUserId) {
            adminManager.loadUserAttendance(adminManager.selectedUserId);
        }
    }
}

// グローバル関数（HTMLから直接呼び出すため）
window.openCorrectionRequestModal = () => correctionManager.openCorrectionRequestModal();
window.closeCorrectionRequestModal = () => correctionManager.closeCorrectionRequestModal();

// アプリケーション開始
document.addEventListener('DOMContentLoaded', () => {
    new App();
});