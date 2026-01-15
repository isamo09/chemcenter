import re

PLUGIN_CONFIG = {
    'name': "Принцип Ле Шателье",
    'description': 'Расчет смещения равновесия при изменении давления',
    'icon': 'scale-balanced',
    'version': '1.0.0',
    'enabled': True,
    'route': '/plugin/le-chatelier'
}

def parse_side(side_str):
    """Parse equation side: '3-3+2' → [3, -3, 2]"""
    tokens = re.findall(r'[+-]?\d+', side_str)
    return [int(x) for x in tokens] if tokens else []

def calculate_equilibrium(equation):
    """Calculate equilibrium shift based on pressure changes"""
    try:
        if "=" not in equation:
            return {
                'error': True,
                'message': 'Неверный формат. Используйте формат: 3-3=4+2+1'
            }
        
        left_str, right_str = equation.split("=", 1)
        
        left_coeffs = parse_side(left_str)
        right_coeffs = parse_side(right_str)
        
        if not left_coeffs or not right_coeffs:
            return {
                'error': True,
                'message': 'Неверный формат уравнения'
            }
        
        if abs(right_coeffs[-1]) != 1:
            return {
                'error': True,
                'message': 'Последний коэффициент справа должен быть ±1'
            }
        
        substance_coeffs = right_coeffs[:-1]
        
        if len(left_coeffs) != len(substance_coeffs):
            return {
                'error': True,
                'message': 'Разное количество веществ слева и справа'
            }
        
        delta_n = sum(substance_coeffs) - sum(left_coeffs)
        
        if delta_n > 0:
            direction = 'right'
            explanation = (
                f'Δn = {sum(substance_coeffs)} - {sum(left_coeffs)} = {delta_n}\n\n'
                f'✓ Положительное Δn: При увеличении давления равновесие смещается влево'
            )
        elif delta_n < 0:
            direction = 'left'
            explanation = (
                f'Δn = {sum(substance_coeffs)} - {sum(left_coeffs)} = {delta_n}\n\n'
                f'✓ Отрицательное Δn: При увеличении давления равновесие смещается вправо'
            )
        else:
            direction = 'none'
            explanation = (
                f'Δn = {sum(substance_coeffs)} - {sum(left_coeffs)} = {delta_n}\n\n'
                f'✓ Нулевое Δn: Давление НЕ влияет на положение равновесия'
            )
        
        return {
            'error': False,
            'delta': f'{delta_n:+d}',
            'delta_n': delta_n,
            'direction': direction,
            'explanation': explanation,
            'equation': equation
        }
    except Exception as e:
        return {
            'error': True,
            'message': f'Ошибка расчета: {str(e)}'
        }

def get_content():
    """Return Le Chatelier plugin data"""
    return {
        'type': 'le_chatelier',
        'config': PLUGIN_CONFIG
    }
