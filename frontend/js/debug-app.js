/**
 * デバッグ用シンプルアプリケーション
 */

// グローバル変数
let currentUser = null;
// Vercel用のAPI URL設定
const API_BASE_URL = window.location.hostname === 'localhost' ? 
    'http://localhost:8001' : 
    `https://${window.location.hostname}/api`;

// 初期化
document.addEventListener('DOMContentLoaded', function() {
    console.log('デバッグアプリ初期化開始');
    
    // 既存のトークンをチェック
    const token = localStorage.getItem('access_token');
    const user = localStorage.getItem('user');
    
    if (token && user) {
        currentUser = JSON.parse(user);
        console.log('ログイン済みユーザー:', currentUser);
        showMainPage();
        loadTodayAttendance().then(() => {
            setupMainPageListeners();
            loadCorrectionRequests();
            loadAttendanceHistory();
        });
    } else {
        console.log('未ログインユーザー');
        showLoginPage();
        setupLoginListeners();
    }
    
    // デバッグ: DOM要素の存在確認
    console.log('show-register要素:', document.getElementById('show-register'));
    console.log('show-login要素:', document.getElementById('show-login'));
});

// ページ表示制御
function showLoginPage() {
    document.querySelectorAll('.page').forEach(page => page.classList.remove('active'));
    document.getElementById('login-page').classList.add('active');
}

function showRegisterPage() {
    document.querySelectorAll('.page').forEach(page => page.classList.remove('active'));
    document.getElementById('register-page').classList.add('active');
    setupRegisterListeners();
}

function showMainPage() {
    document.querySelectorAll('.page').forEach(page => page.classList.remove('active'));
    document.getElementById('main-page').classList.add('active');
    
    if (currentUser) {
        const userNameEl = document.getElementById('user-name');
        if (userNameEl) {
            userNameEl.textContent = currentUser.full_name;
        }
    }
}

// ログイン関連リスナー
function setupLoginListeners() {
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
        console.log('ログインフォームリスナー設定完了');
    }
    
    // 新規登録リンク
    const showRegisterLink = document.getElementById('show-register');
    console.log('新規登録リンク要素検索結果:', showRegisterLink);
    if (showRegisterLink) {
        showRegisterLink.addEventListener('click', (e) => {
            e.preventDefault();
            console.log('新規登録リンククリックされました');
            showRegisterPage();
        });
        console.log('新規登録リンクリスナー設定完了');
    } else {
        console.log('新規登録リンク要素が見つかりません');
    }
}

