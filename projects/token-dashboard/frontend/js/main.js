// Token Dashboard - Frontend JavaScript

const API_BASE = '/api';
let currentPage = 'overview';
let currentFilter = 'all'; // 保存總覽頁面的 filter 狀態
let countdownValue = 5.0; // 改為 5 秒刷新
let countdownInterval;
let isLoading = false; // 防止重複載入
let currentAbortController = null; // 用於取消進行中的請求

// 初始化
document.addEventListener('DOMContentLoaded', () => {
  setupNavigation();
  loadPage('overview');
  updateControlPanel();
  // startCountdown(); // 自動刷新已停用
  
  // 自動刷新已停用
  // 如需手動刷新，請按 F5 或點擊瀏覽器刷新按鈕
  
  // 配額詳情每 5 分鐘刷新
  setInterval(() => {
    if (currentPage === 'quota' && !isLoading) {
      loadPage(currentPage, false);
    }
  }, 300000); // 5 分鐘 = 300000ms
});

// 導航設置
function setupNavigation() {
  const navBtns = document.querySelectorAll('.nav-btn');
  navBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const page = btn.dataset.page;
      navBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      loadPage(page);
    });
  });
}

// 載入頁面
async function loadPage(page, showLoading = true) {
  // 如果正在載入且是自動刷新，跳過
  if (isLoading && !showLoading) {
    return;
  }
  
  // 取消之前的請求
  if (currentAbortController) {
    currentAbortController.abort();
  }
  currentAbortController = new AbortController();
  
  const targetPage = page;
  currentPage = page;
  const content = document.getElementById('content');
  
  if (showLoading) {
    content.innerHTML = '<div class="loading">載入中...</div>';
  }
  
  isLoading = true;
  
  try {
    // 檢查是否被切換到其他頁面
    if (currentPage !== targetPage) {
      return;
    }
    
    switch (page) {
      case 'overview':
        await renderOverview(currentFilter);
        break;
      case 'quota':
        await renderQuota();
        break;
      case 'models':
        await renderModels();
        break;
      case 'model-analytics':
        await renderModelAnalytics();
        break;
      case 'rate-limits':
        await renderRateLimits();
        break;
      case 'history':
        await renderHistory();
        break;
      case 'cost':
        await renderCost();
        break;
    }
  } catch (error) {
    // 忽略 abort 錯誤
    if (error.name === 'AbortError') {
      return;
    }
    // 只有還在同一頁面才顯示錯誤
    if (currentPage === targetPage) {
      content.innerHTML = `<div class="error">載入失敗：${error.message}</div>`;
    }
  } finally {
    isLoading = false;
  }
}

