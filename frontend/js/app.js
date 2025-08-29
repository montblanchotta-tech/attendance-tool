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
        document.getElementById('login-form').addEventListener('submit', 
            (e) => authManager.handleLogin(e));
        document.getElementById('register-form').addEventListener('submit', 
            (e) => authManager.handleRegister(e));
        
        // 修正申請フォーム
        document.getElementById('correction-request-form').addEventListener('submit',
            (e) => correctionManager.submitCorrectionRequest(e));
        
        // 管理者フォーム
        document.getElementById('edit-form').addEventListener('submit',
            (e) => adminManager.updateAttendanceRecord(e));
        
        // ページ切り替え
        document.getElementById('show-register').addEventListener('click',
            () => showPage('register-page'));
        document.getElementById('show-login').addEventListener('click',
            () => showPage('login-page'));
        document.getElementById('logout-btn').addEventListener('click',
            () => authManager.logout());
        
        // 管理者ページ
        document.getElementById('admin-btn').addEventListener('click',
            () => this.showAdminPage());
        document.getElementById('back-to-main').addEventListener('click',
            () => this.showMainPage());
        
        // フィルター更新
        document.getElementById('update-filter').addEventListener('click',
            () => attendanceManager.loadAttendanceHistory());
        document.getElementById('update-admin-filter').addEventListener('click',
            () => this.updateAdminFilter());
        
        // モーダル閉じる
        document.querySelectorAll('.close').forEach(closeBtn => {
            closeBtn.addEventListener('click', (e) => {
                e.target.closest('.modal').style.display = 'none';
            });
        });
        
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
window.closeEditModal = () => adminManager.closeEditModal();
window.openApprovalModal = (id) => adminManager.openApprovalModal(id);
window.closeApprovalModal = () => adminManager.closeApprovalModal();
window.approveRequest = () => adminManager.processRequest('approved');
window.rejectRequest = () => adminManager.processRequest('rejected');

// アプリケーション開始
document.addEventListener('DOMContentLoaded', () => {
    new App();
});