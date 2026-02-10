PLUGIN_CONFIG = {
    'name': 'Электрохимический ряд напряжений',
    'description': 'Интерактивный ряд активности металлов с возможностью сравнения',
    'icon': 'bolt',
    'version': '1.0.0',
    'enabled': True,
    'route': '/plugin/electrochemical_voltage_series'
}

def get_content():
    """Return electrochemical series plugin data"""
    return {
        'type': 'electrochemical_series',
        'config': PLUGIN_CONFIG
    }
