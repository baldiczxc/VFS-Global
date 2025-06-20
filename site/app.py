from flask import Flask, render_template, redirect, url_for, request
from prometheus_flask_exporter import PrometheusMetrics
import sqlite3
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

app = Flask(__name__)
metrics = PrometheusMetrics(app)

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database.db')
def get_db():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    return db

@app.route('/')
def index():
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    db = get_db()
    
    # Get realtime metrics
    realtime = db.execute('SELECT * FROM metrics ORDER BY last_updated DESC LIMIT 1').fetchone()
    if realtime:
        realtime = dict(realtime)
        realtime['error_percent'] = round((realtime['errors'] / realtime['slots_checked'] * 100) 
                                        if realtime['slots_checked'] > 0 else 0, 2)
    else:
        realtime = {
            # 'slots_checked': 0,  # убрано, больше не используется в шаблоне
            'active_users': 0,
            'successful_records': 0,
            'error_percent': 0
        }

    # --- Тестовые флаги ---
    if request.args.get('test') == '1':
        try:
            # slots = int(request.args.get('slots', realtime['slots_checked']))  # убрано
            users = int(request.args.get('users', realtime['active_users']))
            success = int(request.args.get('success', realtime['successful_records']))
            errors = int(request.args.get('errors', realtime.get('errors', 0)))
        except Exception:
            # slots = realtime.get('slots_checked', 0)
            users = realtime['active_users']
            success = realtime['successful_records']
            errors = realtime.get('errors', 0)
        # realtime['slots_checked'] = slots  # убрано
        realtime['active_users'] = users
        realtime['successful_records'] = success
        realtime['errors'] = errors
        # realtime['error_percent'] = round((errors / slots * 100) if slots > 0 else 0, 2)  # убрано
    # --- конец тестовых флагов ---

    # Get system statuses
    statuses = db.execute('SELECT * FROM system_status').fetchall()
    
    # Calculate KPIs
    total_attempts = db.execute('SELECT SUM(attempts) FROM bookings').fetchone()[0] or 0
    total_successful = db.execute('SELECT SUM(successful) FROM bookings').fetchone()[0] or 0
    
    kpi = {
        'success_rate': round((total_successful / total_attempts * 100) if total_attempts > 0 else 0, 1),
        'avg_response': round(realtime.get('slots_checked', 0) / 100, 1) if realtime.get('slots_checked', 0) > 0 else 0,
        'uptime': 99.9,  # This could be calculated based on actual system uptime
        'records_per_day': total_successful
    }

    # Get today's bookings
    bookings = db.execute('''
        SELECT hour, successful, attempts 
        FROM bookings 
        WHERE date = DATE('now') 
        ORDER BY hour
    ''').fetchall()

    # Активные пользователи за сегодня
    active_users = db.execute('''
        SELECT DISTINCT username FROM bookings WHERE username IS NOT NULL AND date = DATE('now')
    ''').fetchall()
    # Исправляем подсчет активных пользователей за сегодня
    realtime['active_users'] = len(active_users)

    # Группировка пользователей по дням для графика
    users_by_day = db.execute('''
        SELECT 
            strftime('%d.%m', date) as day, 
            COUNT(DISTINCT username) as count
        FROM bookings
        WHERE username IS NOT NULL
        GROUP BY day
        ORDER BY date
        LIMIT 14
    ''').fetchall()

    db.close()
    return render_template(
        'dashboard.html',
        realtime=realtime,
        statuses=statuses,
        kpi=kpi,
        bookings=bookings,
        active_users=active_users,
        users_by_day=users_by_day
    )

if __name__ == '__main__':
    # Используем правильную БД для инициализации (создаём таблицы в database.db)
    import sqlite3
    from database import init_db as metrics_init_db

    # Инициализация metrics.db (vfs_metrics.db) для совместимости, если нужно
    metrics_init_db()

    # Инициализация основной БД (database.db) для сайта
    if not os.path.exists(DB_PATH):
        # Если database.db не существует, создаём таблицы
        from init_db import init_db as site_init_db
        site_init_db()
    else:
        # Проверяем наличие таблиц, если файл уже есть
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        # Проверяем таблицу metrics
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='metrics'")
        if not cursor.fetchone():
            from init_db import init_db as site_init_db
            site_init_db()
        conn.close()

    app.run(debug=True, host='0.0.0.0')