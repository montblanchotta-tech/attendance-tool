// グローバル変数
let currentUser = null;
let attendanceTimer = null;
let allUsers = [];
let selectedUserId = null;
let currentRecordId = null;
let currentRequestId = null;
let selectedRecordForRequest = null;
const API_BASE_URL = 'http://localhost:8001';

// 初期化
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setInterval(updateCurrentTime, 1000);
});

// アプリケーション初期化
function initializeApp() {
    const token = localStorage.getItem('access_token');
    const user = localStorage.getItem('user');
    
    if (token && user) {
        currentUser = JSON.parse(user);
        showMainPage();
        loadTodayAttendance();
        loadAttendanceHistory();
        loadCorrectionRequests();
    } else {
        showLogin();
    }

    // フォームイベントリスナー
    document.getElementById('login-form').addEventListener('submit', handleLogin);
    document.getElementById('register-form').addEventListener('submit', handleRegister);
    
    // 日付フィルターの初期値設定
    const today = new Date();
    const oneMonthAgo = new Date(today.getFullYear(), today.getMonth() - 1, today.getDate());
    document.getElementById('start-date').value = formatDate(oneMonthAgo);
    document.getElementById('end-date').value = formatDate(today);
}

// 現在時刻更新
function updateCurrentTime() {
    const now = new Date();
    document.getElementById('current-date').textContent = formatDateJP(now);
    document.getElementById('current-time').textContent = formatTime(now);
}

// 日付フォーマット関数
function formatDate(date) {
    return date.toISOString().split('T')[0];
}

function formatDateJP(date) {
    return date.toLocaleDateString('ja-JP', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        weekday: 'long'
    });
}

function formatTime(date) {
    return date.toLocaleTimeString('ja-JP', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
}

function formatDateTime(dateTimeStr) {
    if (!dateTimeStr) return '--:--';
    const date = new Date(dateTimeStr);
    return date.toLocaleTimeString('ja-JP', {
        hour: '2-digit',
        minute: '2-digit'
    });
}

// ページ表示制御
function showLogin() {
    document.querySelectorAll('.page').forEach(page => page.classList.remove('active'));
    document.getElementById('login-page').classList.add('active');
}

function showRegister() {
    document.querySelectorAll('.page').forEach(page => page.classList.remove('active'));
    document.getElementById('register-page').classList.add('active');
}

function showMainPage() {
    document.querySelectorAll('.page').forEach(page => page.classList.remove('active'));
    document.getElementById('main-page').classList.add('active');
    if (currentUser) {
        document.getElementById('user-name').textContent = currentUser.full_name;
        // 管理者ボタンの表示制御
        if (currentUser.is_admin) {
            document.getElementById('admin-btn').style.display = 'inline-flex';
        }
    }
}

function showAdminPage() {
    if (!currentUser || !currentUser.is_admin) {
        showMessage('管理者権限が必要です', 'error');
        return;
    }
    document.querySelectorAll('.page').forEach(page => page.classList.remove('active'));
    document.getElementById('admin-page').classList.add('active');
    loadAllUsers();
    loadAdminCorrectionRequests();
    initAdminDateFilters();
}

// ログイン処理
async function handleLogin(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const loginData = {
        username: formData.get('username'),
        password: formData.get('password')
    };

    try {
        const response = await fetch(`${API_BASE_URL}/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(loginData)
        });

        const result = await response.json();

        if (response.ok) {
            localStorage.setItem('access_token', result.access_token);
            localStorage.setItem('user', JSON.stringify(result.user));
            currentUser = result.user;
            showMessage('ログインしました', 'success');
            showMainPage();
            loadTodayAttendance();
            loadAttendanceHistory();
        } else {
            showMessage(result.detail || 'ログインに失敗しました', 'error');
        }
    } catch (error) {
        console.error('Login error:', error);
        showMessage('サーバーに接続できません', 'error');
    }
}

// 登録処理
async function handleRegister(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const registerData = {
        full_name: formData.get('full_name'),
        username: formData.get('username'),
        email: formData.get('email'),
        password: formData.get('password')
    };

    try {
        const response = await fetch(`${API_BASE_URL}/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(registerData)
        });

        const result = await response.json();

        if (response.ok) {
            showMessage('登録が完了しました。ログインしてください。', 'success');
            showLogin();
            event.target.reset();
        } else {
            showMessage(result.detail || '登録に失敗しました', 'error');
        }
    } catch (error) {
        console.error('Register error:', error);
        showMessage('サーバーに接続できません', 'error');
    }
}

