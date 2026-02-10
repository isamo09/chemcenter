import re
from typing import Dict, List, Tuple, Optional

PLUGIN_CONFIG = {
    'name': "Решатель ионных уравнений",
    'description': 'Решение полных и сокращенных ионных уравнений с проверкой растворимости',
    'icon': 'ion-equation',
    'version': '1.0.0',
    'enabled': True,
    'route': '/plugin/Ionic_equation'
}

# Импортируем таблицу растворимости
try:
    from plugins.solubility_table import SOLUBILITY_MATRIX, SOLUBILITY_DATA
except ImportError:
    try:
        from solubility_table import SOLUBILITY_MATRIX, SOLUBILITY_DATA
    except ImportError:
        # Запасные данные
        SOLUBILITY_MATRIX = {}
        SOLUBILITY_DATA = {}


class IonicEquationSolver:
    """Класс для решения ионных уравнений"""

    def __init__(self):
        self.compound_db = self.build_compound_database()

    def build_compound_database(self) -> Dict[str, Dict]:
        """Строит базу данных соединений из таблицы растворимости"""
        compounds = {}

        for ion_pair_str, data in SOLUBILITY_MATRIX.items():
            if ' + ' in str(ion_pair_str):
                cation, anion = str(ion_pair_str).split(' + ')
                formula = self.generate_formula(cation, anion)
                if formula:
                    compounds[formula] = {
                        'formula': formula,
                        'cation': cation,
                        'anion': anion,
                        'solubility': data.get('sol', '?'),
                        'description': data.get('desc', ''),
                        'color': data.get('color', '#95A5A6')
                    }

        # Добавляем основные соединения
        basic_compounds = {
            'NaCl': {'cation': 'Na⁺', 'anion': 'Cl⁻', 'solubility': 'р'},
            'KCl': {'cation': 'K⁺', 'anion': 'Cl⁻', 'solubility': 'р'},
            'HCl': {'cation': 'H⁺', 'anion': 'Cl⁻', 'solubility': 'р'},
            'NaOH': {'cation': 'Na⁺', 'anion': 'OH⁻', 'solubility': 'р'},
            'KOH': {'cation': 'K⁺', 'anion': 'OH⁻', 'solubility': 'р'},
            'AgNO3': {'cation': 'Ag⁺', 'anion': 'NO₃⁻', 'solubility': 'р'},
            'AgCl': {'cation': 'Ag⁺', 'anion': 'Cl⁻', 'solubility': 'н'},
            'NaNO3': {'cation': 'Na⁺', 'anion': 'NO₃⁻', 'solubility': 'р'},
            'BaCl2': {'cation': 'Ba²⁺', 'anion': 'Cl⁻', 'solubility': 'р'},
            'Na2SO4': {'cation': 'Na⁺', 'anion': 'SO₄²⁻', 'solubility': 'р'},
            'BaSO4': {'cation': 'Ba²⁺', 'anion': 'SO₄²⁻', 'solubility': 'н'},
            'H2SO4': {'cation': 'H⁺', 'anion': 'SO₄²⁻', 'solubility': 'р'},
            'Na2CO3': {'cation': 'Na⁺', 'anion': 'CO₃²⁻', 'solubility': 'р'},
            'CaCO3': {'cation': 'Ca²⁺', 'anion': 'CO₃²⁻', 'solubility': 'н'},
            'CaCl2': {'cation': 'Ca²⁺', 'anion': 'Cl⁻', 'solubility': 'р'},
            'MgCl2': {'cation': 'Mg²⁺', 'anion': 'Cl⁻', 'solubility': 'р'},
            'AlCl3': {'cation': 'Al³⁺', 'anion': 'Cl⁻', 'solubility': 'р'},
            'FeCl3': {'cation': 'Fe³⁺', 'anion': 'Cl⁻', 'solubility': 'р'},
            'CuCl2': {'cation': 'Cu²⁺', 'anion': 'Cl⁻', 'solubility': 'р'},
            'PbCl2': {'cation': 'Pb²⁺', 'anion': 'Cl⁻', 'solubility': 'м'},
            'Ca(OH)2': {'cation': 'Ca²⁺', 'anion': 'OH⁻', 'solubility': 'м'},
            'Mg(OH)2': {'cation': 'Mg²⁺', 'anion': 'OH⁻', 'solubility': 'н'},
            'Al(OH)3': {'cation': 'Al³⁺', 'anion': 'OH⁻', 'solubility': 'н'},
            'Fe(OH)3': {'cation': 'Fe³⁺', 'anion': 'OH⁻', 'solubility': 'н'},
            'Cu(OH)2': {'cation': 'Cu²⁺', 'anion': 'OH⁻', 'solubility': 'н'},
            'H2O': {'cation': 'H⁺', 'anion': 'OH⁻', 'solubility': 'р'},
            'CO2': {'cation': 'C⁴⁺', 'anion': 'O²⁻', 'solubility': 'р'},
        }

        for formula, data in basic_compounds.items():
            if formula not in compounds:
                compounds[formula] = {
                    'formula': formula,
                    **data,
                    'description': '',
                    'color': '#95A5A6'
                }

        return compounds

    def generate_formula(self, cation: str, anion: str) -> Optional[str]:
        """Генерирует формулу из ионов"""
        try:
            cation_base = cation.replace('⁺', '').replace('²⁺', '').replace('³⁺', '')
            anion_base = anion.replace('⁻', '').replace('²⁻', '').replace('³⁻', '')

            # Простые случаи
            common_formulas = {
                ('Na⁺', 'Cl⁻'): 'NaCl',
                ('K⁺', 'Cl⁻'): 'KCl',
                ('H⁺', 'Cl⁻'): 'HCl',
                ('Na⁺', 'OH⁻'): 'NaOH',
                ('K⁺', 'OH⁻'): 'KOH',
                ('Ag⁺', 'NO₃⁻'): 'AgNO3',
                ('Ag⁺', 'Cl⁻'): 'AgCl',
                ('Na⁺', 'NO₃⁻'): 'NaNO3',
                ('Ba²⁺', 'Cl⁻'): 'BaCl2',
                ('Na⁺', 'SO₄²⁻'): 'Na2SO4',
                ('Ba²⁺', 'SO₄²⁻'): 'BaSO4',
                ('H⁺', 'SO₄²⁻'): 'H2SO4',
                ('Na⁺', 'CO₃²⁻'): 'Na2CO3',
                ('Ca²⁺', 'CO₃²⁻'): 'CaCO3',
                ('Ca²⁺', 'Cl⁻'): 'CaCl2',
                ('Mg²⁺', 'Cl⁻'): 'MgCl2',
                ('Al³⁺', 'Cl⁻'): 'AlCl3',
                ('Fe³⁺', 'Cl⁻'): 'FeCl3',
                ('Cu²⁺', 'Cl⁻'): 'CuCl2',
                ('Pb²⁺', 'Cl⁻'): 'PbCl2',
                ('Ca²⁺', 'OH⁻'): 'Ca(OH)2',
                ('Mg²⁺', 'OH⁻'): 'Mg(OH)2',
                ('Al³⁺', 'OH⁻'): 'Al(OH)3',
                ('Fe³⁺', 'OH⁻'): 'Fe(OH)3',
                ('Cu²⁺', 'OH⁻'): 'Cu(OH)2',
                ('H⁺', 'OH⁻'): 'H2O',
            }

            return common_formulas.get((cation, anion))
        except:
            return None

    def solve_ionic_equation(self, equation_str: str) -> Dict:
        """
        Решает ионное уравнение, введенное пользователем

        Форматы:
        1. Только реагенты: "NaCl + AgNO3"
        2. Полное уравнение: "NaCl + AgNO3 = AgCl + NaNO3"
        3. С реакционной стрелкой: "NaCl + AgNO3 → AgCl + NaNO3"
        """
        try:
            # Нормализуем уравнение
            equation_str = equation_str.strip()

            # Определяем формат
            if '=' in equation_str:
                separator = '='
            elif '→' in equation_str:
                separator = '→'
            else:
                # Только реагенты - предсказываем продукты
                return self.predict_reaction(equation_str)

            # Разделяем на левую и правую часть
            left_str, right_str = equation_str.split(separator, 1)

            # Парсим соединения
            reactants = self.parse_compounds(left_str)
            products = self.parse_compounds(right_str)

            if not reactants or not products:
                return {
                    'error': True,
                    'message': 'Не удалось распознать соединения в уравнении'
                }

            # Проверяем баланс и генерируем уравнения
            return self.generate_ionic_equations(reactants, products, equation_str)

        except Exception as e:
            return {
                'error': True,
                'message': f'Ошибка обработки уравнения: {str(e)}'
            }

    def predict_reaction(self, reactants_str: str) -> Dict:
        """Предсказывает реакцию по реагентам"""
        try:
            reactants = self.parse_compounds(reactants_str)

            if len(reactants) != 2:
                return {
                    'error': True,
                    'message': 'Введите 2 реагента через + (например: NaCl + AgNO3)'
                }

            # Получаем ионы
            r1_info = self.get_compound_info(reactants[0])
            r2_info = self.get_compound_info(reactants[1])

            if not r1_info or not r2_info:
                return {
                    'error': True,
                    'message': f'Неизвестные соединения: {reactants[0]} или {reactants[1]}'
                }

            # Реакция обмена: меняем ионы
            product1_formula = self.generate_formula(r1_info['cation'], r2_info['anion'])
            product2_formula = self.generate_formula(r2_info['cation'], r1_info['anion'])

            if not product1_formula or not product2_formula:
                return {
                    'error': True,
                    'message': 'Не удалось определить продукты реакции'
                }

            # Получаем информацию о продуктах
            p1_info = self.get_compound_info(product1_formula)
            p2_info = self.get_compound_info(product2_formula)

            # Формируем уравнение
            equation = f"{reactants[0]} + {reactants[1]} → {product1_formula} + {product2_formula}"

            return self.generate_ionic_equations(
                reactants,
                [product1_formula, product2_formula],
                equation
            )

        except Exception as e:
            return {
                'error': True,
                'message': f'Ошибка предсказания реакции: {str(e)}'
            }

    def parse_compounds(self, compounds_str: str) -> List[str]:
        """Парсит строку с соединениями"""
        compounds = []
        for comp in re.split(r'\s*\+\s*', compounds_str.strip()):
            if comp:
                compounds.append(comp.strip())
        return compounds

    def get_compound_info(self, formula: str) -> Optional[Dict]:
        """Возвращает информацию о соединении"""
        return self.compound_db.get(formula)

    def generate_ionic_equations(self, reactants: List[str], products: List[str], original_eq: str) -> Dict:
        """Генерирует полные и сокращенные ионные уравнения"""
        try:
            # Собираем информацию о всех соединениях
            all_compounds = []
            for formula in reactants + products:
                info = self.get_compound_info(formula)
                if info:
                    all_compounds.append(info)
                else:
                    # Если нет в базе, создаем базовую информацию
                    all_compounds.append({
                        'formula': formula,
                        'cation': '?',
                        'anion': '?',
                        'solubility': '?',
                        'description': 'Неизвестное соединение'
                    })

            # Генерируем полное ионное уравнение
            total_ionic_parts = []

            # Реагенты
            for i, formula in enumerate(reactants):
                info = self.get_compound_info(formula)
                if info and info['solubility'] in ['р', 'м']:  # Растворимые диссоциируют
                    total_ionic_parts.append(info['cation'])
                    total_ionic_parts.append(info['anion'])
                else:
                    total_ionic_parts.append(formula)

            total_ionic_parts.append('→')

            # Продукты
            for i, formula in enumerate(products):
                info = self.get_compound_info(formula)
                if info and info['solubility'] in ['р', 'м']:  # Растворимые диссоциируют
                    total_ionic_parts.append(info['cation'])
                    total_ionic_parts.append(info['anion'])
                else:
                    total_ionic_parts.append(formula)

            total_ionic = ' + '.join(total_ionic_parts).replace('+ → +', '→')

            # Генерируем сокращенное ионное уравнение
            # Находим ионы-наблюдатели (те, что не меняются)
            spectator_ions = []
            net_ionic_reactants = []
            net_ionic_products = []

            # Упрощенный алгоритм: ищем осадки
            precipitates = []
            for formula in products:
                info = self.get_compound_info(formula)
                if info and info['solubility'] == 'н':  # Нерастворимый продукт
                    precipitates.append(formula)
                    # В сокращенном уравнении показываем ионы, образующие осадок
                    for reactant in reactants:
                        r_info = self.get_compound_info(reactant)
                        if r_info:
                            if r_info['cation'] == info['cation'] or r_info['anion'] == info['anion']:
                                if r_info['formula'] not in net_ionic_reactants:
                                    net_ionic_reactants.append(r_info['formula'])

            if not net_ionic_reactants:
                # Если не нашли осадков, используем полное уравнение
                net_ionic = total_ionic
            else:
                net_ionic = ' + '.join(net_ionic_reactants) + ' → ' + ' + '.join(precipitates)

            # Определяем тип реакции
            reaction_type = self.determine_reaction_type(reactants, products, precipitates)

            # Информация о растворимости
            solubility_info = []
            for formula in reactants + products:
                info = self.get_compound_info(formula)
                if info:
                    solubility_info.append({
                        'formula': formula,
                        'solubility': info['solubility'],
                        'description': info['description'],
                        'is_precipitate': info['solubility'] == 'н'
                    })

            return {
                'error': False,
                'original_equation': original_eq,
                'molecular_equation': original_eq,
                'total_ionic_equation': total_ionic,
                'net_ionic_equation': net_ionic,
                'spectator_ions': spectator_ions,
                'precipitates': precipitates,
                'reaction_type': reaction_type,
                'solubility_info': solubility_info,
                'notes': self.generate_notes(reactants, products, precipitates)
            }

        except Exception as e:
            return {
                'error': True,
                'message': f'Ошибка генерации уравнений: {str(e)}'
            }

    def determine_reaction_type(self, reactants: List[str], products: List[str], precipitates: List[str]) -> str:
        """Определяет тип реакции"""
        # Проверяем на осадок
        if precipitates:
            return 'Реакция обмена с образованием осадка'

        # Проверяем на кислоту и основание
        acids = ['HCl', 'H2SO4', 'HNO3', 'H3PO4']
        bases = ['NaOH', 'KOH', 'Ca(OH)2', 'Ba(OH)2']

        has_acid = any(r in acids for r in reactants)
        has_base = any(r in bases for r in reactants)
        has_water = 'H2O' in products

        if has_acid and has_base and has_water:
            return 'Реакция нейтрализации'

        return 'Реакция обмена'

    def generate_notes(self, reactants: List[str], products: List[str], precipitates: List[str]) -> List[str]:
        """Генерирует пояснительные заметки"""
        notes = []

        if precipitates:
            notes.append(f'Образуется осадок: {", ".join(precipitates)}')

        # Проверяем растворимость
        for formula in products:
            info = self.get_compound_info(formula)
            if info:
                if info['solubility'] == 'р':
                    notes.append(f'{formula} - растворимое соединение')
                elif info['solubility'] == 'м':
                    notes.append(f'{formula} - малорастворимое соединение')
                elif info['solubility'] == 'н':
                    notes.append(f'{formula} - нерастворимое соединение (осадок)')

        return notes


