"""
Test Admin Interface - Run without database dependency
"""
from flask import Flask, render_template, request, jsonify, redirect, url_for
import sys
import os
import logging
from datetime import datetime, timedelta
import json

app = Flask(__name__)
app.secret_key = 'parking_system_secret_key_change_in_production'

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mock data for testing
MOCK_TRANSACTIONS = [
    {
        '_id': 'trans_001',
        'type': 'member_entry',
        'timestamp': datetime.now().isoformat(),
        'plate_number': 'B1234XYZ',
        'member_name': 'John Doe',
        'member_id': 'member_001',
        'gate_id': 'entry_gate_01',
        'confidence': 0.95
    },
    {
        '_id': 'trans_002',
        'type': 'non_member_entry',
        'timestamp': (datetime.now() - timedelta(minutes=30)).isoformat(),
        'plate_number': 'B5678ABC',
        'gate_id': 'entry_gate_01',
        'confidence': 0.87
    },
    {
        '_id': 'trans_003',
        'type': 'member_exit',
        'timestamp': (datetime.now() - timedelta(hours=1)).isoformat(),
        'plate_number': 'B9999ZZZ',
        'member_name': 'Jane Smith',
        'member_id': 'member_002',
        'gate_id': 'exit_gate_01',
        'confidence': 0.92
    }
]

MOCK_MEMBERS = [
    {
        '_id': 'member_001',
        'name': 'John Doe',
        'plate_number': 'B1234XYZ',
        'phone': '+62 812 3456 7890',
        'email': 'john@example.com',
        'membership_type': 'premium',
        'status': 'active',
        'created_at': '2025-01-01T10:00:00'
    },
    {
        '_id': 'member_002',
        'name': 'Jane Smith',
        'plate_number': 'B9999ZZZ',
        'phone': '+62 821 9876 5432',
        'email': 'jane@example.com',
        'membership_type': 'regular',
        'status': 'active',
        'created_at': '2025-01-02T14:30:00'
    }
]

MOCK_SETTINGS = {
    'alpr_enabled': True,
    'audio_enabled': True,
    'cctv_ip': '192.168.1.100',
    'cctv_username': 'admin',
    'database_host': 'localhost',
    'websocket_port': 8765
}

@app.route('/')
def dashboard():
    """Dashboard page"""
    try:
        # Calculate statistics from mock data
        today = datetime.now().date()
        today_transactions = []
        
        for t in MOCK_TRANSACTIONS:
            try:
                trans_date = datetime.fromisoformat(t.get('timestamp', '')).date()
                if trans_date == today:
                    today_transactions.append(t)
            except:
                continue
        
        stats = {
            'total_today': len(today_transactions),
            'entries_today': len([t for t in today_transactions if 'entry' in t.get('type', '')]),
            'exits_today': len([t for t in today_transactions if 'exit' in t.get('type', '')]),
            'members_today': len([t for t in today_transactions if 'member' in t.get('type', '')])
        }
        
        return render_template('dashboard.html', 
                             transactions=MOCK_TRANSACTIONS, 
                             stats=stats)
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        return f"<h1>Dashboard Error</h1><p>{str(e)}</p>", 500

@app.route('/members')
def members():
    """Members management page"""
    return render_template('members.html', members=MOCK_MEMBERS)

@app.route('/members/add', methods=['GET', 'POST'])
def add_member():
    """Add new member"""
    if request.method == 'POST':
        try:
            member_data = {
                '_id': f"member_{len(MOCK_MEMBERS) + 1:03d}",
                'name': request.form['name'],
                'plate_number': request.form['plate_number'].upper(),
                'phone': request.form.get('phone', ''),
                'email': request.form.get('email', ''),
                'membership_type': request.form.get('membership_type', 'regular'),
                'status': 'active',
                'created_at': datetime.now().isoformat()
            }
            
            MOCK_MEMBERS.append(member_data)
            logger.info(f"Mock member added: {member_data['name']}")
            return redirect(url_for('members'))
        except Exception as e:
            logger.error(f"Add member error: {e}")
            return render_template('add_member.html', error=str(e))
    
    return render_template('add_member.html')

@app.route('/transactions')
def transactions():
    """Transactions page"""
    try:
        # Get filter parameters
        date_from = request.args.get('date_from', '')
        date_to = request.args.get('date_to', '')
        transaction_type = request.args.get('type', '')
        
        filtered_transactions = MOCK_TRANSACTIONS.copy()
        
        # Apply filters
        if date_from:
            try:
                filtered_transactions = [t for t in filtered_transactions 
                                       if datetime.fromisoformat(t.get('timestamp', '')) >= datetime.fromisoformat(date_from)]
            except:
                pass
        
        if date_to:
            try:
                filtered_transactions = [t for t in filtered_transactions 
                                       if datetime.fromisoformat(t.get('timestamp', '')) <= datetime.fromisoformat(date_to)]
            except:
                pass
        
        if transaction_type:
            filtered_transactions = [t for t in filtered_transactions 
                                   if transaction_type in t.get('type', '')]
        
        return render_template('transactions.html', 
                             transactions=filtered_transactions,
                             date_from=date_from,
                             date_to=date_to,
                             transaction_type=transaction_type)
    except Exception as e:
        logger.error(f"Transactions page error: {e}")
        return f"<h1>Transactions Error</h1><p>{str(e)}</p><a href='/'>Back to Dashboard</a>", 500

@app.route('/settings')
def settings():
    """Settings page"""
    return render_template('settings.html', settings=MOCK_SETTINGS)

@app.route('/settings/update', methods=['POST'])
def update_settings():
    """Update settings"""
    try:
        # Update mock settings
        MOCK_SETTINGS['alpr_enabled'] = request.form.get('alpr_enabled') == 'on'
        MOCK_SETTINGS['audio_enabled'] = request.form.get('audio_enabled') == 'on'
        
        if request.form.get('cctv_ip'):
            MOCK_SETTINGS['cctv_ip'] = request.form['cctv_ip']
        if request.form.get('cctv_username'):
            MOCK_SETTINGS['cctv_username'] = request.form['cctv_username']
        
        logger.info("Mock settings updated")
        return redirect(url_for('settings'))
    except Exception as e:
        logger.error(f"Update settings error: {e}")
        return render_template('settings.html', settings=MOCK_SETTINGS, error=str(e))

@app.route('/api/stats')
def api_stats():
    """API endpoint for dashboard statistics"""
    try:
        # Generate mock weekly stats
        daily_stats = {}
        for i in range(7):
            date = (datetime.now() - timedelta(days=i)).date().isoformat()
            daily_stats[date] = {
                'entries': max(0, 10 - i * 2),
                'exits': max(0, 8 - i * 2),
                'members': max(0, 6 - i),
                'non_members': max(0, 4 - i)
            }
        
        return jsonify(daily_stats)
    except Exception as e:
        logger.error(f"API stats error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/live_transactions')
def api_live_transactions():
    """API endpoint for live transactions"""
    return jsonify(MOCK_TRANSACTIONS)

@app.errorhandler(404)
def not_found(error):
    return f"<h1>404 Not Found</h1><p>Page not found</p><a href='/'>Go to Dashboard</a>", 404

@app.errorhandler(500)
def internal_error(error):
    return f"<h1>500 Internal Error</h1><p>Internal server error</p><a href='/'>Go to Dashboard</a>", 500

def main():
    """Main function"""
    print("=" * 50)
    print("PARKING SYSTEM ADMIN - TEST MODE")
    print("=" * 50)
    print("This is a test version with mock data")
    print("No database connection required")
    print("Access: http://localhost:5000")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == '__main__':
    main()