// ログアウト
function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    currentUser = null;
    showMessage('ログアウトしました', 'info');
    showLogin();
}

// 勤怠記録
async function recordAttendance(action) {
    const notes = document.getElementById('attendance-notes').value;
    const attendanceData = {
        action: action,
        notes: notes || null
    };

    try {
        const response = await fetch(`${API_BASE_URL}/attendance`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            },
            body: JSON.stringify(attendanceData)
        });

        const result = await response.json();

        if (response.ok) {
            const actionMessages = {
                'clock_in': '出勤を記録しました',
                'clock_out': '退勤を記録しました',
                'break_start': '休憩開始を記録しました',
                'break_end': '休憩終了を記録しました'
            };
            showMessage(actionMessages[action] || '記録しました', 'success');
            document.getElementById('attendance-notes').value = '';
            loadTodayAttendance();
            loadAttendanceHistory();
        } else {
            showMessage(result.detail || '記録に失敗しました', 'error');
        }
    } catch (error) {
        console.error('Attendance error:', error);
        showMessage('サーバーに接続できません', 'error');
    }
}

// 今日の勤怠状況取得
async function loadTodayAttendance() {
    try {
        const response = await fetch(`${API_BASE_URL}/attendance/today`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            }
        });

        const result = await response.json();

        if (response.ok) {
            updateAttendanceUI(result);
        }
    } catch (error) {
        console.error('Load today attendance error:', error);
    }
}

// 勤怠UI更新
function updateAttendanceUI(record) {
    const clockInBtn = document.getElementById('clock-in-btn');
    const clockOutBtn = document.getElementById('clock-out-btn');
    const breakStartBtn = document.getElementById('break-start-btn');
    const breakEndBtn = document.getElementById('break-end-btn');
    const workStatus = document.getElementById('work-status');

    // 時刻表示を更新
    document.getElementById('today-clock-in').textContent = formatDateTime(record.clock_in);
    document.getElementById('today-clock-out').textContent = formatDateTime(record.clock_out);
    document.getElementById('today-break-start').textContent = formatDateTime(record.break_start);
    document.getElementById('today-break-end').textContent = formatDateTime(record.break_end);

    // ボタンの状態を更新
    clockInBtn.disabled = !!record.clock_in;
    clockOutBtn.disabled = !record.clock_in || !!record.clock_out;
    breakStartBtn.disabled = !record.clock_in || !!record.clock_out || (record.break_start && !record.break_end);
    breakEndBtn.disabled = !record.break_start || !!record.break_end;

    // 状態表示を更新
    let statusText = '未出勤';
    let statusClass = '';
    
    if (record.clock_out) {
        statusText = '退勤済み';
        statusClass = '';
    } else if (record.break_start && !record.break_end) {
        statusText = '休憩中';
        statusClass = 'break';
    } else if (record.clock_in) {
        statusText = '勤務中';
        statusClass = 'working';
    }

    workStatus.textContent = statusText;
    workStatus.className = `work-status ${statusClass}`;
}

