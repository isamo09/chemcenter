from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from flask_cors import CORS
from functools import wraps
import json
import os
import hashlib
import uuid
from datetime import datetime, timedelta
from pathlib import Path

app = Flask(__name__)
app.secret_key = 'key'
CORS(app)

# Configuration
PLUGINS_DIR = Path('plugins')
DATA_DIR = Path('data')
DATA_DIR.mkdir(exist_ok=True)
PLUGINS_DIR.mkdir(exist_ok=True)

STATS_FILE = DATA_DIR / 'visits.json'


def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()


def load_visits():
    """Load visits data from file"""
    if STATS_FILE.exists():
        with open(STATS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'visits': []}


def save_visits(data):
    """Save visits data to file"""
    with open(STATS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def record_visit():
    """Record a new visit"""
    data = load_visits()

    # Get or create session ID
    if 'visitor_id' not in session:
        session['visitor_id'] = str(uuid.uuid4())

    visit = {
        'timestamp': datetime.now().isoformat(),
        'session_id': session['visitor_id'],
        'ip': request.remote_addr,
        'user_agent': request.headers.get('User-Agent', '')[:200]
    }

    data['visits'].append(visit)

    # Keep only last 100000 visits to prevent file from growing too large
    if len(data['visits']) > 100000:
        data['visits'] = data['visits'][-100000:]

    save_visits(data)


def get_statistics():
    """Calculate visit statistics"""
    data = load_visits()
    visits = data.get('visits', [])

    now = datetime.now()

    # Define time periods
    periods = {
        'hour': {
            'current_start': now.replace(minute=0, second=0, microsecond=0),
            'prev_start': now.replace(minute=0, second=0, microsecond=0) - timedelta(hours=1),
            'prev_end': now.replace(minute=0, second=0, microsecond=0)
        },
        'day': {
            'current_start': now.replace(hour=0, minute=0, second=0, microsecond=0),
            'prev_start': now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1),
            'prev_end': now.replace(hour=0, minute=0, second=0, microsecond=0)
        },
        'month': {
            'current_start': now.replace(day=1, hour=0, minute=0, second=0, microsecond=0),
            'prev_start': (now.replace(day=1) - timedelta(days=1)).replace(day=1, hour=0, minute=0, second=0,
                                                                           microsecond=0),
            'prev_end': now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        },
        'year': {
            'current_start': now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0),
            'prev_start': now.replace(year=now.year - 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0),
            'prev_end': now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        }
    }

    stats = {
        'total': {'visits': 0, 'unique': 0},
        'hour': {'current': {'visits': 0, 'unique': 0}, 'previous': {'visits': 0, 'unique': 0}},
        'day': {'current': {'visits': 0, 'unique': 0}, 'previous': {'visits': 0, 'unique': 0}},
        'month': {'current': {'visits': 0, 'unique': 0}, 'previous': {'visits': 0, 'unique': 0}},
        'year': {'current': {'visits': 0, 'unique': 0}, 'previous': {'visits': 0, 'unique': 0}}
    }

    # Session sets for unique counting
    total_sessions = set()
    period_sessions = {
        'hour': {'current': set(), 'previous': set()},
        'day': {'current': set(), 'previous': set()},
        'month': {'current': set(), 'previous': set()},
        'year': {'current': set(), 'previous': set()}
    }

    for visit in visits:
        try:
            visit_time = datetime.fromisoformat(visit['timestamp'])
            session_id = visit.get('session_id', visit.get('ip', 'unknown'))

            # Total
            stats['total']['visits'] += 1
            total_sessions.add(session_id)

            # Check each period
            for period_name, period_times in periods.items():
                # Current period
                if visit_time >= period_times['current_start']:
                    stats[period_name]['current']['visits'] += 1
                    period_sessions[period_name]['current'].add(session_id)

                # Previous period
                if period_times['prev_start'] <= visit_time < period_times['prev_end']:
                    stats[period_name]['previous']['visits'] += 1
                    period_sessions[period_name]['previous'].add(session_id)
        except (ValueError, KeyError):
            continue

    # Calculate unique visits
    stats['total']['unique'] = len(total_sessions)
    for period_name in periods:
        stats[period_name]['current']['unique'] = len(period_sessions[period_name]['current'])
        stats[period_name]['previous']['unique'] = len(period_sessions[period_name]['previous'])

    return stats