// メインページ関連リスナー
function setupMainPageListeners() {
    console.log('=== メインページリスナー設定開始 ===');
    console.log('DOM状態確認:');
    console.log('- clock-in-btn:', document.getElementById('clock-in-btn'));
    console.log('- clock-out-btn:', document.getElementById('clock-out-btn'));
    console.log('- break-start-btn:', document.getElementById('break-start-btn'));
    console.log('- break-end-btn:', document.getElementById('break-end-btn'));
    
    // ログアウトボタン
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', handleLogout);
        console.log('ログアウトボタンリスナー設定完了');
    }
    
    // 管理者メニューボタン
    const adminBtn = document.getElementById('admin-btn');
    if (adminBtn && currentUser && currentUser.is_admin) {
        adminBtn.style.display = 'inline-block';
        adminBtn.addEventListener('click', showAdminSection);
        console.log('管理者メニューボタンリスナー設定完了');
    }
    
    // 修正申請ボタン
    const newCorrectionBtn = document.getElementById('new-correction-btn');
    if (newCorrectionBtn) {
        newCorrectionBtn.addEventListener('click', showCorrectionModal);
        console.log('修正申請ボタンリスナー設定完了');
    }
    
    // モーダル関連
    const correctionModal = document.getElementById('correction-request-modal');
    const closeCorrectionModal = document.getElementById('close-correction-modal');
    const cancelCorrectionBtn = document.getElementById('cancel-correction-btn');
    
    if (closeCorrectionModal) {
        closeCorrectionModal.addEventListener('click', hideCorrectionModal);
    }
    if (cancelCorrectionBtn) {
        cancelCorrectionBtn.addEventListener('click', hideCorrectionModal);
    }
    
    // 修正申請フォーム
    const correctionForm = document.getElementById('correction-request-form');
    if (correctionForm) {
        correctionForm.addEventListener('submit', handleCorrectionRequest);
        console.log('修正申請フォームリスナー設定完了');
    }
    
    // 出勤ボタンに直接リスナーを設定
    const clockInBtn = document.getElementById('clock-in-btn');
    console.log('出勤ボタン要素詳細:', {
        element: clockInBtn,
        disabled: clockInBtn ? clockInBtn.disabled : 'N/A',
        style: clockInBtn ? clockInBtn.style.display : 'N/A',
        class: clockInBtn ? clockInBtn.className : 'N/A'
    });
    
    if (clockInBtn) {
        // 既存のリスナーを削除（重複防止）
        clockInBtn.replaceWith(clockInBtn.cloneNode(true));
        const newClockInBtn = document.getElementById('clock-in-btn');
        
        newClockInBtn.addEventListener('click', (e) => {
            console.log('出勤ボタンクリックイベント発火:', e);
            console.log('イベントターゲット:', e.target);
            recordAttendance('clock_in');
        });
        console.log('出勤ボタンリスナー設定完了（新しい要素）');
        
        // テスト用：直接クリックをシミュレート
        console.log('テスト用クリックシミュレーション実行...');
        setTimeout(() => {
            newClockInBtn.click();
        }, 1000);
        
    } else {
        console.log('出勤ボタン要素が見つかりません');
    }
    
    const clockOutBtn = document.getElementById('clock-out-btn');
    if (clockOutBtn) {
        clockOutBtn.addEventListener('click', () => recordAttendance('clock_out'));
        console.log('退勤ボタンリスナー設定完了');
    }
    
    const breakStartBtn = document.getElementById('break-start-btn');
    if (breakStartBtn) {
        breakStartBtn.addEventListener('click', () => recordAttendance('break_start'));
        console.log('休憩開始ボタンリスナー設定完了');
    }
    
    const breakEndBtn = document.getElementById('break-end-btn');
    if (breakEndBtn) {
        breakEndBtn.addEventListener('click', () => recordAttendance('break_end'));
        console.log('休憩終了ボタンリスナー設定完了');
    }
}

