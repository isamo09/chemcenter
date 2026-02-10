PLUGIN_CONFIG = {
    'name': 'Калькулятор молярной массы',
    'description': 'Расчет молярной массы вещества по химической формуле',
    'icon': 'weight-scale',
    'version': '1.0.0',
    'enabled': True,
    'route': '/plugin/molar_mass_calculator'
}

def get_content():
    """Return molar mass calculator plugin data"""
    return {
        'type': 'molar_mass_calculator',
        'config': PLUGIN_CONFIG
    }