// 渲染總覽頁
async function renderOverview(filter = 'all') {
  // 保存 filter 狀態
  currentFilter = filter;
  
  // 並行獲取：即時統計 + DB 統計 + OAuth 狀態 + API 額度 + 速率限制 + 模型分析
  const [live, today, week, month, oauthStatus, quotaUsage, rateLimits, modelAnalytics] = await Promise.all([
    fetch(`${API_BASE}/live-stats?filter=${filter}`).then(r => r.json()),
    fetch(`${API_BASE}/overview?period=today`).then(r => r.json()),
    fetch(`${API_BASE}/overview?period=week`).then(r => r.json()),
    fetch(`${API_BASE}/overview?period=month`).then(r => r.json()),
    fetch(`${API_BASE}/oauth-status`).then(r => r.json()).catch(() => ({ tokens: [] })),
    fetch(`${API_BASE}/quota-usage`).then(r => r.json()).catch(() => ({ google_gemini: [], openai: [] })),
    fetch(`${API_BASE}/rate-limits`).then(r => r.json()).catch(() => ({ rate_limits: [] })),
    fetch(`${API_BASE}/model-analytics?period=today`).then(r => r.json()).catch(() => ({ models: [] }))
  ]);
  
  const content = document.getElementById('content');
  
  // 使用即時統計（live）代替 DB 統計，更快更準確
  const todayTokens = live.total_tokens || today.total_tokens;
  const estimatedCost = (todayTokens / 1000000 * 3).toFixed(2); // 粗估
  
  // API 額度狀態警告
  let quotaWarnings = '';
  
  // Anthropic OAuth Token 狀態
  if (oauthStatus.tokens && oauthStatus.tokens.length > 0) {
    const invalidTokens = oauthStatus.tokens.filter(t => !t.valid);
    if (invalidTokens.length > 0) {
      quotaWarnings += `
        <div class="alert-banner" style="display: flex; margin-bottom: 15px;">
          <i data-lucide="alert-triangle" class="alert-icon"></i>
          <div style="flex: 1;">
            <strong>⚠️ Claude OAuth Token 已過期</strong>
            <p style="margin: 5px 0 0 0; font-size: 0.9rem;">檢測到 ${invalidTokens.length} 個失效的 OAuth token，請重新授權。</p>
          </div>
          <button class="btn-alert-action" onclick="alert('請在終端機執行：openclaw models auth setup-token --provider anthropic')">重新授權</button>
        </div>
      `;
    }
  }
  
  // Google Gemini 額度狀態
  if (quotaUsage.google_gemini && quotaUsage.google_gemini.length > 0) {
    const gemini = quotaUsage.google_gemini[0];
    const proLeft = gemini.models?.pro || 0;
    const flashLeft = gemini.models?.flash || 0;
    
    if (proLeft < 20 || flashLeft < 20) {
      quotaWarnings += `
        <div class="alert-banner" style="display: flex; margin-bottom: 15px; background: rgba(255, 170, 0, 0.2); border-color: #ffaa00;">
          <i data-lucide="zap" class="alert-icon" style="stroke: #ffaa00;"></i>
          <div style="flex: 1;">
            <strong style="color: #ffaa00;">⚡ Gemini API 額度偏低</strong>
            <p style="margin: 5px 0 0 0; font-size: 0.9rem; color: #fff;">Pro: ${proLeft}% 剩餘 | Flash: ${flashLeft}% 剩餘</p>
          </div>
        </div>
      `;
    } else {
      quotaWarnings += `
        <div style="background: rgba(0, 255, 136, 0.1); border-left: 4px solid #00ff88; padding: 12px 20px; border-radius: 8px; margin-bottom: 15px; display: flex; align-items: center; gap: 15px;">
          <i data-lucide="check-circle" style="width: 24px; height: 24px; stroke: #00ff88;"></i>
          <div style="flex: 1;">
            <strong style="color: #00ff88;">✅ Gemini API 額度充足</strong>
            <p style="margin: 5px 0 0 0; font-size: 0.85rem; color: #fff;">Pro: ${proLeft}% 剩餘 | Flash: ${flashLeft}% 剩餘</p>
          </div>
        </div>
      `;
    }
  }
  
  // OpenAI 額度狀態
  if (quotaUsage.openai && quotaUsage.openai.length > 0) {
    const openai = quotaUsage.openai[0];
    if (openai.daily && openai.daily.percent_left < 20) {
      quotaWarnings += `
        <div class="alert-banner" style="display: flex; margin-bottom: 15px; background: rgba(255, 170, 0, 0.2); border-color: #ffaa00;">
          <i data-lucide="zap" class="alert-icon" style="stroke: #ffaa00;"></i>
          <div style="flex: 1;">
            <strong style="color: #ffaa00;">⚡ OpenAI 每日額度偏低</strong>
            <p style="margin: 5px 0 0 0; font-size: 0.9rem; color: #fff;">剩餘 ${openai.daily.percent_left}% | 重置於 ${openai.daily.reset_in}</p>
          </div>
        </div>
      `;
    }
  }
  
  // Cooldown 狀態
  if (rateLimits.rate_limits && rateLimits.rate_limits.length > 0) {
    const activeCooldowns = rateLimits.rate_limits.filter(rl => {
      if (!rl.cooldown_until) return false;
      return new Date(rl.cooldown_until) > new Date();
    });
    
    if (activeCooldowns.length > 0) {
      const cooldownItems = activeCooldowns.map(rl => {
        const cooldownEnd = new Date(rl.cooldown_until);
        const now = new Date();
        const remainingMs = cooldownEnd - now;
        const remainingMin = Math.ceil(remainingMs / 60000);
        const resetTime = cooldownEnd.toLocaleTimeString('zh-TW', { hour: '2-digit', minute: '2-digit' });
        return `<strong>${rl.provider}</strong>: ${remainingMin}分鐘後解除 (${resetTime})`;
      }).join('<br>');
      
      quotaWarnings += `
        <div class="alert-banner" style="display: flex; margin-bottom: 15px; background: rgba(255, 100, 100, 0.2); border-color: #ff6464;">
          <i data-lucide="clock" class="alert-icon" style="stroke: #ff6464;"></i>
          <div style="flex: 1;">
            <strong style="color: #ff6464;">⏳ API 冷卻中</strong>
            <p style="margin: 5px 0 0 0; font-size: 0.9rem; color: #fff;">${cooldownItems}</p>
          </div>
        </div>
      `;
    }
  }
  
  // 過濾選項
  const filterBtns = `
    <div style="margin-bottom: 20px; display: flex; gap: 10px;">
      <button class="btn-select ${filter === 'all' ? 'active' : ''}" onclick="renderOverview('all')" style="padding: 8px 16px; ${filter === 'all' ? 'background: #00ff88; color: #000;' : ''}">全部</button>
      <button class="btn-select ${filter === 'dm' ? 'active' : ''}" onclick="renderOverview('dm')" style="padding: 8px 16px; ${filter === 'dm' ? 'background: #00ff88; color: #000;' : ''}">僅私聊</button>
      <button class="btn-select ${filter === 'group' ? 'active' : ''}" onclick="renderOverview('group')" style="padding: 8px 16px; ${filter === 'group' ? 'background: #00ff88; color: #000;' : ''}">僅群組</button>
      <span style="margin-left: auto; color: #888; align-self: center;">📊 ${live.period || '過去 24 小時'}</span>
    </div>
  `;
  
  content.innerHTML = quotaWarnings + filterBtns + `
    <div class="stats-grid">
      <div class="stat-card">
        <h3>${filter === 'all' ? '總消耗' : filter === 'dm' ? '私聊消耗' : '群組消耗'} <span style="color: #00ff88; font-size: 0.7rem;">●即時</span></h3>
        <div class="value">${formatNumber(todayTokens)}</div>
        <div class="label">tokens (~$${estimatedCost})</div>
      </div>
      <div class="stat-card">
        <h3>本週消耗</h3>
        <div class="value">${formatNumber(week.total_tokens)}</div>
        <div class="label">tokens ($${week.estimated_cost.toFixed(2)})</div>
      </div>
      <div class="stat-card">
        <h3>本月消耗</h3>
        <div class="value">${formatNumber(month.total_tokens)}</div>
        <div class="label">tokens ($${month.estimated_cost.toFixed(2)})</div>
      </div>
      <div class="stat-card">
        <h3>活躍 Sessions</h3>
        <div class="value">${live.sessions_count || 0}</div>
        <div class="label">個</div>
      </div>
    </div>
    
    <div class="section">
      <h2><i data-lucide="trending-up" style="width: 24px; height: 24px; stroke: currentColor; vertical-align: middle; margin-right: 8px;"></i>Token 消耗分佈</h2>
      <div class="chart-container">
        <div style="margin-bottom: 15px;">
          <strong>Input:</strong> ${formatNumber(today.total_tokens_in)} tokens
          <div class="progress-bar">
            <div class="progress-fill" style="width: ${(today.total_tokens_in / today.total_tokens * 100) || 0}%">
              ${((today.total_tokens_in / today.total_tokens * 100) || 0).toFixed(1)}%
            </div>
          </div>
        </div>
        <div>
          <strong>Output:</strong> ${formatNumber(today.total_tokens_out)} tokens
          <div class="progress-bar">
            <div class="progress-fill" style="width: ${(today.total_tokens_out / today.total_tokens * 100) || 0}%">
              ${((today.total_tokens_out / today.total_tokens * 100) || 0).toFixed(1)}%
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="section">
      <h2><i data-lucide="message-circle" style="width: 24px; height: 24px; stroke: currentColor; vertical-align: middle; margin-right: 8px;"></i>Session 類型分佈</h2>
      <div class="chart-container" style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px;">
        ${['dm', 'group', 'cron', 'other'].map(type => {
          const tokens = live.by_type?.[type] || 0;
          const percentage = todayTokens > 0 ? ((tokens / todayTokens) * 100).toFixed(1) : 0;
          let label, icon, desc;
          switch(type) {
            case 'dm':
              label = '私聊';
              icon = '💬';
              desc = '你與我的對話';
              break;
            case 'group':
              label = '群組';
              icon = '👥';
              desc = '群組討論';
              break;
            case 'cron':
              label = 'Cron';
              icon = '⏰';
              desc = '自動排程任務';
              break;
            default:
              label = '其他';
              icon = '📝';
              desc = 'Main/Isolated sessions';
          }
          return `
            <div class="stat-card" style="text-align: center;">
              <div style="font-size: 2rem; margin-bottom: 10px;" title="${desc}">${icon}</div>
              <strong>${label}</strong>
              <div style="font-size: 0.8rem; color: #888; margin-bottom: 10px;">${desc}</div>
              <div style="font-size: 1.2rem; margin: 10px 0;">${formatNumber(tokens)}</div>
              <div style="color: #888; font-size: 0.9rem;">${percentage}%</div>
            </div>
          `;
        }).join('')}
      </div>
    </div>
    
    <div class="section">
      <h2><i data-lucide="cpu" style="width: 24px; height: 24px; stroke: currentColor; vertical-align: middle; margin-right: 8px;"></i>模型使用分佈 <span style="color: #00d4ff; font-size: 0.8rem;">●歷史累計</span></h2>
      <div class="chart-container">
        ${(modelAnalytics.models || []).length > 0 
          ? modelAnalytics.models.map(m => {
              return `
                <div style="margin-bottom: 10px;">
                  <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                    <span class="status-badge status-ok">${m.model}</span>
                    <span>${formatNumber(m.total_tokens)} tokens (${m.percentage}%)</span>
                  </div>
                  <div class="progress-bar">
                    <div class="progress-fill" style="width: ${Math.min(m.percentage, 100)}%; background: linear-gradient(90deg, #00ff88, #00d4ff);"></div>
                  </div>
                </div>
              `;
            }).join('')
          : '<span style="color: #888;">暫無數據</span>'
        }
      </div>
    </div>
  `;
  lucide.createIcons(); // 初始化新加入的 icons
}