// 勤怠履歴取得
async function loadAttendanceHistory() {
    const startDate = document.getElementById('start-date').value;
    const endDate = document.getElementById('end-date').value;
    
    let url = `${API_BASE_URL}/attendance`;
    const params = [];
    if (startDate) params.push(`start_date=${startDate}`);
    if (endDate) params.push(`end_date=${endDate}`);
    if (params.length > 0) url += `?${params.join('&')}`;

    try {
        const response = await fetch(url, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            }
        });

        const records = await response.json();

        if (response.ok) {
            displayAttendanceHistory(records);
        }
    } catch (error) {
        console.error('Load attendance history error:', error);
    }
}

// 勤怠履歴表示
function displayAttendanceHistory(records) {
    const tbody = document.querySelector('#attendance-table tbody');
    tbody.innerHTML = '';

    records.forEach(record => {
        const row = document.createElement('tr');
        
        // 労働時間計算
        let workingHours = '--';
        if (record.clock_in && record.clock_out) {
            const clockIn = new Date(record.clock_in);
            const clockOut = new Date(record.clock_out);
            let totalMinutes = (clockOut - clockIn) / (1000 * 60);
            
            // 休憩時間を差し引く
            if (record.break_start && record.break_end) {
                const breakStart = new Date(record.break_start);
                const breakEnd = new Date(record.break_end);
                const breakMinutes = (breakEnd - breakStart) / (1000 * 60);
                totalMinutes -= breakMinutes;
            }
            
            const hours = Math.floor(totalMinutes / 60);
            const minutes = Math.floor(totalMinutes % 60);
            workingHours = `${hours}時間${minutes}分`;
        }

        // ステータスバッジ
        const statusClass = `status-${record.status}`;
        const statusText = {
            'present': '出勤',
            'absent': '欠勤',
            'late': '遅刻',
            'early_leave': '早退'
        }[record.status] || record.status;

        row.innerHTML = `
            <td>${record.date}</td>
            <td>${formatDateTime(record.clock_in)}</td>
            <td>${formatDateTime(record.clock_out)}</td>
            <td>${formatDateTime(record.break_start)}</td>
            <td>${formatDateTime(record.break_end)}</td>
            <td>${workingHours}</td>
            <td><span class="status-badge ${statusClass}">${statusText}</span></td>
            <td>${record.notes || ''}</td>
            <td>
                <button onclick="openCorrectionRequestModal(${record.id}, '${record.date}')" class="btn btn-warning" style="font-size: 12px; padding: 4px 8px;">
                    <i class="fas fa-edit"></i> 修正申請
                </button>
            </td>
        `;
        
        tbody.appendChild(row);
    });
}

// メッセージ表示
function showMessage(text, type = 'info') {
    const messageEl = document.getElementById('message');
    messageEl.textContent = text;
    messageEl.className = `message ${type}`;
    messageEl.classList.add('show');
    
    setTimeout(() => {
        messageEl.classList.remove('show');
    }, 3000);
}

// 管理者機能
async function loadAllUsers() {
    try {
        const response = await fetch(`${API_BASE_URL}/admin/users`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            }
        });

        if (response.ok) {
            allUsers = await response.json();
            displayUsersList();
            populateUserSelect();
        } else {
            showMessage('ユーザー一覧の取得に失敗しました', 'error');
        }
    } catch (error) {
        console.error('Load users error:', error);
        showMessage('サーバーに接続できません', 'error');
    }
}

