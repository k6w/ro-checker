
html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Jerry's Pizza Account Viewer</title>
    <style>
        :root {
            --bg-primary: #1a1a1a;
            --bg-secondary: #2d2d2d;
            --bg-card: #242424;
            --text-primary: #e9ecef;
            --text-secondary: #adb5bd;
            --border-color: #495057;
            --accent-color: #ff4757;
            --success-color: #2ecc71;
            --shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
            --font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }

        [data-theme="light"] {
            --bg-primary: #f0f2f5;
            --bg-secondary: #ffffff;
            --bg-card: #ffffff;
            --text-primary: #212529;
            --text-secondary: #6c757d;
            --border-color: #dee2e6;
            --accent-color: #dc3545;
            --success-color: #28a745;
            --shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }

        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: var(--font-family);
            background-color: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
            min-height: 100vh;
        }

        .header {
            background: var(--bg-secondary);
            border-bottom: 1px solid var(--border-color);
            padding: 1rem 0;
            position: sticky;
            top: 0;
            z-index: 100;
            box-shadow: var(--shadow);
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 1.5rem;
        }

        .header-content {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 1rem;
            flex-wrap: wrap;
        }

        .logo {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            font-weight: 700;
            font-size: 1.25rem;
            color: var(--accent-color);
        }

        .controls {
            display: flex;
            gap: 0.75rem;
            align-items: center;
            flex-wrap: wrap;
        }

        select, button, input {
            font-family: inherit;
            font-size: 0.9rem;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            border: 1px solid var(--border-color);
            background: var(--bg-card);
            color: var(--text-primary);
            outline: none;
            transition: all 0.2s;
        }

        select:focus, input:focus {
            border-color: var(--accent-color);
            box-shadow: 0 0 0 2px rgba(220, 53, 69, 0.2);
        }

        button {
            cursor: pointer;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        button:hover {
            background: var(--bg-secondary);
            border-color: var(--text-secondary);
        }

        .btn-primary {
            background: var(--accent-color);
            color: white;
            border: none;
        }

        .btn-primary:hover {
            background: #c0392b;
            opacity: 0.9;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 1rem;
            margin: 2rem 0;
        }

        .stat-card {
            background: var(--bg-card);
            padding: 1.25rem;
            border-radius: 8px;
            border: 1px solid var(--border-color);
        }

        .stat-label {
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: var(--text-secondary);
            margin-bottom: 0.25rem;
        }

        .stat-value {
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--text-primary);
        }

        .toolbar {
            display: flex;
            gap: 1rem;
            margin-bottom: 1.5rem;
            flex-wrap: wrap;
            background: var(--bg-card);
            padding: 1rem;
            border-radius: 8px;
            border: 1px solid var(--border-color);
            align-items: center;
        }

        .search-box {
            flex: 1;
            min-width: 250px;
            position: relative;
        }

        .search-box input {
            width: 100%;
            padding-left: 2.5rem;
        }

        .search-icon {
            position: absolute;
            left: 0.75rem;
            top: 50%;
            transform: translateY(-50%);
            color: var(--text-secondary);
            pointer-events: none;
        }

        .accounts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 1.5rem;
        }

        .account-card {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            overflow: hidden;
            transition: transform 0.2s, box-shadow 0.2s;
        }

        .account-card:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow);
        }

        .card-header {
            padding: 1rem;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: rgba(0,0,0,0.02);
        }

        .account-name {
            font-weight: 600;
            font-size: 1.1rem;
        }

        .badge {
            background: var(--success-color);
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: 600;
        }

        .card-body {
            padding: 1rem;
        }

        .info-row {
            display: flex;
            justify-content: space-between;
            margin-bottom: 0.5rem;
            font-size: 0.9rem;
        }

        .info-label {
            color: var(--text-secondary);
        }

        .credentials-box {
            background: var(--bg-secondary);
            padding: 0.75rem;
            border-radius: 6px;
            margin-top: 1rem;
            font-family: monospace;
            font-size: 0.9rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border: 1px solid var(--border-color);
        }

        .pagination {
            display: flex;
            justify-content: center;
            gap: 0.5rem;
            margin: 2rem 0;
            align-items: center;
        }

        .pagination button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        .loading-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.5);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 1000;
            backdrop-filter: blur(2px);
        }

        .spinner {
            width: 40px;
            height: 40px;
            border: 3px solid rgba(255,255,255,0.3);
            border-radius: 50%;
            border-top-color: var(--accent-color);
            animation: spin 1s ease-in-out infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        .hidden { display: none !important; }
    </style>
</head>
<body data-theme="dark">
    <header class="header">
        <div class="container header-content">
            <div class="logo">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12,2C6.48,2,2,6.48,2,12s4.48,10,10,10s10-4.48,10-10S17.52,2,12,2z M12,20c-4.41,0-8-3.59-8-8s3.59-8,8-8s8,3.59,8,8 S16.41,20,12,20z M12.5,7H11v6l5.25,3.15l0.75-1.23l-4.5-2.67V7z"/>
                </svg>
                Jerry's Pizza Viewer
            </div>
            <div class="controls">
                <span id="file-info" style="color: var(--text-secondary); font-size: 0.9rem;">No file loaded</span>
                <select id="fileSelector" style="min-width: 200px;">
                    <option value="">Loading files...</option>
                </select>
                <button class="btn-primary" onclick="requestRefresh()">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M17.65,6.35C16.2,4.9,14.21,4,12,4c-4.42,0-7.99,3.58-7.99,8s3.57,8,7.99,8c3.73,0,6.84-2.55,7.73-6h-2.08 c-0.82,2.33-3.04,4-5.65,4c-3.31,0-6-2.69-6-6s2.69-6,6-6c1.66,0,3.14,0.69,4.22,1.78L13,11h7V4L17.65,6.35z"/></svg>
                    Refresh
                </button>
                <button onclick="toggleTheme()" id="themeBtn">☀️</button>
            </div>
        </div>
    </header>

    <main class="container">
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Accounts</div>
                <div class="stat-value" id="totalAccounts">0</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Total Balance</div>
                <div class="stat-value" id="totalBalance">0</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Avg Balance</div>
                <div class="stat-value" id="avgBalance">0</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Total Spent</div>
                <div class="stat-value" id="totalSpent">$0</div>
            </div>
        </div>

        <div class="toolbar">
            <div class="search-box">
                <span class="search-icon">🔍</span>
                <input type="text" id="searchInput" placeholder="Search accounts...">
            </div>
            <select id="sortBy" onchange="handleSort()">
                <option value="balance_desc">Balance (High to Low)</option>
                <option value="balance_asc">Balance (Low to High)</option>
                <option value="spent_desc">Total Spent (High to Low)</option>
                <option value="orders_desc">Orders (High to Low)</option>
                <option value="date_desc">Newest First</option>
            </select>
            <select id="itemsPerPage" onchange="handlePageSize()">
                <option value="12">12 per page</option>
                <option value="24">24 per page</option>
                <option value="48">48 per page</option>
                <option value="100">100 per page</option>
            </select>
        </div>

        <div id="accountsGrid" class="accounts-grid"></div>
        
        <div class="pagination" id="pagination">
            <button onclick="changePage(-1)" id="prevBtn">Previous</button>
            <span id="pageInfo">Page 1 of 1</span>
            <button onclick="changePage(1)" id="nextBtn">Next</button>
        </div>
    </main>

    <div id="loading" class="loading-overlay hidden">
        <div class="spinner"></div>
    </div>

    <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
    <script>
        // State
        let state = {
            accounts: [],
            filteredAccounts: [],
            currentPage: 1,
            itemsPerPage: 12,
            sortBy: 'balance_desc',
            theme: 'dark'
        };

        let socket;

        // Initialize
        document.addEventListener('DOMContentLoaded', () => {
            initWebSocket();
            loadFiles();
            setupEventListeners();
        });

        function initWebSocket() {
            socket = io();
            
            socket.on('connect', () => console.log('Connected to server'));
            
            socket.on('data_update', (data) => {
                showLoading(false);
                document.getElementById('file-info').textContent = data.file;
                state.accounts = data.accounts || [];
                applyFiltersAndSort();
                loadFiles(); // Refresh file list in case of new files
            });

            socket.on('error', (err) => {
                console.error('Socket error:', err);
                showLoading(false);
            });
        }

        function setupEventListeners() {
            document.getElementById('searchInput').addEventListener('input', (e) => {
                state.currentPage = 1;
                applyFiltersAndSort();
            });
        }

        async function loadFiles() {
            try {
                const res = await fetch('/api/files');
                const data = await res.json();
                const selector = document.getElementById('fileSelector');
                
                // Flatten and sort files
                const allFiles = [];
                Object.values(data.files).forEach(files => allFiles.push(...files));
                allFiles.sort((a, b) => parseInt(b.number) - parseInt(a.number));

                const currentVal = selector.value;
                selector.innerHTML = allFiles.length ? 
                    allFiles.map(f => `<option value="${f.file}">${f.website} #${f.number}</option>`).join('') :
                    '<option value="">No files found</option>';
                
                if (currentVal && allFiles.some(f => f.file === currentVal)) {
                    selector.value = currentVal;
                }

                selector.onchange = (e) => {
                    if (e.target.value) {
                        showLoading(true);
                        socket.emit('request_update', { filename: e.target.value });
                    }
                };
            } catch (e) {
                console.error('Error loading files:', e);
            }
        }

        function requestRefresh() {
            showLoading(true);
            const filename = document.getElementById('fileSelector').value;
            socket.emit('request_update', { filename });
        }

        function applyFiltersAndSort() {
            const query = document.getElementById('searchInput').value.toLowerCase();
            const sortType = document.getElementById('sortBy').value;

            // Filter
            state.filteredAccounts = state.accounts.filter(acc => {
                return (acc.firstName || '').toLowerCase().includes(query) ||
                       (acc.lastName || '').toLowerCase().includes(query) ||
                       (acc.email || '').toLowerCase().includes(query) ||
                       (acc.login || '').toLowerCase().includes(query);
            });

            // Sort
            state.filteredAccounts.sort((a, b) => {
                const getBalance = acc => acc.loyaltyBalance || acc.points || 0;
                
                switch(sortType) {
                    case 'balance_desc': return getBalance(b) - getBalance(a);
                    case 'balance_asc': return getBalance(a) - getBalance(b);
                    case 'spent_desc': return (b.totalSpent || 0) - (a.totalSpent || 0);
                    case 'orders_desc': return (b.orderCount || 0) - (a.orderCount || 0);
                    case 'date_desc': return new Date(b.registerDate || 0) - new Date(a.registerDate || 0);
                    default: return 0;
                }
            });

            updateStats();
            renderPage();
        }

        function updateStats() {
            const accs = state.filteredAccounts;
            const total = accs.length;
            
            if (total === 0) {
                ['totalAccounts', 'totalBalance', 'avgBalance', 'totalSpent'].forEach(id => 
                    document.getElementById(id).textContent = '0'
                );
                return;
            }

            const getBalance = acc => acc.loyaltyBalance || acc.points || 0;
            const totalBalance = accs.reduce((sum, acc) => sum + getBalance(acc), 0);
            const totalSpent = accs.reduce((sum, acc) => sum + (acc.totalSpent || 0), 0);

            document.getElementById('totalAccounts').textContent = total;
            document.getElementById('totalBalance').textContent = totalBalance.toLocaleString();
            document.getElementById('avgBalance').textContent = Math.round(totalBalance / total).toLocaleString();
            document.getElementById('totalSpent').textContent = '$' + totalSpent.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2});
        }

        function renderPage() {
            const grid = document.getElementById('accountsGrid');
            const start = (state.currentPage - 1) * state.itemsPerPage;
            const end = start + state.itemsPerPage;
            const pageItems = state.filteredAccounts.slice(start, end);
            const totalPages = Math.ceil(state.filteredAccounts.length / state.itemsPerPage);

            // Update pagination controls
            document.getElementById('pageInfo').textContent = `Page ${state.currentPage} of ${totalPages || 1}`;
            document.getElementById('prevBtn').disabled = state.currentPage <= 1;
            document.getElementById('nextBtn').disabled = state.currentPage >= totalPages;

            if (pageItems.length === 0) {
                grid.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 3rem; color: var(--text-secondary);">No accounts found matching your criteria</div>';
                return;
            }

            grid.innerHTML = pageItems.map(acc => {
                const balance = acc.loyaltyBalance || acc.points || 0;
                return `
                <div class="account-card">
                    <div class="card-header">
                        <div class="account-name">${acc.firstName} ${acc.lastName}</div>
                        <div class="badge">${balance} pts</div>
                    </div>
                    <div class="card-body">
                        <div class="info-row">
                            <span class="info-label">Email</span>
                            <span>${acc.email || 'N/A'}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Phone</span>
                            <span>${acc.mobilePhone || 'N/A'}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Orders</span>
                            <span>${acc.orderCount || 0}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Total Spent</span>
                            <span>$${(acc.totalSpent || 0).toFixed(2)}</span>
                        </div>
                        <div class="credentials-box">
                            <span>${acc.login}:${acc.password}</span>
                            <button onclick="copyToClipboard('${acc.login}:${acc.password}')" style="padding: 0.25rem 0.5rem; font-size: 0.8rem;">Copy</button>
                        </div>
                    </div>
                </div>
            `}).join('');
        }

        function handleSort() {
            state.sortBy = document.getElementById('sortBy').value;
            state.currentPage = 1;
            applyFiltersAndSort();
        }

        function handlePageSize() {
            state.itemsPerPage = parseInt(document.getElementById('itemsPerPage').value);
            state.currentPage = 1;
            renderPage();
        }

        function changePage(delta) {
            const totalPages = Math.ceil(state.filteredAccounts.length / state.itemsPerPage);
            const newPage = state.currentPage + delta;
            if (newPage >= 1 && newPage <= totalPages) {
                state.currentPage = newPage;
                renderPage();
                window.scrollTo({ top: 0, behavior: 'smooth' });
            }
        }

        function copyToClipboard(text) {
            navigator.clipboard.writeText(text).then(() => {
                // Could add a toast notification here
            });
        }

        function toggleTheme() {
            state.theme = state.theme === 'dark' ? 'light' : 'dark';
            document.body.setAttribute('data-theme', state.theme);
            document.getElementById('themeBtn').textContent = state.theme === 'dark' ? '☀️' : '🌙';
        }

        function showLoading(show) {
            const el = document.getElementById('loading');
            if (show) el.classList.remove('hidden');
            else el.classList.add('hidden');
        }
    </script>
</body>
</html>"""

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html_content)
