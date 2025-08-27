/**
 * 勤怠関連のモジュール
 */
import CONFIG from '../config.js';
import { formatDateTime, showMessage } from '../utils.js';
import authManager from './auth.js';

class AttendanceManager {
    constructor() {
        this.attendanceTimer = null;
    }

    // 今日の勤怠状況を読み込み
    async loadTodayAttendance() {
        try {
            const response = await fetch(`${CONFIG.API_BASE_URL}/attendance/today`, {
                headers: authManager.getAuthHeaders()
            });

            if (response.ok) {
                const data = await response.json();
                this.displayTodayAttendance(data);
            }
        } catch (error) {
            console.error('Load today attendance error:', error);
        }
    }

    // 今日の勤怠状況を表示
    displayTodayAttendance(data) {
        const statusDiv = document.getElementById('attendance-status');
        
        if (data.id === 0 || data.status === 'not_clocked_in') {
            statusDiv.innerHTML = `
                <div class="status-item">
                    <div class="status-label">出勤状況</div>
                    <div class="status-value not-clocked">未出勤</div>
                </div>
                <div class="action-buttons">
                    <button onclick="attendanceManager.recordAttendance('clock_in')" class="btn btn-primary">出勤</button>
                </div>
            `;
        } else {
            const clockInTime = data.clock_in ? formatDateTime(data.clock_in) : '--:--';
            const clockOutTime = data.clock_out ? formatDateTime(data.clock_out) : '--:--';
            const breakStartTime = data.break_start ? formatDateTime(data.break_start) : '--:--';
            const breakEndTime = data.break_end ? formatDateTime(data.break_end) : '--:--';
            
            let actionButtons = '';
            if (!data.clock_out) {
                if (!data.break_start || data.break_end) {
                    actionButtons += '<button onclick="attendanceManager.recordAttendance(\'break_start\')" class="btn btn-warning">休憩開始</button>';
                } else {
                    actionButtons += '<button onclick="attendanceManager.recordAttendance(\'break_end\')" class="btn btn-warning">休憩終了</button>';
                }
                actionButtons += '<button onclick="attendanceManager.recordAttendance(\'clock_out\')" class="btn btn-danger">退勤</button>';
            }
            
            statusDiv.innerHTML = `
                <div class="status-row">
                    <div class="status-item">
                        <div class="status-label">出勤</div>
                        <div class="status-value">${clockInTime}</div>
                    </div>
                    <div class="status-item">
                        <div class="status-label">退勤</div>
                        <div class="status-value">${clockOutTime}</div>
                    </div>
                </div>
                <div class="status-row">
                    <div class="status-item">
                        <div class="status-label">休憩開始</div>
                        <div class="status-value">${breakStartTime}</div>
                    </div>
                    <div class="status-item">
                        <div class="status-label">休憩終了</div>
                        <div class="status-value">${breakEndTime}</div>
                    </div>
                </div>
                <div class="action-buttons">
                    ${actionButtons}
                </div>
            `;
        }
    }

    // 勤怠記録
    async recordAttendance(action) {
        const notes = prompt('メモ（任意）:');
        
        try {
            const response = await fetch(`${CONFIG.API_BASE_URL}/attendance`, {
                method: 'POST',
                headers: authManager.getAuthHeaders(),
                body: JSON.stringify({ action, notes })
            });

            if (response.ok) {
                const data = await response.json();
                showMessage(data.message);
                this.loadTodayAttendance();
                this.loadAttendanceHistory();
            } else {
                const error = await response.json();
                showMessage(error.detail || '記録に失敗しました', 'error');
            }
        } catch (error) {
            console.error('Record attendance error:', error);
            showMessage('ネットワークエラーが発生しました', 'error');
        }
    }

    // 勤怠履歴を読み込み
    async loadAttendanceHistory() {
        const startDate = document.getElementById('start-date').value;
        const endDate = document.getElementById('end-date').value;
        
        try {
            const params = new URLSearchParams();
            if (startDate) params.append('start_date', startDate);
            if (endDate) params.append('end_date', endDate);
            
            const response = await fetch(`${CONFIG.API_BASE_URL}/attendance?${params}`, {
                headers: authManager.getAuthHeaders()
            });

            if (response.ok) {
                const data = await response.json();
                this.displayAttendanceHistory(data);
            }
        } catch (error) {
            console.error('Load attendance history error:', error);
        }
    }

    // 勤怠履歴を表示
    displayAttendanceHistory(records) {
        const tbody = document.querySelector('#attendance-table tbody');
        tbody.innerHTML = '';

        records.forEach(record => {
            const row = document.createElement('tr');
            
            // 勤務時間の計算
            let workHours = '';
            if (record.clock_in && record.clock_out) {
                const clockIn = new Date(record.clock_in);
                const clockOut = new Date(record.clock_out);
                let totalHours = (clockOut - clockIn) / (1000 * 60 * 60);
                
                // 休憩時間を引く
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
                    <button onclick="correctionManager.openCorrectionRequestModal(${record.id})" 
                            class="btn btn-sm btn-outline">修正申請</button>
                </td>
            `;
            
            tbody.appendChild(row);
        });
    }
}

// グローバルにエクスポート（HTMLから直接呼び出すため）
window.attendanceManager = new AttendanceManager();

export default window.attendanceManager;