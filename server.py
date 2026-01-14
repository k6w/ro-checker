from flask import Flask, render_template, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import json
import os
from pathlib import Path
import time
from threading import Thread

app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), 'templates'))
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

def get_latest_success_file():
    """Get the most recent success file"""
    success_files = sorted(Path('.').glob('success_*.json'), key=lambda x: x.stat().st_mtime, reverse=True)
    return success_files[0] if success_files else None

def get_all_success_files():
    """Get all success files grouped by website"""
    files_by_website = {}
    
    for file in Path('.').glob('success_*.json'):
        # Extract website name from filename (success_<website>_<number>.json)
        parts = file.stem.split('_')
        if len(parts) >= 3:
            website = parts[1]
            number = parts[2]
            
            if website not in files_by_website:
                files_by_website[website] = []
            
            files_by_website[website].append({
                'number': number,
                'file': file.name,
                'website': website
            })
    
    # Sort by number within each website
    for website in files_by_website:
        files_by_website[website].sort(key=lambda x: int(x['number']), reverse=True)
    
    return files_by_website

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/accounts')
def get_accounts():
    """Get accounts from the latest success file"""
    latest_file = get_latest_success_file()
    if not latest_file:
        return jsonify({'accounts': [], 'total': 0, 'website': 'none'})
    
    try:
        with open(latest_file, 'r', encoding='utf-8') as f:
            accounts = json.load(f)
            website = accounts[0].get('website', 'unknown') if accounts else 'unknown'
            return jsonify({
                'accounts': accounts,
                'total': len(accounts),
                'file': latest_file.name,
                'website': website
            })
    except Exception as e:
        return jsonify({'error': str(e), 'accounts': [], 'total': 0, 'website': 'none'}), 500

@app.route('/api/accounts/<filename>')
def get_accounts_by_filename(filename):
    """Get accounts from a specific success file"""
    # Sanitize filename
    if not filename.endswith('.json') or not filename.startswith('success_'):
        return jsonify({'error': 'Invalid filename', 'accounts': [], 'total': 0}), 404
    
    if not os.path.exists(filename):
        return jsonify({'error': 'File not found', 'accounts': [], 'total': 0}), 404
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            accounts = json.load(f)
            
            # Extract website from accounts if available
            website = accounts[0].get('website', 'unknown') if accounts else 'unknown'
            
            return jsonify({
                'accounts': accounts,
                'total': len(accounts),
                'file': filename,
                'website': website
            })
    except Exception as e:
        return jsonify({'error': str(e), 'accounts': [], 'total': 0}), 500

@app.route('/api/files')
def get_files():
    """Get list of all success files grouped by website"""
    files = get_all_success_files()
    return jsonify({'files': files})

@app.route('/api/stats')
def get_stats():
    """Get statistics from the latest success file"""
    latest_file = get_latest_success_file()
    if not latest_file:
        return jsonify({
            'total_accounts': 0,
            'total_balance': 0,
            'avg_balance': 0,
            'website': 'none'
        })
    
    try:
        with open(latest_file, 'r', encoding='utf-8') as f:
            accounts = json.load(f)
            total = len(accounts)
            
            if total == 0:
                return jsonify({
                    'total_accounts': 0,
                    'total_balance': 0,
                    'avg_balance': 0,
                    'website': 'none'
                })
            
            # Detect website and balance key
            website = accounts[0].get('website', 'unknown')
            
            # Determine balance key based on website
            if website == 'jerryspizza':
                balance_key = 'loyaltyBalance'
                order_key = 'orderCount'
                spent_key = 'totalSpent'
            elif website == 'pizzahut':
                balance_key = 'points'
                order_key = None
                spent_key = None
            else:
                balance_key = 'loyaltyBalance'
                order_key = 'orderCount'
                spent_key = 'totalSpent'
            
            total_balance = sum(acc.get(balance_key, 0) for acc in accounts)
            
            stats = {
                'total_accounts': total,
                'total_balance': total_balance,
                'avg_balance': round(total_balance / total, 2) if total > 0 else 0,
                'website': website
            }
            
            # Add website-specific stats
            if order_key and spent_key:
                total_orders = sum(acc.get(order_key, 0) for acc in accounts)
                total_spent = sum(acc.get(spent_key, 0) for acc in accounts)
                stats.update({
                    'total_orders': total_orders,
                    'total_spent': round(total_spent, 2),
                    'avg_orders': round(total_orders / total, 2) if total > 0 else 0,
                    'avg_spent': round(total_spent / total, 2) if total > 0 else 0
                })
            
            return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def background_file_monitor():
    """Monitor for new success files and emit updates"""
    last_files = set()
    while True:
        current_files = set(str(f) for f in Path('.').glob('success_*.json'))
        if current_files != last_files:
            new_files = current_files - last_files
            if new_files:
                # New file detected, send update
                latest_file = get_latest_success_file()
                if latest_file:
                    try:
                        with open(latest_file, 'r', encoding='utf-8') as f:
                            accounts = json.load(f)
                            socketio.emit('data_update', {
                                'accounts': accounts,
                                'file': latest_file.name,
                                'timestamp': time.time()
                            })
                    except Exception as e:
                        print(f"Error reading file: {e}")
            last_files = current_files
        time.sleep(2)  # Check every 2 seconds

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    # Send initial data on connect
    latest_file = get_latest_success_file()
    if latest_file:
        try:
            with open(latest_file, 'r', encoding='utf-8') as f:
                accounts = json.load(f)
                emit('data_update', {
                    'accounts': accounts,
                    'file': latest_file.name,
                    'timestamp': time.time()
                })
        except Exception as e:
            print(f"Error sending initial data: {e}")

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('request_update')
def handle_request_update(data):
    """Handle manual refresh requests"""
    filename = data.get('filename')
    if filename:
        # Use specific file
        target_file = Path(filename)
        
        if target_file.exists():
            try:
                with open(target_file, 'r', encoding='utf-8') as f:
                    accounts = json.load(f)
                    emit('data_update', {
                        'accounts': accounts,
                        'file': target_file.name,
                        'timestamp': time.time()
                    })
            except Exception as e:
                emit('error', {'message': str(e)})
    else:
        # Get latest file
        latest_file = get_latest_success_file()
        if latest_file:
            try:
                with open(latest_file, 'r', encoding='utf-8') as f:
                    accounts = json.load(f)
                    emit('data_update', {
                        'accounts': accounts,
                        'file': latest_file.name,
                        'timestamp': time.time()
                    })
            except Exception as e:
                emit('error', {'message': str(e)})

if __name__ == '__main__':
    print("=" * 80)
    print("JERRY'S PIZZA ACCOUNT VIEWER")
    print("=" * 80)
    print("\n[*] Starting web server with WebSocket support...")
    print("[*] Open your browser to: http://localhost:5000")
    print("[*] Press Ctrl+C to stop\n")
    
    # Start background file monitor
    monitor_thread = Thread(target=background_file_monitor, daemon=True)
    monitor_thread.start()
    
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