// 渲染模型頁
async function renderModels() {
  const data = await fetch(`${API_BASE}/models`).then(r => r.json());
  
  const content = document.getElementById('content');
  content.innerHTML = `
    <div class="section">
      <h2><i data-lucide="bar-chart-3" style="width: 24px; height: 24px; stroke: currentColor; vertical-align: middle; margin-right: 8px;"></i>模型配額狀態</h2>
      <div class="table-wrapper">
        <table>
        <thead>
          <tr>
            <th>Provider</th>
            <th>模型</th>
            <th>剩餘配額</th>
            <th>重置時間</th>
            <th>狀態</th>
          </tr>
        </thead>
        <tbody>
          ${data.models.map(m => `
            <tr>
              <td>${m.provider}</td>
              <td>${m.model}</td>
              <td>
                <div class="progress-bar">
                  <div class="progress-fill" style="width: ${m.quota_left}%; background: ${getQuotaColor(m.quota_left)}">
                    ${m.quota_left}%
                  </div>
                </div>
              </td>
              <td>${m.reset_time || 'N/A'}</td>
              <td><span class="status-badge ${getQuotaStatus(m.quota_left)}">${getQuotaLabel(m.quota_left)}</span></td>
            </tr>
          `).join('')}
        </tbody>
      </table>
      </div>
    </div>
  `;
}

