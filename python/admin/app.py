"""
Admin Web Application for Parking System
"""
from flask import Flask, render_template, request, jsonify, redirect, url_for, Response
import sys
import os
import logging
from datetime import datetime, timedelta
import json

# Add shared directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

from config import Config
from database import DatabaseService

logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'parking_system_secret_key_change_in_production'

# Global variables
config = None
database = None

def init_app():
    """Initialize application"""
    global config, database
    
    config_file = os.path.join(os.path.dirname(__file__), 'config.ini')
    config = Config(config_file)
    database = DatabaseService(config)

@app.route('/')
def dashboard():
    """Dashboard page"""
    try:
        # Get recent transactions with error handling
        try:
            recent_transactions = database.get_recent_transactions(20)
        except Exception as db_error:
            logger.warning(f"Database error: {db_error}")
            recent_transactions = []
        
        # Calculate statistics
        today = datetime.now().date()
        today_transactions = []
        
        # Safely process transactions
        for t in recent_transactions:
            try:
                if t.get('timestamp'):
                    trans_date = datetime.fromisoformat(t.get('timestamp', '')).date()
                    if trans_date == today:
                        today_transactions.append(t)
            except:
                continue  # Skip transactions with invalid timestamps
        
        stats = {
            'total_today': len(today_transactions),
            'entries_today': len([t for t in today_transactions if 'entry' in t.get('type', '')]),
            'exits_today': len([t for t in today_transactions if 'exit' in t.get('type', '')]),
            'members_today': len([t for t in today_transactions if 'member' in t.get('type', '')])
        }
        
        return render_template('dashboard.html', 
                             transactions=recent_transactions[:10], 
                             stats=stats)
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        # Return simple fallback dashboard
        return render_template('dashboard.html', 
                             transactions=[], 
                             stats={
                                 'total_today': 0,
                                 'entries_today': 0,
                                 'exits_today': 0,
                                 'members_today': 0
                             })

@app.route('/members')
def members():
    """Members management page"""
    try:
        try:
            members_list = database.get_all_members()
        except Exception as db_error:
            logger.warning(f"Database error: {db_error}")
            members_list = []
        
        return render_template('members.html', members=members_list)
    except Exception as e:
        logger.error(f"Members page error: {e}")
        return f"<h1>Members Error</h1><p>{str(e)}</p><a href='/'>Back to Dashboard</a>", 500

@app.route('/members/add', methods=['GET', 'POST'])
def add_member():
    """Add new member"""
    if request.method == 'POST':
        try:
            member_data = {
                'name': request.form['name'],
                'plate_number': request.form['plate_number'].upper(),
                'phone': request.form.get('phone', ''),
                'email': request.form.get('email', ''),
                'membership_type': request.form.get('membership_type', 'regular'),
                'status': 'active'
            }
            
            database.save_member(member_data)
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
        
        # Try to get transactions from database
        try:
            all_transactions = database.get_recent_transactions(500)
        except Exception as db_error:
            logger.warning(f"Database error: {db_error}")
            # Return empty list if database is not available
            all_transactions = []
        
        # Apply filters
        filtered_transactions = all_transactions
        
        if date_from:
            try:
                from datetime import datetime
                filtered_transactions = [t for t in filtered_transactions 
                                       if datetime.fromisoformat(t.get('waktu_masuk', '')[:19]) >= datetime.fromisoformat(date_from)]
            except:
                pass  # Skip filter if date parsing fails
        
        if date_to:
            try:
                from datetime import datetime
                filtered_transactions = [t for t in filtered_transactions 
                                       if datetime.fromisoformat(t.get('waktu_masuk', '')[:19]) <= datetime.fromisoformat(date_to)]
            except:
                pass  # Skip filter if date parsing fails
        
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
        # Return simple error page
        return f"<h1>Transactions Error</h1><p>{str(e)}</p><a href='/'>Back to Dashboard</a>", 500

@app.route('/settings')
def settings():
    """Settings page"""
    try:
        # Current settings
        current_settings = {
            'alpr_enabled': config.getboolean('ALPR', 'enabled'),
            'audio_enabled': config.getboolean('AUDIO', 'enabled'),
            'cctv_ip': config.get('CCTV', 'ip_address'),
            'cctv_username': config.get('CCTV', 'username'),
            'database_host': config.get('DATABASE', 'host'),
            'websocket_port': config.getint('WEBSOCKET', 'server_port')
        }
        
        return render_template('settings.html', settings=current_settings)
    except Exception as e:
        logger.error(f"Settings page error: {e}")
        # Return simple error page instead of rendering template that might not exist
        return f"<h1>Settings Error</h1><p>{str(e)}</p><a href='/'>Back to Dashboard</a>", 500

