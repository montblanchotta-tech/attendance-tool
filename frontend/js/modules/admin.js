/**
 * 管理者関連のモジュール
 */
import CONFIG from '../config.js';
import { formatDateTime, showMessage } from '../utils.js';
import authManager from './auth.js';

class AdminManager {
    constructor() {
        this.allUsers = [];
        this.selectedUserId = null;
        this.currentRecordId = null;
        this.currentRequestId = null;
    }

    // 全ユーザーを読み込み
    async loadAllUsers() {
        try {
            const response = await fetch(`${CONFIG.API_BASE_URL}/admin/users`, {
                headers: authManager.getAuthHeaders()
            });

            if (response.ok) {
                const users = await response.json();
                this.allUsers = users;
                this.displayUsers(users);
            }
        } catch (error) {
            console.error('Load users error:', error);
        }
    }

    // ユーザー一覧を表示
    displayUsers(users) {
        const tbody = document.querySelector('#users-table tbody');
        tbody.innerHTML = '';

        users.forEach(user => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${user.username}</td>
                <td>${user.full_name}</td>
                <td>${user.email}</td>
                <td>${user.is_admin ? '管理者' : '一般'}</td>
                <td>${new Date(user.created_at).toLocaleDateString('ja-JP')}</td>
                <td>
                    <button onclick="adminManager.loadUserAttendance(${user.id})" class="btn btn-info">勤怠確認</button>
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    // ユーザーの勤怠記録を読み込み
    async loadUserAttendance(userId) {
        this.selectedUserId = userId;
        const startDate = document.getElementById('admin-start-date').value;
        const endDate = document.getElementById('admin-end-date').value;

        try {
            const params = new URLSearchParams();
            if (startDate) params.append('start_date', startDate);
            if (endDate) params.append('end_date', endDate);

            const response = await fetch(`${CONFIG.API_BASE_URL}/admin/attendance/${userId}?${params}`, {
                headers: authManager.getAuthHeaders()
            });

            if (response.ok) {
                const data = await response.json();
                this.displayUserAttendance(data);
                document.getElementById('user-attendance-section').style.display = 'block';
            }
        } catch (error) {
            console.error('Load user attendance error:', error);
        }
    }

    // ユーザーの勤怠記録を表示
    displayUserAttendance(data) {
        document.getElementById('selected-user-info').textContent = 
            `${data.user.full_name} (${data.user.username})`;

        const tbody = document.querySelector('#user-attendance-table tbody');
        tbody.innerHTML = '';

        data.records.forEach(record => {
            const row = document.createElement('tr');
            
            // 勤務時間の計算
            let workHours = '';
            if (record.clock_in && record.clock_out) {
                const clockIn = new Date(record.clock_in);
                const clockOut = new Date(record.clock_out);
                let totalHours = (clockOut - clockIn) / (1000 * 60 * 60);
                
                if (record.break_start && record.break_end) {
                    const breakStart = new Date(record.break_start);
                    const breakEnd = new Date(record.break_end);
                    const breakHours = (breakEnd - breakStart) / (1000 * 60 * 60);
                    totalHours -= breakHours;
                }
                
                workHours = `${totalHours.toFixed(1)}h`;
            }
            
            row.innerHTML = `
                <td>${record.date}</td>
                <td>${record.clock_in ? formatDateTime(record.clock_in) : '--:--'}</td>
                <td>${record.clock_out ? formatDateTime(record.clock_out) : '--:--'}</td>
                <td>${record.break_start ? formatDateTime(record.break_start) : '--:--'}</td>
                <td>${record.break_end ? formatDateTime(record.break_end) : '--:--'}</td>
                <td>${workHours}</td>
                <td>${record.notes || ''}</td>
                <td>
                    <button onclick="adminManager.openEditModal(${record.id}, '${record.date}')" 
                            class="btn btn-warning btn-sm">編集</button>
                </td>
            `;
            
            tbody.appendChild(row);
        });
    }

    // 編集モーダルを開く
    async openEditModal(recordId, date) {
        this.currentRecordId = recordId;
        
        try {
            const response = await fetch(`${CONFIG.API_BASE_URL}/admin/attendance/${this.selectedUserId}`, {
                headers: authManager.getAuthHeaders()
            });

            if (response.ok) {
                const data = await response.json();
                const record = data.records.find(r => r.id === recordId);
                
                if (record) {
                    document.getElementById('edit-date').value = record.date;
                    document.getElementById('edit-clock-in').value = record.clock_in ? 
                        new Date(record.clock_in).toTimeString().slice(0, 5) : '';
                    document.getElementById('edit-clock-out').value = record.clock_out ? 
                        new Date(record.clock_out).toTimeString().slice(0, 5) : '';
                    document.getElementById('edit-break-start').value = record.break_start ? 
                        new Date(record.break_start).toTimeString().slice(0, 5) : '';
                    document.getElementById('edit-break-end').value = record.break_end ? 
                        new Date(record.break_end).toTimeString().slice(0, 5) : '';
                    document.getElementById('edit-notes').value = record.notes || '';
                }
                
                document.getElementById('edit-modal').style.display = 'block';
            }
        } catch (error) {
            console.error('Open edit modal error:', error);
        }
    }

    // 勤怠記録を更新
    async updateAttendanceRecord(event) {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        const reason = document.getElementById('edit-reason').value;
        
        if (!reason.trim()) {
            showMessage('修正理由を入力してください', 'error');
            return;
        }
        
        const correctionData = {
            user_id: this.selectedUserId,
            date: formData.get('edit_date'),
            clock_in: formData.get('edit_clock_in') || null,
            clock_out: formData.get('edit_clock_out') || null,
            break_start: formData.get('edit_break_start') || null,
            break_end: formData.get('edit_break_end') || null,
            notes: formData.get('edit_notes') || null,
            reason: reason
        };

        try {
            const response = await fetch(`${CONFIG.API_BASE_URL}/admin/attendance/correct`, {
                method: 'POST',
                headers: authManager.getAuthHeaders(),
                body: JSON.stringify(correctionData)
            });

            if (response.ok) {
                const data = await response.json();
                showMessage(data.message);
                this.closeEditModal();
                this.loadUserAttendance(this.selectedUserId);
            } else {
                const error = await response.json();
                showMessage(error.detail || '更新に失敗しました', 'error');
            }
        } catch (error) {
            console.error('Update attendance error:', error);
            showMessage('ネットワークエラーが発生しました', 'error');
        }
    }

    // 編集モーダルを閉じる
    closeEditModal() {
        document.getElementById('edit-modal').style.display = 'none';
        document.getElementById('edit-form').reset();
        document.getElementById('edit-reason').value = '';
        this.currentRecordId = null;
    }

    // 管理者の修正申請一覧を読み込み
    async loadAdminCorrectionRequests() {
        try {
            const response = await fetch(`${CONFIG.API_BASE_URL}/correction-request/admin/all`, {
                headers: authManager.getAuthHeaders()
            });

            if (response.ok) {
                const requests = await response.json();
                this.displayAdminCorrectionRequests(requests);
            }
        } catch (error) {
            console.error('Load admin correction requests error:', error);
        }
    }

    // 管理者の修正申請一覧を表示
    displayAdminCorrectionRequests(requests) {
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
                        `<button onclick="adminManager.openApprovalModal(${request.id})" class="btn btn-info" style="font-size: 12px; padding: 4px 8px;">処理</button>` :
                        '-'
                    }
                </td>
            `;
            
            tbody.appendChild(row);
        });
    }

    // 承認モーダルを開く
    async openApprovalModal(requestId) {
        this.currentRequestId = requestId;
        
        try {
            const response = await fetch(`${CONFIG.API_BASE_URL}/correction-request/admin/all`, {
                headers: authManager.getAuthHeaders()
            });

            if (response.ok) {
                const requests = await response.json();
                const request = requests.find(r => r.id === requestId);
                
                if (request) {
                    this.displayRequestDetails(request);
                    document.getElementById('approval-modal').style.display = 'block';
                }
            }
        } catch (error) {
            console.error('Open approval modal error:', error);
        }
    }

    // 申請詳細を表示
    displayRequestDetails(request) {
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

    // 申請を処理
    async processRequest(status) {
        const adminNotes = document.getElementById('admin-notes').value;
        
        const approvalData = {
            status: status,
            admin_notes: adminNotes || null
        };

        try {
            const response = await fetch(`${CONFIG.API_BASE_URL}/correction-request/${this.currentRequestId}/approve`, {
                method: 'PUT',
                headers: authManager.getAuthHeaders(),
                body: JSON.stringify(approvalData)
            });

            if (response.ok) {
                const data = await response.json();
                showMessage(data.message);
                this.closeApprovalModal();
                this.loadAdminCorrectionRequests();
            } else {
                const error = await response.json();
                showMessage(error.detail || '処理に失敗しました', 'error');
            }
        } catch (error) {
            console.error('Process request error:', error);
            showMessage('ネットワークエラーが発生しました', 'error');
        }
    }

    // 承認モーダルを閉じる
    closeApprovalModal() {
        document.getElementById('approval-modal').style.display = 'none';
        document.getElementById('admin-notes').value = '';
        this.currentRequestId = null;
    }
}

// グローバルにエクスポート（HTMLから直接呼び出すため）
window.adminManager = new AdminManager();

export default window.adminManager;