// 渲染速率限制頁
async function renderRateLimits() {
  const data = await fetch(`${API_BASE}/rate-limits`).then(r => r.json());
  
  const content = document.getElementById('content');
  content.innerHTML = `
    <div class="section">
      <h2><i data-lucide="zap" style="width: 24px; height: 24px; stroke: currentColor; vertical-align: middle; margin-right: 8px;"></i>速率限制監控</h2>
      <div class="table-wrapper">
        <table>
        <thead>
          <tr>
            <th>Provider</th>
            <th>RPM</th>
            <th>TPM</th>
            <th>Cooldown</th>
            <th>更新時間</th>
          </tr>
        </thead>
        <tbody>
          ${data.rate_limits.map(rl => `
            <tr>
              <td>${rl.provider}</td>
              <td>${rl.rpm}</td>
              <td>${rl.tpm}</td>
              <td>${rl.cooldown_until || 'N/A'}</td>
              <td>${formatTime(rl.timestamp)}</td>
            </tr>
          `).join('')}
        </tbody>
      </table>
      </div>
    </div>
    
    <div class="section">
      <h2><i data-lucide="info" style="width: 24px; height: 24px; stroke: currentColor; vertical-align: middle; margin-right: 8px;"></i>說明</h2>
      <div class="chart-container">
        <p><strong>RPM (Requests Per Minute)</strong>: 每分鐘請求數限制</p>
        <p><strong>TPM (Tokens Per Minute)</strong>: 每分鐘 Token 數限制</p>
        <p><strong>Cooldown</strong>: 速率限制觸發後的冷卻時間</p>
      </div>
    </div>
  `;
  lucide.createIcons(); // 初始化新加入的 icons
}

// 渲染歷史頁
async function renderHistory() {
  const data = await fetch(`${API_BASE}/history?days=7`).then(r => r.json());
  
  const content = document.getElementById('content');
  content.innerHTML = `
    <div class="section">
      <h2><i data-lucide="calendar" style="width: 24px; height: 24px; stroke: currentColor; vertical-align: middle; margin-right: 8px;"></i>最近 7 天用量</h2>
      <div class="table-wrapper">
        <table>
        <thead>
          <tr>
            <th>日期</th>
            <th>Total Tokens</th>
            <th>Input</th>
            <th>Output</th>
            <th>請求數</th>
          </tr>
        </thead>
        <tbody>
          ${data.history.map(h => `
            <tr>
              <td>${h.date}</td>
              <td><strong>${formatNumber(h.total_tokens)}</strong></td>
              <td>${formatNumber(h.tokens_in)}</td>
              <td>${formatNumber(h.tokens_out)}</td>
              <td>${h.requests}</td>
            </tr>
          `).join('')}
        </tbody>
      </table>
      </div>
    </div>
  `;
  lucide.createIcons(); // 初始化新加入的 icons
}

// 渲染成本頁
async function renderCost() {
  const [today, week, month] = await Promise.all([
    fetch(`${API_BASE}/cost?period=today`).then(r => r.json()),
    fetch(`${API_BASE}/cost?period=week`).then(r => r.json()),
    fetch(`${API_BASE}/cost?period=month`).then(r => r.json())
  ]);
  
  const content = document.getElementById('content');
  content.innerHTML = `
    <div class="stats-grid">
      <div class="stat-card">
        <h3>今日成本</h3>
        <div class="value">$${today.total_cost}</div>
      </div>
      <div class="stat-card">
        <h3>本週成本</h3>
        <div class="value">$${week.total_cost}</div>
      </div>
      <div class="stat-card">
        <h3>本月成本</h3>
        <div class="value">$${month.total_cost}</div>
      </div>
      <div class="stat-card">
        <h3>預估月底</h3>
        <div class="value">$${(parseFloat(month.total_cost) * 30 / new Date().getDate()).toFixed(2)}</div>
      </div>
    </div>
    
    <div class="section">
      <h2><i data-lucide="dollar-sign" style="width: 24px; height: 24px; stroke: currentColor; vertical-align: middle; margin-right: 8px;"></i>成本分解（本月）</h2>
      <div class="table-wrapper">
        <table>
        <thead>
          <tr>
            <th>模型</th>
            <th>Input Tokens</th>
            <th>Output Tokens</th>
            <th>成本</th>
          </tr>
        </thead>
        <tbody>
          ${month.breakdown.map(b => `
            <tr>
              <td>${b.model}</td>
              <td>${formatNumber(b.tokens_in)}</td>
              <td>${formatNumber(b.tokens_out)}</td>
              <td><strong>$${b.cost}</strong></td>
            </tr>
          `).join('')}
        </tbody>
      </table>
      </div>
    </div>
  `;
}