function displayUsersList() {
    const tbody = document.querySelector('#users-table tbody');
    tbody.innerHTML = '';

    allUsers.forEach(user => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${user.id}</td>
            <td>${user.username}</td>
            <td>${user.full_name}</td>
            <td>${user.email}</td>
            <td>${user.is_admin ? 'はい' : 'いいえ'}</td>
            <td>${new Date(user.created_at).toLocaleDateString('ja-JP')}</td>
            <td>
                <div class="admin-actions">
                    <button onclick="selectUserForAttendance(${user.id}, '${user.full_name}')" class="btn btn-info">勤怠確認</button>
                </div>
            </td>
        `;
        tbody.appendChild(row);
    });
}

function populateUserSelect() {
    const select = document.getElementById('correction-user');
    select.innerHTML = '<option value="">選択してください</option>';
    
    allUsers.forEach(user => {
        const option = document.createElement('option');
        option.value = user.id;
        option.textContent = `${user.full_name} (${user.username})`;
        select.appendChild(option);
    });
}

function selectUserForAttendance(userId, userName) {
    selectedUserId = userId;
    document.getElementById('user-attendance-title').textContent = `${userName} さんの勤怠一覧`;
    document.getElementById('user-attendance-card').style.display = 'block';
    document.getElementById('correction-user').value = userId;
    loadUserAttendance();
}

async function loadUserAttendance() {
    if (!selectedUserId) return;

    const startDate = document.getElementById('admin-start-date').value;
    const endDate = document.getElementById('admin-end-date').value;
    
    let url = `${API_BASE_URL}/admin/attendance/${selectedUserId}`;
    const params = [];
    if (startDate) params.push(`start_date=${startDate}`);
    if (endDate) params.push(`end_date=${endDate}`);
    if (params.length > 0) url += `?${params.join('&')}`;

    try {
        const response = await fetch(url, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            }
        });

        if (response.ok) {
            const result = await response.json();
            displayUserAttendanceRecords(result.records);
        } else {
            showMessage('勤怠記録の取得に失敗しました', 'error');
        }
    } catch (error) {
        console.error('Load user attendance error:', error);
        showMessage('サーバーに接続できません', 'error');
    }
}

function displayUserAttendanceRecords(records) {
    const tbody = document.querySelector('#user-attendance-table tbody');
    tbody.innerHTML = '';

    records.forEach(record => {
        const row = document.createElement('tr');
        
        // 労働時間計算
        let workingHours = '--';
        if (record.clock_in && record.clock_out) {
            const clockIn = new Date(record.clock_in);
            const clockOut = new Date(record.clock_out);
            let totalMinutes = (clockOut - clockIn) / (1000 * 60);
            
            if (record.break_start && record.break_end) {
                const breakStart = new Date(record.break_start);
                const breakEnd = new Date(record.break_end);
                const breakMinutes = (breakEnd - breakStart) / (1000 * 60);
                totalMinutes -= breakMinutes;
            }
            
            const hours = Math.floor(totalMinutes / 60);
            const minutes = Math.floor(totalMinutes % 60);
            workingHours = `${hours}時間${minutes}分`;
        }

        const statusClass = `status-${record.status}`;
        const statusText = {
            'present': '出勤',
            'absent': '欠勤',
            'late': '遅刻',
            'early_leave': '早退'
        }[record.status] || record.status;

        row.innerHTML = `
            <td>${record.date}</td>
            <td>${formatDateTime(record.clock_in)}</td>
            <td>${formatDateTime(record.clock_out)}</td>
            <td>${formatDateTime(record.break_start)}</td>
            <td>${formatDateTime(record.break_end)}</td>
            <td>${workingHours}</td>
            <td><span class="status-badge ${statusClass}">${statusText}</span></td>
            <td style="max-width: 200px; overflow-wrap: break-word;">${record.notes || ''}</td>
            <td>
                <button onclick="editRecord(${record.id}, '${record.date}')" class="btn edit-record-btn">編集</button>
            </td>
        `;
        
        tbody.appendChild(row);
    });
}

async function loadExistingRecord() {
    const userId = document.getElementById('correction-user').value;
    const date = document.getElementById('correction-date').value;
    
    if (!userId || !date) {
        showMessage('ユーザーと日付を選択してください', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/admin/attendance/${userId}?start_date=${date}&end_date=${date}`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            }
        });

        if (response.ok) {
            const result = await response.json();
            const records = result.records;
            
            if (records.length === 0) {
                showMessage('その日の記録はありません', 'info');
                clearTimeInputs();
                document.getElementById('update-btn').style.display = 'none';
                currentRecordId = null;
                return;
            }

            const record = records[0];
            populateTimeInputs(record);
            document.getElementById('update-btn').style.display = 'inline-flex';
            currentRecordId = record.id;
            showMessage('既存記録を読み込みました', 'success');
        }
    } catch (error) {
        console.error('Load existing record error:', error);
        showMessage('記録の読み込みに失敗しました', 'error');
    }
}

