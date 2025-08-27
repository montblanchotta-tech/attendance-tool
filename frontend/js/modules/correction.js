/**
 * 修正申請関連のモジュール
 */
import CONFIG from '../config.js';
import { formatDateTime, showMessage } from '../utils.js';
import authManager from './auth.js';

class CorrectionManager {
    constructor() {
        this.selectedRecordForRequest = null;
        this.currentRequestId = null;
    }

    // 修正申請を読み込み
    async loadCorrectionRequests() {
        try {
            const response = await fetch(`${CONFIG.API_BASE_URL}/correction-request`, {
                headers: authManager.getAuthHeaders()
            });

            if (response.ok) {
                const requests = await response.json();
                this.displayCorrectionRequests(requests);
            }
        } catch (error) {
            console.error('Load correction requests error:', error);
        }
    }

    // 修正申請を表示
    displayCorrectionRequests(requests) {
        const tbody = document.querySelector('#correction-requests-table tbody');
        tbody.innerHTML = '';

        requests.forEach(request => {
            const row = document.createElement('tr');
            
            const statusClass = `request-status-${request.status}`;
            const statusText = {
                'pending': '承認待ち',
                'approved': '承認済み',
                'rejected': '却下'
            }[request.status] || request.status;

            row.innerHTML = `
                <td>${request.requested_date}</td>
                <td>
                    出勤: ${formatDateTime(request.requested_clock_in)}<br>
                    退勤: ${formatDateTime(request.requested_clock_out)}<br>
                    休憩開始: ${formatDateTime(request.requested_break_start)}<br>
                    休憩終了: ${formatDateTime(request.requested_break_end)}
                </td>
                <td style="max-width: 200px; word-wrap: break-word;">${request.reason}</td>
                <td><span class="${statusClass}">${statusText}</span></td>
                <td>${request.admin_notes || ''}</td>
                <td>${new Date(request.created_at).toLocaleDateString('ja-JP')}</td>
            `;
            
            tbody.appendChild(row);
        });
    }

    // 修正申請モーダルを開く
    openCorrectionRequestModal(recordId = null) {
        this.selectedRecordForRequest = recordId;
        
        // フォームをリセット
        document.getElementById('correction-request-form').reset();
        
        if (recordId) {
            // 既存の記録を修正する場合、記録データを取得してフォームに設定
            this.loadRecordForCorrection(recordId);
        } else {
            // 新規作成の場合は今日の日付を設定
            const today = new Date().toISOString().split('T')[0];
            document.getElementById('correction-date').value = today;
        }
        
        document.getElementById('correction-request-modal').style.display = 'block';
    }

    // 記録データを取得してフォームに設定
    async loadRecordForCorrection(recordId) {
        try {
            // 勤怠履歴から該当の記録を探す
            const response = await fetch(`${CONFIG.API_BASE_URL}/attendance`, {
                headers: authManager.getAuthHeaders()
            });

            if (response.ok) {
                const records = await response.json();
                const record = records.find(r => r.id === recordId);
                
                if (record) {
                    document.getElementById('correction-date').value = record.date;
                    document.getElementById('correction-clock-in').value = record.clock_in ? 
                        new Date(record.clock_in).toTimeString().slice(0, 5) : '';
                    document.getElementById('correction-clock-out').value = record.clock_out ? 
                        new Date(record.clock_out).toTimeString().slice(0, 5) : '';
                    document.getElementById('correction-break-start').value = record.break_start ? 
                        new Date(record.break_start).toTimeString().slice(0, 5) : '';
                    document.getElementById('correction-break-end').value = record.break_end ? 
                        new Date(record.break_end).toTimeString().slice(0, 5) : '';
                    document.getElementById('correction-notes').value = record.notes || '';
                }
            }
        } catch (error) {
            console.error('Load record for correction error:', error);
        }
    }

    // 修正申請を送信
    async submitCorrectionRequest(event) {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        
        const requestData = {
            attendance_record_id: this.selectedRecordForRequest,
            requested_date: formData.get('correction_date'),
            requested_clock_in: formData.get('correction_clock_in') || null,
            requested_clock_out: formData.get('correction_clock_out') || null,
            requested_break_start: formData.get('correction_break_start') || null,
            requested_break_end: formData.get('correction_break_end') || null,
            requested_notes: formData.get('correction_notes') || null,
            reason: formData.get('correction_reason')
        };

        try {
            const response = await fetch(`${CONFIG.API_BASE_URL}/correction-request`, {
                method: 'POST',
                headers: authManager.getAuthHeaders(),
                body: JSON.stringify(requestData)
            });

            if (response.ok) {
                const data = await response.json();
                showMessage(data.message);
                this.closeCorrectionRequestModal();
                this.loadCorrectionRequests();
            } else {
                const error = await response.json();
                showMessage(error.detail || '申請に失敗しました', 'error');
            }
        } catch (error) {
            console.error('Submit correction request error:', error);
            showMessage('ネットワークエラーが発生しました', 'error');
        }
    }

    // 修正申請モーダルを閉じる
    closeCorrectionRequestModal() {
        document.getElementById('correction-request-modal').style.display = 'none';
        this.selectedRecordForRequest = null;
    }
}

// グローバルにエクスポート（HTMLから直接呼び出すため）
window.correctionManager = new CorrectionManager();

export default window.correctionManager;