// 出勤ボタンクリック処理
function handleAttendanceClick(event) {
    console.log('出勤エリアクリック:', event.target);
    
    // ボタンかどうかチェック
    if (event.target.tagName === 'BUTTON') {
        const action = event.target.getAttribute('data-action');
        if (action) {
            console.log('出勤アクション実行:', action);
            recordAttendance(action);
        } else {
            console.log('data-action属性が見つかりません');
        }
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
    
    try {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(loginData)
        });

        if (response.ok) {
            const data = await response.json();
            console.log('ログイン成功:', data);
            
            localStorage.setItem('access_token', data.access_token);
            localStorage.setItem('user', JSON.stringify(data.user));
            currentUser = data.user;
            
            showMainPage();
            loadTodayAttendance().then(() => {
                setupMainPageListeners();
                loadCorrectionRequests();
                loadAttendanceHistory();
            });
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

// 今日の勤怠状況読み込み
async function loadTodayAttendance() {
    console.log('今日の勤怠状況読み込み開始');
    
    return new Promise(async (resolve) => {
    
    try {
        const response = await fetch(`${API_BASE_URL}/attendance/today`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            const data = await response.json();
            console.log('今日の勤怠データ:', data);
            displayTodayAttendance(data);
            resolve();
        } else {
            console.error('勤怠データ取得エラー:', response.status);
            resolve();
        }
    } catch (error) {
        console.error('勤怠データ取得ネットワークエラー:', error);
        resolve();
    }
    });
}

// 今日の勤怠状況表示
function displayTodayAttendance(data) {
    console.log('勤怠状況表示:', data);
    console.log('データ詳細分析:');
    console.log('- data.id:', data.id);
    console.log('- data.status:', data.status);
    console.log('- data.clock_in:', data.clock_in);
    console.log('- data.clock_out:', data.clock_out);
    console.log('- data.break_start:', data.break_start);
    console.log('- data.break_end:', data.break_end);
    
    // 状況テキストの更新
    const workStatus = document.getElementById('work-status');
    if (workStatus) {
        if (data.id === 0 || data.status === 'not_clocked_in') {
            workStatus.textContent = '未出勤';
            workStatus.className = 'work-status not-clocked';
        } else if (data.clock_out) {
            // 退勤済みの場合
            const clockOutTime = new Date(data.clock_out).toLocaleTimeString('ja-JP', {hour: '2-digit', minute: '2-digit'});
            workStatus.textContent = `退勤済み (${clockOutTime}まで) - 再出勤可能`;
            workStatus.className = 'work-status clocked-out';
        } else {
            let statusText = '出勤中';
            if (data.clock_in) {
                const clockInTime = new Date(data.clock_in).toLocaleTimeString('ja-JP', {hour: '2-digit', minute: '2-digit'});
                statusText += ` (${clockInTime}から)`;
            }
            
            if (data.break_start && !data.break_end) {
                const breakTime = new Date(data.break_start).toLocaleTimeString('ja-JP', {hour: '2-digit', minute: '2-digit'});
                statusText += ` - 休憩中 (${breakTime}から)`;
            }
            
            workStatus.textContent = statusText;
            workStatus.className = 'work-status clocked-in';
        }
    }
    
    // 現在時刻の更新
    updateCurrentTime();
    
    // ボタンの有効/無効化
    const clockInBtn = document.getElementById('clock-in-btn');
    const clockOutBtn = document.getElementById('clock-out-btn');
    const breakStartBtn = document.getElementById('break-start-btn');
    const breakEndBtn = document.getElementById('break-end-btn');
    
    if (data.id === 0 || data.status === 'not_clocked_in') {
        console.log('未出勤状態: 出勤ボタンのみ有効');
        if (clockInBtn) clockInBtn.disabled = false;
        if (clockOutBtn) clockOutBtn.disabled = true;
        if (breakStartBtn) breakStartBtn.disabled = true;
        if (breakEndBtn) breakEndBtn.disabled = true;
    } else {
        console.log('出勤済み状態: 関連ボタンを有効化');
        if (clockInBtn) clockInBtn.disabled = true;
        
        if (data.clock_out) {
            console.log('既に退勤済み - 再出勤可能にする');
            if (clockInBtn) clockInBtn.disabled = false; // 再出勤を許可
            if (clockOutBtn) clockOutBtn.disabled = true;
            if (breakStartBtn) breakStartBtn.disabled = true;
            if (breakEndBtn) breakEndBtn.disabled = true;
        } else {
            console.log('まだ退勤していない - 退勤ボタンを有効化');
            if (clockOutBtn) clockOutBtn.disabled = false;
            
            if (data.break_start && !data.break_end) {
                console.log('休憩中 - 休憩終了ボタンのみ有効');
                if (breakStartBtn) breakStartBtn.disabled = true;
                if (breakEndBtn) breakEndBtn.disabled = false;
            } else {
                console.log('休憩なしまたは休憩終了済み - 休憩開始ボタンを有効化（複数休憩対応）');
                if (breakStartBtn) breakStartBtn.disabled = false;
                if (breakEndBtn) breakEndBtn.disabled = true;
            }
        }
    }
    
    // 最終的なボタン状態をログ出力
    console.log('最終ボタン状態:');
    console.log('- 出勤:', clockInBtn ? !clockInBtn.disabled : 'N/A');
    console.log('- 退勤:', clockOutBtn ? !clockOutBtn.disabled : 'N/A');
    console.log('- 休憩開始:', breakStartBtn ? !breakStartBtn.disabled : 'N/A');
    console.log('- 休憩終了:', breakEndBtn ? !breakEndBtn.disabled : 'N/A');
}

// 勤怠記録
async function recordAttendance(action) {
    console.log('勤怠記録開始:', action);
    console.log('現在のユーザー:', currentUser);
    console.log('アクセストークン:', localStorage.getItem('access_token') ? '存在' : '存在しない');
    
    const notes = null; // メモ機能は一時的に無効化
    
    try {
        const response = await fetch(`${API_BASE_URL}/attendance/`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ action, notes })
        });

        console.log('勤怠記録レスポンス:', response);

        if (response.ok) {
            const data = await response.json();
            console.log('勤怠記録成功:', data);
            loadTodayAttendance(); // 再読み込み
            loadAttendanceHistory(); // 履歴も更新
        } else {
            const error = await response.json();
            console.error('勤怠記録エラー:', error);
            alert('記録に失敗しました: ' + (error.detail || 'エラーが発生しました'));
        }
    } catch (error) {
        console.error('勤怠記録ネットワークエラー:', error);
        alert('ネットワークエラーが発生しました: ' + error.message);
    }
}