function populateTimeInputs(record) {
    document.getElementById('correction-clock-in').value = record.clock_in ? formatTimeForInput(record.clock_in) : '';
    document.getElementById('correction-clock-out').value = record.clock_out ? formatTimeForInput(record.clock_out) : '';
    document.getElementById('correction-break-start').value = record.break_start ? formatTimeForInput(record.break_start) : '';
    document.getElementById('correction-break-end').value = record.break_end ? formatTimeForInput(record.break_end) : '';
    document.getElementById('correction-notes').value = record.notes || '';
}

function formatTimeForInput(dateTimeStr) {
    if (!dateTimeStr) return '';
    const date = new Date(dateTimeStr);
    return date.toTimeString().slice(0, 5); // HH:MM
}

function clearTimeInputs() {
    document.getElementById('correction-clock-in').value = '';
    document.getElementById('correction-clock-out').value = '';
    document.getElementById('correction-break-start').value = '';
    document.getElementById('correction-break-end').value = '';
    document.getElementById('correction-notes').value = '';
}

async function createAttendanceRecord() {
    const correctionData = getCorrectionFormData();
    if (!correctionData) return;

    try {
        const response = await fetch(`${API_BASE_URL}/admin/attendance/create`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            },
            body: JSON.stringify(correctionData)
        });

        const result = await response.json();

        if (response.ok) {
            showMessage('勤怠記録を作成しました', 'success');
            clearCorrectionForm();
            if (selectedUserId) loadUserAttendance();
        } else {
            showMessage(result.detail || '作成に失敗しました', 'error');
        }
    } catch (error) {
        console.error('Create record error:', error);
        showMessage('サーバーに接続できません', 'error');
    }
}