// 工具函數
function formatNumber(num) {
  if (num === undefined || num === null || isNaN(num)) {
    return '0';
  }
  if (num >= 1000000) {
    return (num / 1000000).toFixed(2) + 'M';
  } else if (num >= 1000) {
    return (num / 1000).toFixed(2) + 'k';
  }
  return num.toString();
}

function formatTime(timestamp) {
  if (!timestamp) return 'N/A';
  const date = new Date(timestamp);
  return date.toLocaleString('zh-TW');
}

function getQuotaColor(percent) {
  if (percent >= 70) return 'linear-gradient(90deg, #28a745 0%, #20c997 100%)';
  if (percent >= 30) return 'linear-gradient(90deg, #ffc107 0%, #fd7e14 100%)';
  return 'linear-gradient(90deg, #dc3545 0%, #c82333 100%)';
}

function getQuotaStatus(percent) {
  if (percent >= 70) return 'status-ok';
  if (percent >= 30) return 'status-warning';
  return 'status-error';
}

function getQuotaLabel(percent) {
  if (percent >= 70) return '正常';
  if (percent >= 30) return '注意';
  return '警告';
}

// ==================== 控制面板功能 ====================

// 更新頂部控制面板
async function updateControlPanel() {
  try {
    const config = await fetch(`${API_BASE}/config`).then(r => r.json());
    
    // 更新當前模型
    const currentModelEl = document.getElementById('current-model');
    if (currentModelEl) {
      currentModelEl.textContent = config.current_model || '未知';
    }
    
    // 更新 Gateway 狀態
    const statusDot = document.getElementById('gateway-status');
    if (statusDot) {
      statusDot.className = 'status-dot pulsing ' + (config.gateway_running ? 'status-ok' : 'status-error');
    }
    
    // 更新配額
    const quotaPercent = config.quota_remaining || 0;
    const quotaPercentEl = document.getElementById('quota-percent');
    const quotaProgress = document.getElementById('quota-progress');
    
    if (quotaPercentEl) {
      quotaPercentEl.textContent = quotaPercent + '%';
    }
    
    if (quotaProgress) {
      const strokeColor = quotaPercent >= 70 ? '#28a745' : quotaPercent >= 30 ? '#ffc107' : '#dc3545';
      quotaProgress.setAttribute('stroke', strokeColor);
      quotaProgress.setAttribute('stroke-dasharray', `${quotaPercent}, 100`);
    }
    
    // 檢查是否有警告
    if (config.warnings && config.warnings.length > 0) {
      showAlertBanner(config.warnings[0]);
    } else {
      hideAlertBanner();
    }
  } catch (error) {
    console.error('更新控制面板失敗:', error);
  }
}

// 倒數計時器
function startCountdown() {
  const timerEl = document.getElementById('countdown-timer');
  
  countdownInterval = setInterval(() => {
    countdownValue -= 0.1;
    if (countdownValue <= 0) {
      countdownValue = 5.0; // 配合 5 秒刷新間隔
    }
    if (timerEl) {
      timerEl.textContent = countdownValue.toFixed(1) + 's';
    }
  }, 100);
}

// 顯示警告橫幅
function showAlertBanner(message) {
  const banner = document.getElementById('alert-banner');
  const messageEl = document.getElementById('alert-message');
  
  if (banner && messageEl) {
    messageEl.textContent = message;
    banner.style.display = 'flex';
  }
}

// 隱藏警告橫幅
function hideAlertBanner() {
  const banner = document.getElementById('alert-banner');
  if (banner) {
    banner.style.display = 'none';
  }
}

// ==================== Toast 通知系統 ====================