// ログアウト処理
function handleLogout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    currentUser = null;
    showLoginPage();
    setupLoginListeners();
}

// 修正申請モーダル表示
function showCorrectionModal() {
    console.log('修正申請モーダル表示');
    const modal = document.getElementById('correction-request-modal');
    if (modal) {
        modal.style.display = 'block';
        
        // 現在の日付をデフォルトに設定
        const today = new Date().toISOString().split('T')[0];
        const dateInput = document.getElementById('request-date');
        if (dateInput) {
            dateInput.value = today;
        }
    }
}

// 修正申請モーダル非表示
function hideCorrectionModal() {
    console.log('修正申請モーダル非表示');
    const modal = document.getElementById('correction-request-modal');
    if (modal) {
        modal.style.display = 'none';
        
        // フォームリセット
        const form = document.getElementById('correction-request-form');
        if (form) {
            form.reset();
        }
    }
}

// 修正申請処理
async function handleCorrectionRequest(event) {
    event.preventDefault();
    console.log('修正申請処理開始');
    
    const formData = new FormData(event.target);
    const requestData = {
        attendance_record_id: null, // 新規作成の場合はnull
        requested_date: formData.get('request_date'),
        requested_clock_in: formData.get('request_clock_in'),
        requested_clock_out: formData.get('request_clock_out'),
        requested_break_start: formData.get('request_break_start'),
        requested_break_end: formData.get('request_break_end'),
        requested_notes: formData.get('request_notes'),
        reason: formData.get('request_reason')
    };
    
    try {
        const response = await fetch(`${API_BASE_URL}/correction-request/`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });

        if (response.ok) {
            const data = await response.json();
            console.log('修正申請成功:', data);
            alert('修正申請を送信しました');
            hideCorrectionModal();
            loadCorrectionRequests();
        } else {
            const error = await response.json();
            console.error('修正申請エラー:', error);
            alert('修正申請に失敗しました: ' + (error.detail || 'エラーが発生しました'));
        }
    } catch (error) {
        console.error('修正申請ネットワークエラー:', error);
        alert('ネットワークエラーが発生しました: ' + error.message);
    }
}

// 修正申請一覧読み込み
async function loadCorrectionRequests() {
    console.log('修正申請一覧読み込み開始');
    
    try {
        const response = await fetch(`${API_BASE_URL}/correction-request/`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            const requests = await response.json();
            console.log('修正申請データ:', requests);
            displayCorrectionRequests(requests);
        } else {
            console.error('修正申請データ取得エラー:', response.status);
        }
    } catch (error) {
        console.error('修正申請データ取得ネットワークエラー:', error);
    }
}