async function updateAttendanceRecord() {
    if (!currentRecordId) {
        showMessage('修正する記録がありません', 'error');
        return;
    }

    const correctionData = getCorrectionFormData();
    if (!correctionData) return;

    try {
        const response = await fetch(`${API_BASE_URL}/admin/attendance/${currentRecordId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            },
            body: JSON.stringify(correctionData)
        });

        const result = await response.json();

        if (response.ok) {
            showMessage('勤怠記録を修正しました', 'success');
            clearCorrectionForm();
            if (selectedUserId) loadUserAttendance();
        } else {
            showMessage(result.detail || '修正に失敗しました', 'error');
        }
    } catch (error) {
        console.error('Update record error:', error);
        showMessage('サーバーに接続できません', 'error');
    }
}

function getCorrectionFormData() {
    const userId = document.getElementById('correction-user').value;
    const date = document.getElementById('correction-date').value;
    const reason = document.getElementById('correction-reason').value;

    if (!userId || !date || !reason.trim()) {
        showMessage('ユーザー、日付、修正理由は必須です', 'error');
        return null;
    }

    return {
        user_id: parseInt(userId),
        date: date,
        clock_in: document.getElementById('correction-clock-in').value || null,
        clock_out: document.getElementById('correction-clock-out').value || null,
        break_start: document.getElementById('correction-break-start').value || null,
        break_end: document.getElementById('correction-break-end').value || null,
        notes: document.getElementById('correction-notes').value || null,
        reason: reason
    };
}

function editRecord(recordId, date) {
    currentRecordId = recordId;
    document.getElementById('correction-date').value = date;
    loadExistingRecord();
    window.scrollTo({ top: document.querySelector('.correction-form').offsetTop - 100, behavior: 'smooth' });
}

function clearCorrectionForm() {
    document.getElementById('correction-user').value = '';
    document.getElementById('correction-date').value = '';
    document.getElementById('correction-reason').value = '';
    clearTimeInputs();
    document.getElementById('update-btn').style.display = 'none';
    currentRecordId = null;
}

function initAdminDateFilters() {
    const today = new Date();
    const oneMonthAgo = new Date(today.getFullYear(), today.getMonth() - 1, today.getDate());
    document.getElementById('admin-start-date').value = formatDate(oneMonthAgo);
    document.getElementById('admin-end-date').value = formatDate(today);
}

// 修正申請機能
function openCorrectionRequestModal(recordId, date) {
    selectedRecordForRequest = recordId;
    document.getElementById('request-date').value = date;
    
    // 既存記録があれば読み込み
    if (recordId) {
        loadExistingRecordForRequest(recordId);
    }
    
    // モーダルタイトルを変更
    document.querySelector('#correction-request-modal .modal-header h3').textContent = 
        recordId ? '勤怠修正申請' : '勤怠記録申請';
    
    document.getElementById('correction-request-modal').style.display = 'block';
}

function openNewCorrectionRequestModal() {
    selectedRecordForRequest = null;
    clearRequestForm();
    
    // デフォルトで今日の日付を設定
    const today = new Date();
    document.getElementById('request-date').value = formatDate(today);
    
    // モーダルタイトルを設定
    document.querySelector('#correction-request-modal .modal-header h3').textContent = '新規勤怠申請';
    
    document.getElementById('correction-request-modal').style.display = 'block';
}

function closeCorrectionRequestModal() {
    document.getElementById('correction-request-modal').style.display = 'none';
    clearRequestForm();
}

function clearRequestForm() {
    document.getElementById('request-date').value = '';
    document.getElementById('request-clock-in').value = '';
    document.getElementById('request-clock-out').value = '';
    document.getElementById('request-break-start').value = '';
    document.getElementById('request-break-end').value = '';
    document.getElementById('request-notes').value = '';
    document.getElementById('request-reason').value = '';
    selectedRecordForRequest = null;
}

async function loadExistingRecordForRequest(recordId) {
    const records = await getCurrentAttendanceRecords();
    const record = records.find(r => r.id === recordId);
    
    if (record) {
        document.getElementById('request-clock-in').value = record.clock_in ? formatTimeForInput(record.clock_in) : '';
        document.getElementById('request-clock-out').value = record.clock_out ? formatTimeForInput(record.clock_out) : '';
        document.getElementById('request-break-start').value = record.break_start ? formatTimeForInput(record.break_start) : '';
        document.getElementById('request-break-end').value = record.break_end ? formatTimeForInput(record.break_end) : '';
        document.getElementById('request-notes').value = record.notes || '';
    }
}

async function getCurrentAttendanceRecords() {
    try {
        const response = await fetch(`${API_BASE_URL}/attendance`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            }
        });
        return response.ok ? await response.json() : [];
    } catch (error) {
        return [];
    }
}

async function submitCorrectionRequest() {
    const requestData = {
        attendance_record_id: selectedRecordForRequest,
        requested_date: document.getElementById('request-date').value,
        requested_clock_in: document.getElementById('request-clock-in').value || null,
        requested_clock_out: document.getElementById('request-clock-out').value || null,
        requested_break_start: document.getElementById('request-break-start').value || null,
        requested_break_end: document.getElementById('request-break-end').value || null,
        requested_notes: document.getElementById('request-notes').value || null,
        reason: document.getElementById('request-reason').value
    };

    if (!requestData.requested_date || !requestData.reason.trim()) {
        showMessage('対象日付と申請理由は必須です', 'error');
        return;
    }

    // 時刻が1つも入力されていない場合は警告
    const hasAnyTime = requestData.requested_clock_in || requestData.requested_clock_out || 
                      requestData.requested_break_start || requestData.requested_break_end;
    
    if (!hasAnyTime && !requestData.requested_notes) {
        showMessage('申請内容（時刻またはメモ）を入力してください', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/correction-request`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            },
            body: JSON.stringify(requestData)
        });

        const result = await response.json();

        if (response.ok) {
            const messageText = selectedRecordForRequest ? '修正申請を送信しました' : '勤怠申請を送信しました';
            showMessage(messageText, 'success');
            closeCorrectionRequestModal();
            loadCorrectionRequests();
        } else {
            showMessage(result.detail || '申請に失敗しました', 'error');
        }
    } catch (error) {
        console.error('Submit request error:', error);
        showMessage('サーバーに接続できません', 'error');
    }
}