function showToast(type, title, message, duration = 3000) {
  const container = document.getElementById('toast-container');
  if (!container) return;
  
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  
  const icons = {
    success: '<i data-lucide="check-circle"></i>',
    warning: '<i data-lucide="alert-triangle"></i>',
    error: '<i data-lucide="x-circle"></i>',
    info: '<i data-lucide="info"></i>'
  };
  
  toast.innerHTML = `
    <span class="toast-icon">${icons[type] || icons.info}</span>
    <div class="toast-content">
      <strong>${title}</strong>
      <p>${message}</p>
    </div>
    <button class="toast-close" onclick="this.parentElement.remove()"><i data-lucide="x"></i></button>
  `;
  
  container.appendChild(toast);
  lucide.createIcons(); // 初始化新加入的 icons
  
  // 自動移除
  setTimeout(() => {
    toast.style.animation = 'slideInRight 0.3s reverse';
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

// ==================== 模型切換 Modal ====================

async function openModelSwitcher() {
  const modal = document.getElementById('modelSwitcherModal');
  const modalBody = document.getElementById('modal-body');
  
  if (!modal || !modalBody) return;
  
  modal.classList.add('active');
  modalBody.innerHTML = '<div class="loading">載入模型列表...</div>';
  
  try {
    const [config, modelsData] = await Promise.all([
      fetch(`${API_BASE}/config`).then(r => r.json()),
      fetch(`${API_BASE}/models`).then(r => r.json())
    ]);
    
    const currentModel = config.current_model;
    
    // 使用後端返回的實際可切換模型列表
    const allModels = modelsData.models || [];
    
    if (allModels.length === 0) {
      modalBody.innerHTML = '<div class="error">無可用模型</div>';
      return;
    }
    
    // 生成模型卡片
    let html = '<div class="model-grid">';
    
    for (const model of allModels) {
      const isCurrent = model.is_current || model.full_name === currentModel;
      const isConfigured = model.is_configured;
      
      const cardClass = isCurrent ? 'model-card current' : 'model-card available';
      
      html += `
        <div class="${cardClass}">
          <div class="model-header">
            ${isCurrent ? '<i data-lucide="star" style="width: 20px; height: 20px; stroke: #ff0080; fill: #ff0080;"></i>' : ''}
            <strong>${model.full_name}</strong>
            ${isCurrent ? '<span class="status-badge status-ok" style="margin-left: auto; font-size: 0.7rem;">當前</span>' : ''}
          </div>
          
          <div class="model-stats">
            <div class="model-stat">
              <span>類型</span>
              <strong style="color: ${isConfigured ? '#00ff88' : '#888'};">${isConfigured ? 'Configured' : 'Fallback'}</strong>
            </div>
            <div class="model-stat">
              <span>Provider</span>
              <strong style="font-size: 0.8rem;">${model.provider}</strong>
            </div>
          </div>
          
          <button class="btn-select" 
                  onclick="switchModel('${model.full_name}')"
                  ${isCurrent ? 'disabled' : ''}>
            ${isCurrent ? '當前使用中' : '切換到此模型'}
          </button>
        </div>
      `;
    }
    
    html += '</div>';
    
    // 智能推薦（推薦 configured 且非當前的模型）
    const recommended = allModels.find(m => m.is_configured && !m.is_current);
    if (recommended) {
      html += `
        <div class="recommendation">
          <i data-lucide="lightbulb" class="recommendation-icon"></i>
          <div style="flex: 1;">
            <strong>智能推薦</strong>
            <p>${recommended.full_name} 已配置可用，建議優先使用</p>
          </div>
          <button class="btn-primary-sm" onclick="switchModel('${recommended.full_name}')">立即切換</button>
        </div>
      `;
    }
    
    modalBody.innerHTML = html;
    lucide.createIcons(); // 初始化新加入的 icons
  } catch (error) {
    modalBody.innerHTML = `<div class="error">載入失敗：${error.message}</div>`;
  }
}

function closeModelSwitcher() {
  const modal = document.getElementById('modelSwitcherModal');
  if (modal) {
    modal.classList.remove('active');
  }
}

// 切換模型
async function switchModel(modelName) {
  const btn = event.target;
  btn.classList.add('loading');
  btn.textContent = '切換中...';
  btn.disabled = true;
  
  try {
    const response = await fetch(`${API_BASE}/switch-model`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ model: modelName })
    });
    
    const result = await response.json();
    
    if (response.ok) {
      showToast('success', '✅ 切換成功', `已切換到 ${modelName}，下一條對話將使用新模型`);
      closeModelSwitcher();
      
      // 強制刷新配置（清除快取）
      await fetch(`${API_BASE}/config?refresh=true`).then(r => r.json());
      
      // 立即更新控制面板
      await updateControlPanel();
      
      // 如果在總覽頁面，也刷新
      if (currentPage === 'overview') {
        await renderOverview(currentFilter);
      }
    } else {
      throw new Error(result.error || '切換失敗');
    }
  } catch (error) {
    showToast('error', '切換失敗', error.message);
    btn.classList.remove('loading');
    btn.textContent = '切換到此模型';
    btn.disabled = false;
  }
}

// 格式化 Cooldown 時間
function formatCooldown(seconds) {
  if (seconds <= 0) return '0s';
  
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;
  
  if (hours > 0) return `${hours}h${minutes}m`;
  if (minutes > 0) return `${minutes}m${secs}s`;
  return `${secs}s`;
}

