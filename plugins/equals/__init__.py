PLUGIN_CONFIG = {
    'name': 'Универсальный калькулятор ионных уравнений',
    'description': 'Расчет ионных уравнений с проверкой растворимости и определением типа реакции',
    'icon': 'calculator',
    'version': '1.0.0',
    'enabled': True,
    'route': '/plugin/equals'
}

def get_content():
    """Return universal ionic equation calculator plugin data"""
    return {
        'type': 'universal_ionic_calculator',
        'config': PLUGIN_CONFIG
    }