// 修正申請一覧表示
function displayCorrectionRequests(requests) {
    const table = document.getElementById('correction-requests-table');
    const tbody = table ? table.querySelector('tbody') : null;
    
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    if (requests.length === 0) {
        const row = tbody.insertRow();
        const cell = row.insertCell();
        cell.colSpan = 6;
        cell.textContent = '修正申請はありません';
        cell.style.textAlign = 'center';
        return;
    }
    
    requests.forEach(request => {
        const row = tbody.insertRow();
        
        // 申請日
        const dateCell = row.insertCell();
        dateCell.textContent = request.requested_date;
        
        // 申請内容（簡略）
        const contentCell = row.insertCell();
        const clockIn = request.requested_clock_in ? new Date(request.requested_clock_in).toLocaleTimeString('ja-JP', {hour: '2-digit', minute: '2-digit'}) : '-';
        const clockOut = request.requested_clock_out ? new Date(request.requested_clock_out).toLocaleTimeString('ja-JP', {hour: '2-digit', minute: '2-digit'}) : '-';
        contentCell.textContent = `${clockIn} - ${clockOut}`;
        
        // 理由
        const reasonCell = row.insertCell();
        reasonCell.textContent = request.reason;
        
        // ステータス
        const statusCell = row.insertCell();
        const statusText = request.status === 'pending' ? '承認待ち' : 
                          request.status === 'approved' ? '承認済み' : '却下';
        statusCell.textContent = statusText;
        statusCell.className = `status-${request.status}`;
        
        // 申請日時
        const createdCell = row.insertCell();
        createdCell.textContent = new Date(request.created_at).toLocaleDateString('ja-JP');
        
        // 管理者メモ
        const notesCell = row.insertCell();
        notesCell.textContent = request.admin_notes || '-';
    });
}

// 管理者ページ表示
function showAdminSection() {
    console.log('管理者ページ表示');
    document.querySelectorAll('.page').forEach(page => page.classList.remove('active'));
    const adminPage = document.getElementById('admin-page');
    if (adminPage) {
        adminPage.classList.add('active');
        setupAdminPageListeners();
        loadAllCorrectionRequests();
    }
}

// 管理者ページリスナー設定
function setupAdminPageListeners() {
    const backToMainBtn = document.getElementById('back-to-main');
    if (backToMainBtn) {
        backToMainBtn.addEventListener('click', () => {
            showMainPage();
            setupMainPageListeners();
        });
    }
}

// 全修正申請読み込み（管理者用）
async function loadAllCorrectionRequests() {
    console.log('全修正申請読み込み開始');
    
    try {
        const response = await fetch(`${API_BASE_URL}/correction-request/admin/all?status=pending`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            const requests = await response.json();
            console.log('全修正申請データ:', requests);
            displayAdminCorrectionRequests(requests);
        } else {
            console.error('全修正申請データ取得エラー:', response.status);
        }
    } catch (error) {
        console.error('全修正申請データ取得ネットワークエラー:', error);
    }
}