// 渲染配額詳情頁
async function renderQuota() {
  const [data, rateLimits, modelAnalytics, costData] = await Promise.all([
    fetch(`${API_BASE}/quota-status`).then(r => r.json()),
    fetch(`${API_BASE}/rate-limits`).then(r => r.json()).catch(() => ({ rate_limits: [] })),
    fetch(`${API_BASE}/model-analytics?period=today`).then(r => r.json()).catch(() => ({ models: [] })),
    fetch(`${API_BASE}/cost?period=today`).then(r => r.json()).catch(() => ({ breakdown: [] }))
  ]);
  const content = document.getElementById('content');
  
  // 按 provider 分組用量
  const usageByProvider = {};
  (modelAnalytics.models || []).forEach(m => {
    const provider = m.provider || 'unknown';
    if (!usageByProvider[provider]) {
      usageByProvider[provider] = { tokens: 0, models: [], cost: 0 };
    }
    usageByProvider[provider].tokens += m.total_tokens;
    usageByProvider[provider].models.push(m);
  });
  
  // 計算成本（從 costData）
  (costData.breakdown || []).forEach(b => {
    const provider = b.model.split('/')[0] || 'unknown';
    if (usageByProvider[provider]) {
      usageByProvider[provider].cost += parseFloat(b.cost) || 0;
    }
  });
  
  let html = '';
  
  // Cooldown 狀態區塊
  const activeCooldowns = (rateLimits.rate_limits || []).filter(rl => {
    if (!rl.cooldown_until) return false;
    return new Date(rl.cooldown_until) > new Date();
  });
  
  if (activeCooldowns.length > 0) {
    html += `
      <div class="section" style="margin-bottom: 20px;">
        <h2><i data-lucide="clock" style="width: 24px; height: 24px; stroke: #ff6464; vertical-align: middle; margin-right: 8px;"></i>冷卻中的 API</h2>
        <div class="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Provider</th>
                <th>剩餘時間</th>
                <th>重置時間</th>
                <th>狀態</th>
              </tr>
            </thead>
            <tbody>
    `;
    
    activeCooldowns.forEach(rl => {
      const cooldownEnd = new Date(rl.cooldown_until);
      const now = new Date();
      const remainingMs = cooldownEnd - now;
      const remainingMin = Math.max(0, Math.ceil(remainingMs / 60000));
      const resetTime = cooldownEnd.toLocaleTimeString('zh-TW', { hour: '2-digit', minute: '2-digit' });
      const resetDate = cooldownEnd.toLocaleDateString('zh-TW', { month: 'short', day: 'numeric' });
      
      html += `
        <tr>
          <td><strong>${rl.provider}</strong></td>
          <td><span style="color: #ff6464; font-weight: bold;">${remainingMin} 分鐘</span></td>
          <td>${resetDate} ${resetTime}</td>
          <td><span class="status-badge status-warning">⏳ 冷卻中</span></td>
        </tr>
      `;
    });
    
    html += `
            </tbody>
          </table>
        </div>
      </div>
    `;
  }
  
  html += '<div class="quota-details">';
  
  if (!data.providers || Object.keys(data.providers).length === 0) {
    content.innerHTML = '<div class="error">無法獲取配額信息</div>';
    return;
  }
  
  // 建立 cooldown 查詢表
  const cooldownMap = {};
  (rateLimits.rate_limits || []).forEach(rl => {
    if (rl.cooldown_until) {
      cooldownMap[rl.provider] = rl.cooldown_until;
    }
  });
  
  // 建議優先順序
  const recommendations = {
    'google': { priority: 1, status: '✅ 最穩定' },
    'google-antigravity': { priority: 2, status: '⚠️ 監控中' },
    'openai-codex': { priority: 3, status: '❌ 需切換' }
  };
  
  Object.entries(data.providers).forEach(([provider, models]) => {
    const rec = recommendations[provider] || { priority: 99, status: '❓' };
    const cooldownUntil = cooldownMap[provider];
    const isInCooldown = cooldownUntil && new Date(cooldownUntil) > new Date();
    const providerUsage = usageByProvider[provider] || { tokens: 0, models: [], cost: 0 };
    
    let statusColor = rec.priority === 1 ? '#00ff88' : rec.priority === 2 ? '#ffd700' : '#ff4444';
    let statusText = rec.status;
    
    if (isInCooldown) {
      statusColor = '#ff6464';
      const cooldownEnd = new Date(cooldownUntil);
      const remainingMin = Math.ceil((cooldownEnd - new Date()) / 60000);
      statusText = `⏳ 冷卻中 (${remainingMin}分鐘)`;
    }
    
    // 判斷認證類型
    const authTypes = [...new Set(models.map(m => m.authType || 'unknown'))];
    const authLabel = authTypes.includes('oauth') ? '🔐 OAuth (訂閱制)' : 
                      authTypes.includes('static') ? '🔑 API Key' : '❓ 未知';
    const isFree = authTypes.includes('oauth') || authTypes.includes('static') && provider.includes('antigravity');
    
    html += `
      <div class="quota-provider" style="border-color: ${statusColor}">
        <h3>${provider} <span style="color: ${statusColor}">${statusText}</span></h3>
        
        <!-- 用量統計 -->
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 15px; padding: 15px; background: rgba(0,0,0,0.2); border-radius: 8px;">
          <div style="text-align: center;">
            <div style="font-size: 0.8rem; color: #888;">認證類型</div>
            <div style="font-size: 1rem; margin-top: 5px;">${authLabel}</div>
          </div>
          <div style="text-align: center;">
            <div style="font-size: 0.8rem; color: #888;">今日用量</div>
            <div style="font-size: 1.2rem; font-weight: bold; margin-top: 5px; color: #00d4ff;">${formatNumber(providerUsage.tokens)}</div>
          </div>
          <div style="text-align: center;">
            <div style="font-size: 0.8rem; color: #888;">成本</div>
            <div style="font-size: 1.2rem; font-weight: bold; margin-top: 5px; color: ${isFree ? '#00ff88' : '#ffd700'};">${isFree ? '$0 (免費)' : '$' + (providerUsage.cost || 0).toFixed(2)}</div>
          </div>
        </div>
        
        <div class="table-wrapper">
          <table class="quota-table">
            <thead>
              <tr>
                <th>Profile / 模型</th>
                <th>類型</th>
                <th>配額</th>
                <th>狀態</th>
              </tr>
            </thead>
            <tbody>
    `;
    
    models.forEach(m => {
      let statusEmoji = m.status === 'ok' ? '✅' : '⏳';
      const modelName = m.profile || m.full_name || m.model || 'unknown';
      
      // 認證類型
      let authTypeLabel = '—';
      if (m.authType === 'oauth') authTypeLabel = '🔐 OAuth';
      else if (m.authType === 'static') authTypeLabel = '🔑 API Key';
      else if (m.email) authTypeLabel = `🔐 ${m.email}`;
      
      // 配額
      let quota;
      if (m.quota !== undefined) {
        const quotaColor = m.quota > 70 ? '#00ff88' : m.quota > 30 ? '#ffd700' : '#ff4444';
        quota = `<span style="color: ${quotaColor}; font-weight: bold;">${m.quota}%</span>`;
      } else {
        quota = '<span style="color: #888">—</span>';
      }
      
      let statusLabel = m.status === 'ok' ? '可用' : m.status === 'expired' ? '已過期' : 'Cooldown';
      
      if (isInCooldown) {
        statusEmoji = '⏳';
        statusLabel = '冷卻中';
      }
      
      html += `
        <tr>
          <td><code>${modelName}</code></td>
          <td>${authTypeLabel}</td>
          <td>${quota}</td>
          <td>${statusEmoji} ${statusLabel}</td>
        </tr>
      `;
    });
    
    html += `
          </tbody>
        </table>
        </div>
      </div>
    `;
  });
  
  html += '</div>';
  content.innerHTML = html;
  lucide.createIcons();
}

