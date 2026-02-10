PLUGIN_CONFIG = {
    'name': 'Углеводороды: формулы и названия',
    'description': 'Определение названий углеводородов по формулам и генерация формул',
    'icon': 'atom',
    'version': '1.0.0',
    'enabled': True,
    'route': '/plugin/hydrocarbon_equations'
}

def get_content():
    """Return hydrocarbon equations plugin data"""
    return {
        'type': 'hydrocarbon_equations',
        'config': PLUGIN_CONFIG
    }
