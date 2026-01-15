PLUGIN_CONFIG = {
    'name': 'Периодическая таблица',
    'description': 'Интерактивная периодическая таблица элементов с классификацией металлов и неметаллов',
    'icon': 'atom',
    'version': '2.0.0',
    'enabled': True,
    'route': '/plugin/periodic-table'
}

def get_content():
    """Return periodic table data"""
    return {
        'type': 'periodic_table',
        'config': PLUGIN_CONFIG
    }
