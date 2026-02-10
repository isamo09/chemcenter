PLUGIN_CONFIG = {
    'name': 'Классификация и номенклатура',
    'description': 'Определение класса органических соединений и их названий',
    'icon': 'atom',
    'version': '1.0.0',
    'enabled': True,
    'route': '/plugin/classification_and_nomenclature'
}

def get_content():
    """Return classification and nomenclature plugin data"""
    return {
        'type': 'classification_nomenclature',
        'config': PLUGIN_CONFIG
    }