// 管理者用修正申請一覧表示
function displayAdminCorrectionRequests(requests) {
    const table = document.getElementById('admin-correction-requests-table');
    const tbody = table ? table.querySelector('tbody') : null;
    
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    if (requests.length === 0) {
        const row = tbody.insertRow();
        const cell = row.insertCell();
        cell.colSpan = 7;
        cell.textContent = '承認待ちの修正申請はありません';
        cell.style.textAlign = 'center';
        return;
    }
    
    requests.forEach(request => {
        const row = tbody.insertRow();
        
        // ユーザー名（仮）
        const userCell = row.insertCell();
        userCell.textContent = `ユーザーID: ${request.user_id}`;
        
        // 申請日
        const dateCell = row.insertCell();
        dateCell.textContent = request.requested_date;
        
        // 申請内容
        const contentCell = row.insertCell();
        const clockIn = request.requested_clock_in ? new Date(request.requested_clock_in).toLocaleTimeString('ja-JP', {hour: '2-digit', minute: '2-digit'}) : '-';
        const clockOut = request.requested_clock_out ? new Date(request.requested_clock_out).toLocaleTimeString('ja-JP', {hour: '2-digit', minute: '2-digit'}) : '-';
        contentCell.textContent = `${clockIn} - ${clockOut}`;
        
        // 理由
        const reasonCell = row.insertCell();
        reasonCell.textContent = request.reason;
        
        // 申請日時
        const createdCell = row.insertCell();
        createdCell.textContent = new Date(request.created_at).toLocaleDateString('ja-JP');
        
        // アクション
        const actionCell = row.insertCell();
        const approveBtn = document.createElement('button');
        approveBtn.className = 'btn btn-success btn-sm';
        approveBtn.textContent = '承認';
        approveBtn.onclick = () => approveCorrectionRequest(request.id, 'approved');
        
        const rejectBtn = document.createElement('button');
        rejectBtn.className = 'btn btn-danger btn-sm';
        rejectBtn.textContent = '却下';
        rejectBtn.onclick = () => approveCorrectionRequest(request.id, 'rejected');
        
        actionCell.appendChild(approveBtn);
        actionCell.appendChild(rejectBtn);
    });
}

// 修正申請の承認・却下
async function approveCorrectionRequest(requestId, status) {
    const adminNotes = prompt(`修正申請を${status === 'approved' ? '承認' : '却下'}します。管理者メモを入力してください（任意）:`);
    
    const approvalData = {
        status: status,
        admin_notes: adminNotes || ''
    };
    
    try {
        const response = await fetch(`${API_BASE_URL}/correction-request/${requestId}/approve`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(approvalData)
        });

        if (response.ok) {
            const data = await response.json();
            console.log('申請処理成功:', data);
            alert(data.message);
            loadAllCorrectionRequests();
        } else {
            const error = await response.json();
            console.error('申請処理エラー:', error);
            alert('処理に失敗しました: ' + (error.detail || 'エラーが発生しました'));
        }
    } catch (error) {
        console.error('申請処理ネットワークエラー:', error);
        alert('ネットワークエラーが発生しました: ' + error.message);
    }
}

// 登録関連リスナー
function setupRegisterListeners() {
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegister);
        console.log('登録フォームリスナー設定完了');
    }
    
    // ログインに戻るリンク
    const showLoginLink = document.getElementById('show-login');
    if (showLoginLink) {
        showLoginLink.addEventListener('click', (e) => {
            e.preventDefault();
            showLoginPage();
            setupLoginListeners();
        });
        console.log('ログインリンクリスナー設定完了');
    }
}