async function renderModelAnalytics() {
  const content = document.getElementById('content');
  content.innerHTML = '<div class="loading">載入模型分析...</div>';
  
  try {
    const period = 'today'; // 可以後續改為可選
    const data = await fetch(`${API_BASE}/model-analytics?period=${period}`).then(r => r.json());
    
    if (!data.models || data.models.length === 0) {
      content.innerHTML = '<div class="error">暫無數據</div>';
      return;
    }
    
    let html = '<div class="model-analytics">';
    
    // 統計卡片（使用現有的 stats-grid）
    html += `
      <div class="stats-grid">
        <div class="stat-card">
          <h3>總 Token 用量</h3>
          <div class="value">${formatNumber(data.total_tokens)}</div>
          <div class="label">tokens</div>
        </div>
        <div class="stat-card">
          <h3>模型數量</h3>
          <div class="value">${data.models.length}</div>
          <div class="label">個</div>
        </div>
        <div class="stat-card">
          <h3>最常用模型</h3>
          <div class="value" style="font-size: 1rem;">${data.models[0]?.model.split('/')[1] || 'N/A'}</div>
          <div class="label">${((data.models[0]?.percentage) || 0)}%</div>
        </div>
        <div class="stat-card">
          <h3>總請求數</h3>
          <div class="value">${data.models.reduce((sum, m) => sum + (m.requests || 0), 0)}</div>
          <div class="label">次</div>
        </div>
      </div>
    `;
    
    // 模型用量表格
    html += `
      <div class="model-usage-table">
        <h3>模型用量詳情</h3>
        <table class="usage-table">
          <thead>
            <tr>
              <th>模型</th>
              <th>Provider</th>
              <th>Input Tokens</th>
              <th>Output Tokens</th>
              <th>總計</th>
              <th>占比</th>
            </tr>
          </thead>
          <tbody>
    `;
    
    data.models.forEach(m => {
      html += `
        <tr>
          <td><code>${m.model}</code></td>
          <td>${m.provider}</td>
          <td>${formatNumber(m.tokens_in)}</td>
          <td>${formatNumber(m.tokens_out)}</td>
          <td><strong>${formatNumber(m.total_tokens)}</strong></td>
          <td>
            <div class="progress-bar">
              <div class="progress-fill" style="width: ${m.percentage}%; background: linear-gradient(90deg, #00ff88, #00d4ff);"></div>
            </div>
            <span style="margin-left: 10px;">${m.percentage}%</span>
          </td>
        </tr>
      `;
    });
    
    html += `
          </tbody>
        </table>
      </div>
    `;
    
    html += '</div>';
    content.innerHTML = html;
    
    lucide.createIcons();
  } catch (error) {
    console.error('載入模型分析失敗:', error);
    content.innerHTML = '<div class="error">載入失敗</div>';
  }
}

function formatNumber(num) {
  return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}