# Основные функции плагина (как у Ле Шателье)
def solve_ionic_equation(equation: str) -> Dict:
    """
    Основная функция для решения ионного уравнения

    Args:
        equation: Строка с уравнением (реагенты или полное уравнение)

    Returns:
        Словарь с результатами
    """
    solver = IonicEquationSolver()
    return solver.solve_ionic_equation(equation)


def get_example_equations() -> List[Dict]:
    """Возвращает примеры уравнений для демонстрации"""
    return [
        {
            'input': 'NaCl + AgNO3',
            'description': 'Образование осадка AgCl'
        },
        {
            'input': 'HCl + NaOH',
            'description': 'Реакция нейтрализации'
        },
        {
            'input': 'BaCl2 + Na2SO4',
            'description': 'Образование осадка BaSO4'
        },
        {
            'input': 'CaCO3 + HCl',
            'description': 'Выделение газа CO2'
        },
        {
            'input': 'NaCl + AgNO3 = AgCl + NaNO3',
            'description': 'Готовое уравнение'
        }
    ]


def get_content():
    """Возвращает данные плагина (как у Ле Шателье)"""
    return {
        'type': 'ionic_equation_solver',
        'config': PLUGIN_CONFIG,
        'examples': get_example_equations(),
        'instructions': '''
            Введите уравнение в одном из форматов:
            1. Только реагенты: NaCl + AgNO3
            2. Полное уравнение: NaCl + AgNO3 = AgCl + NaNO3
            3. Со стрелкой: NaCl + AgNO3 → AgCl + NaNO3

            Примеры:
            • NaCl + AgNO3
            • HCl + NaOH
            • BaCl2 + Na2SO4
            • CaCO3 + HCl
        '''
    }