// 新規登録処理
async function handleRegister(event) {
    event.preventDefault();
    console.log('登録処理開始');
    
    const formData = new FormData(event.target);
    const registerData = {
        full_name: formData.get('full_name'),
        username: formData.get('username'),
        email: formData.get('email'),
        password: formData.get('password')
    };
    
    try {
        const response = await fetch(`${API_BASE_URL}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(registerData)
        });

        if (response.ok) {
            const data = await response.json();
            console.log('登録成功:', data);
            alert('登録が完了しました。ログインしてください。');
            showLoginPage();
            setupLoginListeners();
        } else {
            const error = await response.json();
            console.error('登録エラー:', error);
            alert('登録に失敗しました: ' + (error.detail || 'エラーが発生しました'));
        }
    } catch (error) {
        console.error('登録ネットワークエラー:', error);
        alert('ネットワークエラーが発生しました: ' + error.message);
    }
}

// 勤怠履歴読み込み
async function loadAttendanceHistory() {
    console.log('勤怠履歴読み込み開始');
    
    try {
        const response = await fetch(`${API_BASE_URL}/attendance/`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            const history = await response.json();
            console.log('勤怠履歴データ:', history);
            displayAttendanceHistory(history);
        } else {
            console.error('勤怠履歴取得エラー:', response.status);
        }
    } catch (error) {
        console.error('勤怠履歴取得ネットワークエラー:', error);
    }
}

// 勤怠履歴表示
function displayAttendanceHistory(history) {
    const table = document.getElementById('attendance-history-table');
    const tbody = table ? table.querySelector('tbody') : null;
    
    if (!tbody) {
        console.log('勤怠履歴テーブルが見つかりません');
        return;
    }
    
    tbody.innerHTML = '';
    
    if (history.length === 0) {
        const row = tbody.insertRow();
        const cell = row.insertCell();
        cell.colSpan = 8;
        cell.textContent = '勤怠履歴はありません';
        cell.style.textAlign = 'center';
        return;
    }
    
    history.forEach(record => {
        const row = tbody.insertRow();
        
        // 日付
        const dateCell = row.insertCell();
        dateCell.textContent = record.date;
        
        // 出勤時刻
        const clockInCell = row.insertCell();
        clockInCell.textContent = record.clock_in ? 
            new Date(record.clock_in).toLocaleTimeString('ja-JP', {hour: '2-digit', minute: '2-digit'}) : '-';
        
        // 退勤時刻
        const clockOutCell = row.insertCell();
        clockOutCell.textContent = record.clock_out ? 
            new Date(record.clock_out).toLocaleTimeString('ja-JP', {hour: '2-digit', minute: '2-digit'}) : '-';
        
        // 休憩開始
        const breakStartCell = row.insertCell();
        breakStartCell.textContent = record.break_start ? 
            new Date(record.break_start).toLocaleTimeString('ja-JP', {hour: '2-digit', minute: '2-digit'}) : '-';
        
        // 休憩終了
        const breakEndCell = row.insertCell();
        breakEndCell.textContent = record.break_end ? 
            new Date(record.break_end).toLocaleTimeString('ja-JP', {hour: '2-digit', minute: '2-digit'}) : '-';
        
        // 労働時間計算
        const workTimeCell = row.insertCell();
        if (record.clock_in && record.clock_out) {
            const clockIn = new Date(record.clock_in);
            const clockOut = new Date(record.clock_out);
            let workMinutes = (clockOut - clockIn) / (1000 * 60);
            
            // 休憩時間を差し引く
            if (record.break_start && record.break_end) {
                const breakStart = new Date(record.break_start);
                const breakEnd = new Date(record.break_end);
                const breakMinutes = (breakEnd - breakStart) / (1000 * 60);
                workMinutes -= breakMinutes;
            }
            
            const hours = Math.floor(workMinutes / 60);
            const minutes = Math.floor(workMinutes % 60);
            workTimeCell.textContent = `${hours}時間${minutes}分`;
        } else {
            workTimeCell.textContent = '-';
        }
        
        // 状態
        const statusCell = row.insertCell();
        if (!record.clock_in) {
            statusCell.textContent = '未出勤';
            statusCell.className = 'status-not-started';
        } else if (record.clock_in && !record.clock_out) {
            statusCell.textContent = '勤務中';
            statusCell.className = 'status-working';
        } else {
            statusCell.textContent = '完了';
            statusCell.className = 'status-completed';
        }
        
        // メモ
        const notesCell = row.insertCell();
        notesCell.textContent = record.notes || '-';
    });
}

// 現在時刻と日付の更新
function updateCurrentTime() {
    const now = new Date();
    
    // 現在時刻の更新
    const currentTimeEl = document.getElementById('current-time');
    if (currentTimeEl) {
        currentTimeEl.textContent = now.toLocaleTimeString('ja-JP');
    }
    
    // 現在日付の更新
    const currentDateEl = document.getElementById('current-date');
    if (currentDateEl) {
        currentDateEl.textContent = now.toLocaleDateString('ja-JP', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            weekday: 'long'
        });
    }
}

// 時刻を定期的に更新
setInterval(updateCurrentTime, 1000);

console.log('debug-app.js読み込み完了');