@app.route('/settings/update', methods=['POST'])
def update_settings():
    """Update settings"""
    try:
        # Update ALPR settings
        config.config.set('ALPR', 'enabled', str(request.form.get('alpr_enabled') == 'on'))
        
        # Update Audio settings
        config.config.set('AUDIO', 'enabled', str(request.form.get('audio_enabled') == 'on'))
        
        # Update CCTV settings
        if request.form.get('cctv_ip'):
            config.config.set('CCTV', 'ip_address', request.form['cctv_ip'])
        if request.form.get('cctv_username'):
            config.config.set('CCTV', 'username', request.form['cctv_username'])
        if request.form.get('cctv_password'):
            config.config.set('CCTV', 'password', request.form['cctv_password'])
        
        # Save configuration
        config_file = os.path.join(os.path.dirname(__file__), 'config.ini')
        config.save(config_file)
        
        return redirect(url_for('settings'))
    except Exception as e:
        logger.error(f"Update settings error: {e}")
        return render_template('settings.html', error=str(e))

@app.route('/api/stats')
def api_stats():
    """API endpoint for dashboard statistics"""
    try:
        # Get transactions for the last 7 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        recent_transactions = database.get_recent_transactions(1000)
        
        # Filter transactions for the last 7 days
        week_transactions = [
            t for t in recent_transactions 
            if start_date <= datetime.fromisoformat(t.get('timestamp', '')) <= end_date
        ]
        
        # Group by date
        daily_stats = {}
        for i in range(7):
            date = (end_date - timedelta(days=i)).date()
            daily_stats[date.isoformat()] = {
                'entries': 0,
                'exits': 0,
                'members': 0,
                'non_members': 0
            }
        
        for transaction in week_transactions:
            date = datetime.fromisoformat(transaction.get('timestamp', '')).date().isoformat()
            if date in daily_stats:
                t_type = transaction.get('type', '')
                
                if 'entry' in t_type:
                    daily_stats[date]['entries'] += 1
                elif 'exit' in t_type:
                    daily_stats[date]['exits'] += 1
                
                if 'member' in t_type:
                    daily_stats[date]['members'] += 1
                else:
                    daily_stats[date]['non_members'] += 1
        
        return jsonify(daily_stats)
    except Exception as e:
        logger.error(f"API stats error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/live_transactions')
def api_live_transactions():
    """API endpoint for live transactions"""
    try:
        recent_transactions = database.get_recent_transactions(10)
        return jsonify(recent_transactions)
    except Exception as e:
        logger.error(f"API live transactions error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/transaction/<transaction_id>')
def api_transaction_detail(transaction_id):
    """API endpoint for transaction details"""
    try:
        transaction = database.get_transaction(transaction_id)
        if not transaction:
            return jsonify({'error': 'Transaction not found'}), 404
        
        # Format the transaction data for display
        formatted_transaction = {
            'id': transaction.get('id', ''),
            '_id': transaction.get('_id', ''),
            'no_pol': transaction.get('no_pol', 'N/A'),
            'waktu_masuk': transaction.get('waktu_masuk', ''),
            'waktu_keluar': transaction.get('waktu_keluar', ''),
            'kategori': transaction.get('kategori', 'UMUM'),
            'status_transaksi': transaction.get('status_transaksi', '1'),
            'id_kendaraan': transaction.get('id_kendaraan', 2),
            'id_pintu_masuk': transaction.get('id_pintu_masuk', ''),
            'id_pintu_keluar': transaction.get('id_pintu_keluar', ''),
            'id_op_masuk': transaction.get('id_op_masuk', ''),
            'id_op_keluar': transaction.get('id_op_keluar', ''),
            'bayar_masuk': transaction.get('bayar_masuk', 0),
            'bayar_keluar': transaction.get('bayar_keluar', 0),
            'jenis_system': transaction.get('jenis_system', ''),
            'exit_method': transaction.get('exit_method', ''),
            '_attachments': transaction.get('_attachments', {})
        }
        
        return jsonify(formatted_transaction)
    except Exception as e:
        logger.error(f"API transaction detail error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/transaction/<transaction_id>/image/<image_name>')
def api_transaction_image(transaction_id, image_name):
    """API endpoint for transaction images"""
    try:
        # Get the attachment from CouchDB
        doc = database.db[transaction_id]
        
        if image_name not in doc.get('_attachments', {}):
            return jsonify({'error': 'Image not found'}), 404
        
        # Get the attachment
        attachment = database.db.get_attachment(doc, image_name)
        
        if attachment:
            return Response(
                attachment.read(),
                mimetype='image/jpeg',
                headers={'Content-Disposition': f'inline; filename={image_name}'}
            )
        else:
            return jsonify({'error': 'Failed to load image'}), 500
            
    except Exception as e:
        logger.error(f"API transaction image error: {e}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return render_template('error.html', error='Page not found'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', error='Internal server error'), 500

def main():
    """Main function"""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize app
    init_app()
    
    # Run app
    app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == '__main__':
    main()