async function loadCorrectionRequests() {
    try {
        const response = await fetch(`${API_BASE_URL}/correction-requests`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            }
        });

        if (response.ok) {
            const requests = await response.json();
            displayCorrectionRequests(requests);
        }
    } catch (error) {
        console.error('Load correction requests error:', error);
    }
}

function displayCorrectionRequests(requests) {
    const tbody = document.querySelector('#correction-requests-table tbody');
    tbody.innerHTML = '';

    if (requests.length === 0) {
        const row = document.createElement('tr');
        row.innerHTML = '<td colspan="6" style="text-align: center; color: #666; padding: 20px;">申請履歴がありません</td>';
        tbody.appendChild(row);
        return;
    }

    requests.forEach(request => {
        const row = document.createElement('tr');
        
        const statusClass = `request-status-${request.status}`;
        const statusText = {
            'pending': '承認待ち',
            'approved': '承認済み',
            'rejected': '却下'
        }[request.status] || request.status;

        // 申請内容のサマリーを作成
        const requestSummary = [];
        if (request.requested_clock_in) requestSummary.push(`出勤: ${formatDateTime(request.requested_clock_in)}`);
        if (request.requested_clock_out) requestSummary.push(`退勤: ${formatDateTime(request.requested_clock_out)}`);
        if (request.requested_break_start) requestSummary.push(`休憩開始: ${formatDateTime(request.requested_break_start)}`);
        if (request.requested_break_end) requestSummary.push(`休憩終了: ${formatDateTime(request.requested_break_end)}`);
        if (request.requested_notes) requestSummary.push(`メモ: ${request.requested_notes}`);
        
        const requestContent = requestSummary.length > 0 ? requestSummary.join('<br>') : '記録なし';

        // 申請理由を短縮表示（長い場合）
        const shortReason = request.reason.length > 50 ? 
            request.reason.substring(0, 50) + '...' : 
            request.reason;

        row.innerHTML = `
            <td>${request.requested_date}</td>
            <td style="max-width: 150px; word-wrap: break-word; font-size: 12px;">${requestContent}</td>
            <td style="max-width: 200px; word-wrap: break-word;" title="${request.reason}">${shortReason}</td>
            <td><span class="${statusClass}">${statusText}</span></td>
            <td style="max-width: 150px; word-wrap: break-word;">${request.admin_notes || '-'}</td>
            <td style="font-size: 12px;">${new Date(request.created_at).toLocaleString('ja-JP')}</td>
        `;
        
        tbody.appendChild(row);
    });
}

async function loadAdminCorrectionRequests() {
    try {
        const response = await fetch(`${API_BASE_URL}/admin/correction-requests`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            }
        });

        if (response.ok) {
            const requests = await response.json();
            displayAdminCorrectionRequests(requests);
        }
    } catch (error) {
        console.error('Load admin correction requests error:', error);
    }
}

