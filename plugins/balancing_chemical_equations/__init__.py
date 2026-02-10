PLUGIN_CONFIG = {
    'name': 'Балансировщик химических уравнений',
    'description': 'Автоматическая балансировка химических уравнений с проверкой баланса атомов',
    'icon': 'balance-scale',
    'version': '1.0.0',
    'enabled': True,
    'route': '/plugin/balancing_chemical_equations'
}

def get_content():
    """Return balancing equations plugin data"""
    return {
        'type': 'balancing_equations',
        'config': PLUGIN_CONFIG
    }