def init_admin():
    """Initialize default admin account if not exists"""
    users_file = DATA_DIR / 'users.json'
    if not users_file.exists():
        default_admin = {
            'admin': {
                'password': hash_password('admin123'),
                'role': 'admin',
                'created_at': datetime.now().isoformat()
            }
        }
        with open(users_file, 'w', encoding='utf-8') as f:
            json.dump(default_admin, f, ensure_ascii=False, indent=2)
        print("✓ Default admin account created (login: admin, password: admin123)")
    return True


def check_credentials(username, password):
    """Check if credentials are valid"""
    users_file = DATA_DIR / 'users.json'
    if users_file.exists():
        with open(users_file, 'r', encoding='utf-8') as f:
            users = json.load(f)
        if username in users:
            return users[username]['password'] == hash_password(password)
    return False


def login_required(f):
    """Decorator to require admin login"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated_function


# Initialize admin on startup
init_admin()


# Initialize plugin system
class PluginManager:
    def __init__(self):
        self.plugins = {}
        self.config_file = DATA_DIR / 'config.json'
        self.load_plugins()

    def load_plugins(self):
        """Load all plugins from plugins directory"""
        for plugin_dir in PLUGINS_DIR.glob('*/'):
            if plugin_dir.is_dir() and (plugin_dir / '__init__.py').exists():
                plugin_name = plugin_dir.name
                try:
                    import importlib.util
                    spec = importlib.util.spec_from_file_location(
                        f"plugins.{plugin_name}",
                        plugin_dir / '__init__.py'
                    )
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    if hasattr(module, 'PLUGIN_CONFIG'):
                        self.plugins[plugin_name] = module
                        print(f"✓ Plugin loaded: {plugin_name}")
                except Exception as e:
                    print(f"✗ Error loading plugin {plugin_name}: {e}")

    def get_plugin(self, name):
        return self.plugins.get(name)

    def get_all_plugins(self):
        return self.plugins

    def get_plugin_config(self, name):
        plugin = self.get_plugin(name)
        if plugin and hasattr(plugin, 'PLUGIN_CONFIG'):
            return plugin.PLUGIN_CONFIG
        return None


plugin_manager = PluginManager()


# Routes
@app.route('/')
def index():
    """Main page"""
    record_visit()  # Record visit
    config = load_config()
    return render_template('index.html', config=config)


@app.route('/api/config', methods=['GET'])
def get_config():
    """Get application configuration"""
    config = load_config()
    return jsonify(config)


@app.route('/api/config', methods=['POST'])
@login_required
def update_config():
    """Update application configuration"""
    data = request.json
    config = load_config()
    config.update(data)
    save_config(config)
    return jsonify({'success': True})


@app.route('/api/plugins')
def get_plugins():
    """Get all available plugins with enabled status"""
    config = load_config()
    enabled_plugins = config.get('enabled_plugins', ['periodic_table', 'le_chatelier'])

    plugins_info = {}
    for name, plugin in plugin_manager.get_all_plugins().items():
        if hasattr(plugin, 'PLUGIN_CONFIG'):
            plugin_config = plugin.PLUGIN_CONFIG
            plugins_info[name] = {
                'name': plugin_config['name'],
                'description': plugin_config.get('description', ''),
                'icon': plugin_config.get('icon', 'grid'),
                'version': plugin_config.get('version', '1.0.0'),
                'enabled': name in enabled_plugins
            }
    return jsonify(plugins_info)


@app.route('/api/plugins/<name>/toggle', methods=['POST'])
@login_required
def toggle_plugin(name):
    """Toggle plugin enabled status"""
    config = load_config()
    enabled_plugins = config.get('enabled_plugins', ['periodic_table', 'le_chatelier'])

    if name in enabled_plugins:
        enabled_plugins.remove(name)
    else:
        enabled_plugins.append(name)

    config['enabled_plugins'] = enabled_plugins
    save_config(config)
    return jsonify({'success': True, 'enabled': name in enabled_plugins})


@app.route('/api/admin/statistics')
@login_required
def get_visit_statistics():
    """Get visit statistics"""
    stats = get_statistics()
    return jsonify(stats)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login page"""
    config = load_config()
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if check_credentials(username, password):
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('admin'))
        else:
            return render_template('login.html', config=config, error='Неверный логин или пароль')

    return render_template('login.html', config=config)


@app.route('/logout')
def logout():
    """Logout"""
    session.clear()
    return redirect(url_for('index'))


@app.route('/admin')
@login_required
def admin():
    """Admin dashboard"""
    config = load_config()
    return render_template('admin.html', config=config)


@app.route('/api/admin/tiles', methods=['GET'])
def get_tiles():
    """Get tile configuration"""
    config = load_config()
    return jsonify(config.get('tiles', []))