function displayAdminCorrectionRequests(requests) {
    const tbody = document.querySelector('#admin-correction-requests-table tbody');
    tbody.innerHTML = '';

    requests.forEach(request => {
        const row = document.createElement('tr');
        
        const statusClass = `request-status-${request.status}`;
        const statusText = {
            'pending': '承認待ち',
            'approved': '承認済み',
            'rejected': '却下'
        }[request.status] || request.status;

        const requestSummary = [];
        if (request.requested_clock_in) requestSummary.push(`出勤: ${formatDateTime(request.requested_clock_in)}`);
        if (request.requested_clock_out) requestSummary.push(`退勤: ${formatDateTime(request.requested_clock_out)}`);
        if (request.requested_break_start) requestSummary.push(`休憩開始: ${formatDateTime(request.requested_break_start)}`);
        if (request.requested_break_end) requestSummary.push(`休憩終了: ${formatDateTime(request.requested_break_end)}`);

        row.innerHTML = `
            <td>${request.user.full_name}<br><small>(${request.user.username})</small></td>
            <td>${request.requested_date}</td>
            <td style="max-width: 150px; word-wrap: break-word;">${requestSummary.join('<br>')}</td>
            <td style="max-width: 200px; word-wrap: break-word;">${request.reason}</td>
            <td><span class="${statusClass}">${statusText}</span></td>
            <td>${new Date(request.created_at).toLocaleDateString('ja-JP')}</td>
            <td>
                ${request.status === 'pending' ? 
                    `<button onclick="openApprovalModal(${request.id})" class="btn btn-info" style="font-size: 12px; padding: 4px 8px;">処理</button>` :
                    '-'
                }
            </td>
        `;
        
        tbody.appendChild(row);
    });
}

function openApprovalModal(requestId) {
    currentRequestId = requestId;
    
    // 申請詳細を取得して表示
    fetch(`${API_BASE_URL}/admin/correction-requests`, {
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
    })
    .then(response => response.json())
    .then(requests => {
        const request = requests.find(r => r.id === requestId);
        if (request) {
            displayRequestDetails(request);
            document.getElementById('approval-modal').style.display = 'block';
        }
    });
}

function displayRequestDetails(request) {
    const detailsDiv = document.getElementById('approval-request-details');
    
    const requestSummary = [];
    if (request.requested_clock_in) requestSummary.push(`出勤時刻: ${formatDateTime(request.requested_clock_in)}`);
    if (request.requested_clock_out) requestSummary.push(`退勤時刻: ${formatDateTime(request.requested_clock_out)}`);
    if (request.requested_break_start) requestSummary.push(`休憩開始: ${formatDateTime(request.requested_break_start)}`);
    if (request.requested_break_end) requestSummary.push(`休憩終了: ${formatDateTime(request.requested_break_end)}`);
    if (request.requested_notes) requestSummary.push(`メモ: ${request.requested_notes}`);

    detailsDiv.innerHTML = `
        <div class="request-details">
            <h4>申請詳細</h4>
            <div class="detail-row">
                <span class="detail-label">申請者:</span>
                <span>${request.user.full_name} (${request.user.username})</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">対象日付:</span>
                <span>${request.requested_date}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">申請内容:</span>
                <span>${requestSummary.join('<br>')}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">申請理由:</span>
                <span>${request.reason}</span>
            </div>
        </div>
    `;
}

function closeApprovalModal() {
    document.getElementById('approval-modal').style.display = 'none';
    document.getElementById('admin-notes').value = '';
    currentRequestId = null;
}

async function processRequest(status) {
    if (!currentRequestId) return;

    const approvalData = {
        status: status,
        admin_notes: document.getElementById('admin-notes').value || null
    };

    try {
        const response = await fetch(`${API_BASE_URL}/admin/correction-requests/${currentRequestId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            },
            body: JSON.stringify(approvalData)
        });

        const result = await response.json();

        if (response.ok) {
            const actionText = status === 'approved' ? '承認' : '却下';
            showMessage(`申請を${actionText}しました`, 'success');
            closeApprovalModal();
            loadAdminCorrectionRequests();
        } else {
            showMessage(result.detail || '処理に失敗しました', 'error');
        }
    } catch (error) {
        console.error('Process request error:', error);
        showMessage('サーバーに接続できません', 'error');
    }
}

// API エラーハンドリング
function handleApiError(response) {
    if (response.status === 401) {
        logout();
        showMessage('セッションが期限切れです。再度ログインしてください。', 'error');
    }
}