@app.route('/api/admin/tiles', methods=['POST'])
@login_required
def save_tiles():
    """Save tile configuration"""
    data = request.json
    config = load_config()
    config['tiles'] = data
    save_config(config)
    return jsonify({'success': True})


@app.route('/api/admin/posts', methods=['GET'])
def get_posts():
    """Get all posts"""
    posts_file = DATA_DIR / 'posts.json'
    if posts_file.exists():
        with open(posts_file, 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    return jsonify([])


@app.route('/api/admin/posts', methods=['POST'])
@login_required
def create_post():
    """Create new post"""
    data = request.json
    posts_file = DATA_DIR / 'posts.json'
    if posts_file.exists():
        with open(posts_file, 'r', encoding='utf-8') as f:
            posts = json.load(f)
    else:
        posts = []

    post = {
        'id': int(datetime.now().timestamp() * 1000),
        'title': data.get('title', ''),
        'content': data.get('content', ''),
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    }

    posts.append(post)
    save_posts(posts)
    return jsonify(post)


@app.route('/api/admin/posts/<int:post_id>', methods=['PUT'])
@login_required
def update_post(post_id):
    """Update post"""
    data = request.json
    posts_file = DATA_DIR / 'posts.json'
    if posts_file.exists():
        with open(posts_file, 'r', encoding='utf-8') as f:
            posts = json.load(f)
    else:
        posts = []

    for post in posts:
        if post['id'] == post_id:
            post['title'] = data.get('title', post['title'])
            post['content'] = data.get('content', post['content'])
            post['updated_at'] = datetime.now().isoformat()
            save_posts(posts)
            return jsonify(post)

    return jsonify({'error': 'Post not found'}), 404


@app.route('/api/admin/posts/<int:post_id>', methods=['DELETE'])
@login_required
def delete_post(post_id):
    """Delete post"""
    posts_file = DATA_DIR / 'posts.json'
    if posts_file.exists():
        with open(posts_file, 'r', encoding='utf-8') as f:
            posts = json.load(f)
    else:
        posts = []

    posts = [p for p in posts if p['id'] != post_id]
    save_posts(posts)
    return jsonify({'success': True})


@app.route('/api/admin/change-password', methods=['POST'])
@login_required
def change_password():
    """Change admin password"""
    data = request.json
    old_password = data.get('old_password')
    new_password = data.get('new_password')

    username = session.get('username')
    users_file = DATA_DIR / 'users.json'

    if users_file.exists():
        with open(users_file, 'r', encoding='utf-8') as f:
            users = json.load(f)

        if username in users and users[username]['password'] == hash_password(old_password):
            users[username]['password'] = hash_password(new_password)
            with open(users_file, 'w', encoding='utf-8') as f:
                json.dump(users, f, ensure_ascii=False, indent=2)
            return jsonify({'success': True})

    return jsonify({'error': 'Неверный текущий пароль'}), 400


@app.route('/plugin/<name>')
def view_plugin(name):
    """View plugin page"""
    record_visit()  # Record visit
    plugin = plugin_manager.get_plugin(name)
    if not plugin:
        return "Plugin not found", 404

    config = load_config()

    template_map = {
        'periodic_table': 'plugin_periodic_table.html',
        'le_chatelier': 'plugin_le_chatelier.html',
        'Ionic_equation': 'plugin_Ionic_equation.html',
        'solubility_table': 'plugin_solubility_table.html',
        'balancing_chemical_equations': 'plugin_balancing_chemical_equations.html',
        'electrochemical_voltage_series': 'plugin_electrochemical_voltage_series.html',
        'hydrocarbon_equations': 'plugin_hydrocarbon_equations.html',
        'molar_mass_calculator': 'plugin_molar_mass_calculator.html',
        'classification_and_nomenclature': 'plugin_classification_and_nomenclature.html',
        'equals': 'plugin_equals.html'
    }

    template = template_map.get(name, f'plugin_{name}.html')
    return render_template(template, config=config)


@app.route('/api/plugin/<name>', methods=['GET', 'POST'])
def get_plugin_content(name):
    """Get plugin content"""
    plugin = plugin_manager.get_plugin(name)
    if not plugin:
        return jsonify({'error': 'Plugin not found'}), 404

    # Обработка POST запросов для плагинов с расчетами
    if request.method == 'POST':
        if name == 'Ionic_equation':
            data = request.json
            equation = data.get('equation', '')
            if equation and hasattr(plugin, 'solve_ionic_equation'):
                result = plugin.solve_ionic_equation(equation)
                return jsonify(result)
            return jsonify({'error': 'Invalid request'}), 400

    # Обработка GET запросов
    if name == 'le_chatelier':
        equation = request.args.get('equation')
        if equation and hasattr(plugin, 'calculate_equilibrium'):
            result = plugin.calculate_equilibrium(equation)
            return jsonify(result)

    if hasattr(plugin, 'get_content'):
        content = plugin.get_content()
        return jsonify(content)

    return jsonify({'error': 'Plugin has no content'})


@app.route('/post/<int:post_id>')
def view_post(post_id):
    """View individual post"""
    record_visit()  # Record visit
    posts_file = DATA_DIR / 'posts.json'
    config = load_config()

    if posts_file.exists():
        with open(posts_file, 'r', encoding='utf-8') as f:
            posts = json.load(f)

        for post in posts:
            if post['id'] == post_id:
                # Format date for display
                date = datetime.fromisoformat(post['updated_at'])
                post['updated_at'] = date.strftime('%d %B %Y, %H:%M')
                return render_template('post.html', post=post, config=config)

    return "Post not found", 404


@app.route('/data/elements')
def get_elements_data():
    """
    Get periodic table elements data

    Query parameters:
    - symbol: Get specific element by symbol (e.g., ?symbol=H)
    - number: Get specific element by atomic number (e.g., ?number=1)
    - category: Filter by category (e.g., ?category=noble-gas)
    - period: Filter by period (e.g., ?period=1)
    - group: Filter by group (e.g., ?group=1)
    - all: Get all elements (default)

    Examples:
    - /data/elements?symbol=H - Get hydrogen data
    - /data/elements?category=noble-gas - Get all noble gases
    - /data/elements?period=2 - Get all period 2 elements
    - /data/elements - Get all elements
    """
    elements_file = DATA_DIR / 'elements.json'

    if not elements_file.exists():
        return jsonify({'error': 'Elements data not found'}), 404

    with open(elements_file, 'r', encoding='utf-8') as f:
        elements = json.load(f)

    # Handle specific queries
    symbol = request.args.get('symbol')
    number = request.args.get('number')
    category = request.args.get('category')
    period = request.args.get('period')
    group = request.args.get('group')

    # Get specific element by symbol
    if symbol:
        symbol = symbol.upper()
        if symbol in elements:
            return jsonify(elements[symbol])
        return jsonify({'error': f'Element {symbol} not found'}), 404

    # Get specific element by number
    if number:
        try:
            num = int(number)
            for sym, data in elements.items():
                if data['number'] == num:
                    return jsonify(data)
            return jsonify({'error': f'Element with number {num} not found'}), 404
        except ValueError:
            return jsonify({'error': 'Invalid atomic number'}), 400

    # Filter by category
    if category:
        filtered = [{'symbol': sym, **data} for sym, data in elements.items()
                    if data['category'] == category]
        return jsonify(filtered)

    # Filter by period
    if period:
        try:
            per = int(period)
            filtered = [{'symbol': sym, **data} for sym, data in elements.items()
                        if data['period'] == per]
            return jsonify(filtered)
        except ValueError:
            return jsonify({'error': 'Invalid period number'}), 400

    # Filter by group
    if group:
        try:
            grp = int(group)
            filtered = [{'symbol': sym, **data} for sym, data in elements.items()
                        if data['group'] == grp]
            return jsonify(filtered)
        except ValueError:
            return jsonify({'error': 'Invalid group number'}), 400

    # Return all elements as array (default)
    elements_array = [{'symbol': sym, **data} for sym, data in elements.items()]
    return jsonify(elements_array)


# Helper functions
def load_config():
    """Load configuration from file"""
    config_file = DATA_DIR / 'config.json'
    if config_file.exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return get_default_config()


def save_config(config):
    """Save configuration to file"""
    config_file = DATA_DIR / 'config.json'
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def get_default_config():
    """Get default configuration"""
    return {
        'theme': 'light',
        'site_title': 'Научный Портал',
        'site_description': 'Интерактивная научная платформа',
        'site_logo_light': '/static/images/logo-light.png',
        'site_logo_dark': '/static/images/logo-dark.png',
        'enabled_plugins': [
            'periodic_table',
            'le_chatelier',
            'solubility_table',
            'Ionic_equation',
            'balancing_chemical_equations',
            'electrochemical_voltage_series',
            'hydrocarbon_equations',
            'molar_mass_calculator',
            'classification_and_nomenclature',
            'equals'
        ],
        'tiles': []
    }


def save_posts(posts):
    """Save posts to file"""
    posts_file = DATA_DIR / 'posts.json'
    with open(posts_file, 'w', encoding='utf-8') as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    app.run(debug=True, port=1253, host="0.0.0.0")
