import re
from typing import Dict, List, Tuple, Optional

PLUGIN_CONFIG = {
    'name': "Таблица растворимости веществ",
    'description': 'Интерактивная таблица растворимости солей, оснований и кислот',
    'icon': 'flask-vial',
    'version': '2.0.0',
    'enabled': True,
    'route': '/plugin/solubility_table'
}

# Хуёвая база данных растворимости (основные соединения)
SOLUBILITY_DATA = {
    # Катионы
    'H⁺': {'name': 'Водород', 'color': '#FF9FF3'},
    'Li⁺': {'name': 'Литий', 'color': '#54A0FF'},
    'Na⁺': {'name': 'Натрий', 'color': '#1DD1A1'},
    'K⁺': {'name': 'Калий', 'color': '#FECA57'},
    'NH₄⁺': {'name': 'Аммоний', 'color': '#5F27CD'},
    'Mg²⁺': {'name': 'Магний', 'color': '#FF6B6B'},
    'Ca²⁺': {'name': 'Кальций', 'color': '#48DBFB'},
    'Ba²⁺': {'name': 'Барий', 'color': '#10AC84'},
    'Sr²⁺': {'name': 'Стронций', 'color': '#8395A7'},
    'Al³⁺': {'name': 'Алюминий', 'color': '#8395A7'},
    'Cr³⁺': {'name': 'Хром', 'color': '#B33939'},
    'Zn²⁺': {'name': 'Цинк', 'color': '#706FD3'},
    'Mn²⁺': {'name': 'Марганец', 'color': '#CD6133'},
    'Fe²⁺': {'name': 'Железо (II)', 'color': '#D6A2E8'},
    'Fe³⁺': {'name': 'Железо (III)', 'color': '#E66767'},
    'Co²⁺': {'name': 'Кобальт', 'color': '#596275'},
    'Ni²⁺': {'name': 'Никель', 'color': '#596275'},
    'Cu²⁺': {'name': 'Медь', 'color': '#596275'},
    'Ag⁺': {'name': 'Серебро', 'color': '#596275'},
    'Hg²⁺': {'name': 'Ртуть', 'color': '#596275'},
    'Pb²⁺': {'name': 'Свинец', 'color': '#596275'},

    # Анионы
    'OH⁻': {'name': 'Гидроксид', 'color': '#FDA7DF'},
    'F⁻': {'name': 'Фторид', 'color': '#FDA7DF'},
    'Cl⁻': {'name': 'Хлорид', 'color': '#FDA7DF'},
    'Br⁻': {'name': 'Бромид', 'color': '#FDA7DF'},
    'I⁻': {'name': 'Иодид', 'color': '#FDA7DF'},
    'S²⁻': {'name': 'Сульфид', 'color': '#ED4C67'},
    'HS⁻': {'name': 'Гидросульфид', 'color': '#B53471'},
    'NO₃': {'name': 'Нитрат', 'color': '#833471'},
    'SO₃²⁻': {'name': 'Сульфит', 'color': '#006266'},
    'SO₄²⁻': {'name': 'Сульфат', 'color': '#5758BB'},
    'S₂O₃²⁻': {'name': 'Тиосульфат', 'color': '#12CBC4'},
    'CO₃²⁻': {'name': 'Карбонат', 'color': '#0652DD'},
    'SiO₃²⁻': {'name': 'Силикат', 'color': '#009432'},
    'PO₄³⁻': {'name': 'Фосфат', 'color': '#EA2027'},
    'CrO₄²⁻': {'name': 'Хромат', 'color': '#FFC312'},
    'CH₃COO⁻': {'name': 'Ацетат', 'color': '#C4E538'},
}

SOLUBILITY_MATRIX = {
    # --- ГИДРОКСИДЫ (OH⁻) ---
    'H⁺ + OH⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'Li⁺ + OH⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'Na⁺ + OH⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'K⁺ + OH⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'NH₄⁺ + OH⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'Ba²⁺ + OH⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'Sr²⁺ + OH⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'Ca²⁺ + OH⁻': {'sol': 'м', 'desc': 'Малорастворим', 'color': '#F1C40F'},
    'Mg²⁺ + OH⁻': {'sol': 'н', 'desc': 'Нерастворим', 'color': '#E74C3C'},
    'Al³⁺ + OH⁻': {'sol': 'н', 'desc': 'Нерастворим', 'color': '#E74C3C'},
    'Cr³⁺ + OH⁻': {'sol': 'н', 'desc': 'Нерастворим', 'color': '#E74C3C'},
    'Zn²⁺ + OH⁻': {'sol': 'н', 'desc': 'Нерастворим', 'color': '#E74C3C'},
    'Mn²⁺ + OH⁻': {'sol': 'н', 'desc': 'Нерастворим', 'color': '#E74C3C'},
    'Fe²⁺ + OH⁻': {'sol': 'н', 'desc': 'Нерастворим', 'color': '#E74C3C'},
    'Fe³⁺ + OH⁻': {'sol': 'н', 'desc': 'Нерастворим', 'color': '#E74C3C'},
    'Co²⁺ + OH⁻': {'sol': 'н', 'desc': 'Нерастворим', 'color': '#E74C3C'},
    'Ni²⁺ + OH⁻': {'sol': 'н', 'desc': 'Нерастворим', 'color': '#E74C3C'},
    'Cu²⁺ + OH⁻': {'sol': 'н', 'desc': 'Нерастворим', 'color': '#E74C3C'},
    'Ag⁺ + OH⁻': {'sol': '-', 'desc': 'Не существует', 'color': '#95A5A6'},
    'Hg²⁺ + OH⁻': {'sol': 'н', 'desc': 'Нерастворим', 'color': '#E74C3C'},
    'Pb²⁺ + OH⁻': {'sol': 'н', 'desc': 'Нерастворим', 'color': '#E74C3C'},

    # --- НИТРАТЫ (NO₃⁻) ---
    'H⁺ + NO₃⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'Li⁺ + NO₃⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'Na⁺ + NO₃⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'K⁺ + NO₃⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'NH₄⁺ + NO₃⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'Mg²⁺ + NO₃⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'Ca²⁺ + NO₃⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'Ba²⁺ + NO₃⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'Sr²⁺ + NO₃⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'Al³⁺ + NO₃⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'Cr³⁺ + NO₃⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'Zn²⁺ + NO₃⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'Mn²⁺ + NO₃⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'Fe²⁺ + NO₃⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'Fe³⁺ + NO₃⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'Co²⁺ + NO₃⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'Ni²⁺ + NO₃⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'Cu²⁺ + NO₃⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'Ag⁺ + NO₃⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'Hg²⁺ + NO₃⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'Pb²⁺ + NO₃⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},

    # --- ХЛОРИДЫ (Cl⁻) ---
    'H⁺ + Cl⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'Li⁺ + Cl⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'Na⁺ + Cl⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'K⁺ + Cl⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'NH₄⁺ + Cl⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'Mg²⁺ + Cl⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'Ca²⁺ + Cl⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'Ba²⁺ + Cl⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'Sr²⁺ + Cl⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'Al³⁺ + Cl⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'Cr³⁺ + Cl⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'Zn²⁺ + Cl⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'Mn²⁺ + Cl⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'Fe²⁺ + Cl⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'Fe³⁺ + Cl⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'Co²⁺ + Cl⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'Ni²⁺ + Cl⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'Cu²⁺ + Cl⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'Ag⁺ + Cl⁻': {'sol': 'н', 'desc': 'Нерастворим', 'color': '#E74C3C'},
    'Hg²⁺ + Cl⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'Pb²⁺ + Cl⁻': {'sol': 'м', 'desc': 'Малорастворим', 'color': '#F1C40F'},

    # --- СУЛЬФАТЫ (SO₄²⁻) ---
    'H⁺ + SO₄²⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'Li⁺ + SO₄²⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'Na⁺ + SO₄²⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'K⁺ + SO₄²⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'NH₄⁺ + SO₄²⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'Mg²⁺ + SO₄²⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'Ca²⁺ + SO₄²⁻': {'sol': 'м', 'desc': 'Малорастворим', 'color': '#F1C40F'},
    'Ba²⁺ + SO₄²⁻': {'sol': 'н', 'desc': 'Нерастворим', 'color': '#E74C3C'},
    'Sr²⁺ + SO₄²⁻': {'sol': 'н', 'desc': 'Нерастворим', 'color': '#E74C3C'},
    'Al³⁺ + SO₄²⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'Cr³⁺ + SO₄²⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'Zn²⁺ + SO₄²⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'Mn²⁺ + SO₄²⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'Fe²⁺ + SO₄²⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'Fe³⁺ + SO₄²⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'Co²⁺ + SO₄²⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'Ni²⁺ + SO₄²⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'Cu²⁺ + SO₄²⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'Ag⁺ + SO₄²⁻': {'sol': 'м', 'desc': 'Малорастворим', 'color': '#F1C40F'},
    'Hg²⁺ + SO₄²⁻': {'sol': 'м', 'desc': 'Малорастворим', 'color': '#F1C40F'},
    'Pb²⁺ + SO₄²⁻': {'sol': 'н', 'desc': 'Нерастворим', 'color': '#E74C3C'},

    # --- СУЛЬФИДЫ (S²⁻) ---
    'H⁺ + S²⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'Li⁺ + S²⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'Na⁺ + S²⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'K⁺ + S²⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'NH₄⁺ + S²⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'Mg²⁺ + S²⁻': {'sol': '-', 'desc': 'Не существует', 'color': '#95A5A6'},
    'Ca²⁺ + S²⁻': {'sol': 'м', 'desc': 'Малорастворим', 'color': '#F1C40F'},
    'Ba²⁺ + S²⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'Sr²⁺ + S²⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'Al³⁺ + S²⁻': {'sol': '-', 'desc': 'Не существует', 'color': '#95A5A6'},
    'Cr³⁺ + S²⁻': {'sol': '-', 'desc': 'Не существует', 'color': '#95A5A6'},
    'Zn²⁺ + S²⁻': {'sol': 'н', 'desc': 'Нерастворим', 'color': '#E74C3C'},
    'Mn²⁺ + S²⁻': {'sol': 'н', 'desc': 'Нерастворим', 'color': '#E74C3C'},
    'Fe²⁺ + S²⁻': {'sol': 'н', 'desc': 'Нерастворим', 'color': '#E74C3C'},
    'Fe³⁺ + S²⁻': {'sol': '-', 'desc': 'Не существует', 'color': '#95A5A6'},
    'Co²⁺ + S²⁻': {'sol': 'н', 'desc': 'Нерастворим', 'color': '#E74C3C'},
    'Ni²⁺ + S²⁻': {'sol': 'н', 'desc': 'Нерастворим', 'color': '#E74C3C'},
    'Cu²⁺ + S²⁻': {'sol': 'н', 'desc': 'Нерастворим', 'color': '#E74C3C'},
    'Ag⁺ + S²⁻': {'sol': 'н', 'desc': 'Нерастворим', 'color': '#E74C3C'},
    'Hg²⁺ + S²⁻': {'sol': 'н', 'desc': 'Нерастворим', 'color': '#E74C3C'},
    'Pb²⁺ + S²⁻': {'sol': 'н', 'desc': 'Нерастворим', 'color': '#E74C3C'},

    # --- КАРБОНАТЫ (CO₃²⁻) ---
    'H⁺ + CO₃²⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'Li⁺ + CO₃²⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'Na⁺ + CO₃²⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'K⁺ + CO₃²⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'NH₄⁺ + CO₃²⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'Mg²⁺ + CO₃²⁻': {'sol': 'н', 'desc': 'Нерастворим', 'color': '#E74C3C'},
    'Ca²⁺ + CO₃²⁻': {'sol': 'н', 'desc': 'Нерастворим', 'color': '#E74C3C'},
    'Ba²⁺ + CO₃²⁻': {'sol': 'н', 'desc': 'Нерастворим', 'color': '#E74C3C'},
    'Sr²⁺ + CO₃²⁻': {'sol': 'н', 'desc': 'Нерастворим', 'color': '#E74C3C'},
    'Al³⁺ + CO₃²⁻': {'sol': '-', 'desc': 'Не существует', 'color': '#95A5A6'},
    'Cr³⁺ + CO₃²⁻': {'sol': '-', 'desc': 'Не существует', 'color': '#95A5A6'},
    'Zn²⁺ + CO₃²⁻': {'sol': 'н', 'desc': 'Нерастворим', 'color': '#E74C3C'},
    'Mn²⁺ + CO₃²⁻': {'sol': 'н', 'desc': 'Нерастворим', 'color': '#E74C3C'},
    'Fe²⁺ + CO₃²⁻': {'sol': 'н', 'desc': 'Нерастворим', 'color': '#E74C3C'},
    'Fe³⁺ + CO₃²⁻': {'sol': '-', 'desc': 'Не существует', 'color': '#95A5A6'},
    'Co²⁺ + CO₃²⁻': {'sol': 'н', 'desc': 'Нерастворим', 'color': '#E74C3C'},
    'Ni²⁺ + CO₃²⁻': {'sol': 'н', 'desc': 'Нерастворим', 'color': '#E74C3C'},
    'Cu²⁺ + CO₃²⁻': {'sol': '-', 'desc': 'Не существует', 'color': '#95A5A6'},
    'Ag⁺ + CO₃²⁻': {'sol': 'н', 'desc': 'Нерастворим', 'color': '#E74C3C'},
    'Hg²⁺ + CO₃²⁻': {'sol': '-', 'desc': 'Не существует', 'color': '#95A5A6'},
    'Pb²⁺ + CO₃²⁻': {'sol': 'н', 'desc': 'Нерастворим', 'color': '#E74C3C'},

    # --- ФОСФАТЫ (PO₄³⁻) ---
    'H⁺ + PO₄³⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'Li⁺ + PO₄³⁻': {'sol': 'н', 'desc': 'Нерастворим', 'color': '#E74C3C'},
    'Na⁺ + PO₄³⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'K⁺ + PO₄³⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'NH₄⁺ + PO₄³⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'Mg²⁺ + PO₄³⁻': {'sol': 'н', 'desc': 'Нерастворим', 'color': '#E74C3C'},
    'Ca²⁺ + PO₄³⁻': {'sol': 'н', 'desc': 'Нерастворим', 'color': '#E74C3C'},
    'Ba²⁺ + PO₄³⁻': {'sol': 'н', 'desc': 'Нерастворим', 'color': '#E74C3C'},
    'Sr²⁺ + PO₄³⁻': {'sol': 'н', 'desc': 'Нерастворим', 'color': '#E74C3C'},
    'Al³⁺ + PO₄³⁻': {'sol': 'н', 'desc': 'Нерастворим', 'color': '#E74C3C'},
    'Cr³⁺ + PO₄³⁻': {'sol': 'н', 'desc': 'Нерастворим', 'color': '#E74C3C'},
    'Zn²⁺ + PO₄³⁻': {'sol': 'н', 'desc': 'Нерастворим', 'color': '#E74C3C'},
    'Mn²⁺ + PO₄³⁻': {'sol': 'н', 'desc': 'Нерастворим', 'color': '#E74C3C'},
    'Fe²⁺ + PO₄³⁻': {'sol': 'н', 'desc': 'Нерастворим', 'color': '#E74C3C'},
    'Fe³⁺ + PO₄³⁻': {'sol': 'н', 'desc': 'Нерастворим', 'color': '#E74C3C'},
    'Co²⁺ + PO₄³⁻': {'sol': 'н', 'desc': 'Нерастворим', 'color': '#E74C3C'},
    'Ni²⁺ + PO₄³⁻': {'sol': 'н', 'desc': 'Нерастворим', 'color': '#E74C3C'},
    'Cu²⁺ + PO₄³⁻': {'sol': 'н', 'desc': 'Нерастворим', 'color': '#E74C3C'},
    'Ag⁺ + PO₄³⁻': {'sol': 'н', 'desc': 'Нерастворим', 'color': '#E74C3C'},
    'Hg²⁺ + PO₄³⁻': {'sol': 'н', 'desc': 'Нерастворим', 'color': '#E74C3C'},
    'Pb²⁺ + PO₄³⁻': {'sol': 'н', 'desc': 'Нерастворим', 'color': '#E74C3C'},

    # --- СИЛИКАТЫ (SiO₃²⁻) ---
    'H⁺ + SiO₃²⁻': {'sol': 'н', 'desc': 'Нерастворим', 'color': '#E74C3C'},
    'Li⁺ + SiO₃²⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'Na⁺ + SiO₃²⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'K⁺ + SiO₃²⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'NH₄⁺ + SiO₃²⁻': {'sol': '-', 'desc': 'Не существует', 'color': '#95A5A6'},
    'Mg²⁺ + SiO₃²⁻': {'sol': 'н', 'desc': 'Нерастворим', 'color': '#E74C3C'},
    'Ca²⁺ + SiO₃²⁻': {'sol': 'н', 'desc': 'Нерастворим', 'color': '#E74C3C'},
    'Ba²⁺ + SiO₃²⁻': {'sol': 'н', 'desc': 'Нерастворим', 'color': '#E74C3C'},
    'Sr²⁺ + SiO₃²⁻': {'sol': 'н', 'desc': 'Нерастворим', 'color': '#E74C3C'},
    'Zn²⁺ + SiO₃²⁻': {'sol': 'н', 'desc': 'Нерастворим', 'color': '#E74C3C'},
    'Fe²⁺ + SiO₃²⁻': {'sol': 'н', 'desc': 'Нерастворим', 'color': '#E74C3C'},
    'Pb²⁺ + SiO₃²⁻': {'sol': 'н', 'desc': 'Нерастворим', 'color': '#E74C3C'},

    # --- АЦЕТАТЫ (CH₃COO⁻) ---
    'H⁺ + CH₃COO⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'Li⁺ + CH₃COO⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'Na⁺ + CH₃COO⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'K⁺ + CH₃COO⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'NH₄⁺ + CH₃COO⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'Mg²⁺ + CH₃COO⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'Ca²⁺ + CH₃COO⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'Ba²⁺ + CH₃COO⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'Al³⁺ + CH₃COO⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'},
    'Ag⁺ + CH₃COO⁻': {'sol': 'м', 'desc': 'Малорастворим', 'color': '#F1C40F'},
    'Pb²⁺ + CH₃COO⁻': {'sol': 'р', 'desc': 'Растворим', 'color': '#1ABC9C'}
}

def generate_full_table() -> Dict:
    """Генерирует полную таблицу растворимости"""
    try:
        # Сортируем катионы и анионы
        cations = sorted([k for k in SOLUBILITY_DATA.keys() if '+' in k])
        anions = sorted([k for k in SOLUBILITY_DATA.keys() if '-' in k])

        table_data = []

        # Для каждого катиона
        for cation in cations:
            row = {
                'cation': cation,
                'cation_name': SOLUBILITY_DATA[cation]['name'],
                'cation_color': SOLUBILITY_DATA[cation]['color'],
                'anions': []
            }

            # Для каждого аниона
            for anion in anions:
                key = (cation, anion)
                if key in SOLUBILITY_MATRIX:
                    data = SOLUBILITY_MATRIX[key]
                    row['anions'].append({
                        'anion': anion,
                        'anion_name': SOLUBILITY_DATA[anion]['name'],
                        'solubility': data['sol'],
                        'description': data['desc'],
                        'color': data['color'],
                        'formula': f'{cation[:-1]}{anion.replace("-", "")}'
                    })
                else:
                    row['anions'].append({
                        'anion': anion,
                        'anion_name': SOLUBILITY_DATA[anion]['name'],
                        'solubility': '?',
                        'description': 'Нет данных',
                        'color': '#95A5A6',
                        'formula': f'{cation[:-1]}{anion.replace("-", "")}'
                    })

            table_data.append(row)

        # Общие правила растворимости
        rules = [
            'Все нитраты (NO₃⁻) растворимы',
            'Все соли натрия, калия, аммония растворимы',
            'Хлориды, бромиды, иодиды растворимы, кроме Ag⁺, Pb²⁺, Hg₂²⁺',
            'Сульфаты растворимы, кроме Ba²⁺, Pb²⁺, Ca²⁺ (малорастворим)',
            'Карбонаты, фосфаты, сульфиты нерастворимы, кроме Na⁺, K⁺, NH₄⁺',
            'Гидроксиды нерастворимы, кроме Na⁺, K⁺, Ba²⁺, Ca²⁺ (малорастворим)'
        ]

        return {
            'error': False,
            'cations': cations,
            'anions': anions,
            'table': table_data,
            'rules': rules,
            'total_compounds': len(cations) * len(anions),
            'legend': {
                'р': {'text': 'Растворим', 'color': '#1ABC9C'},
                'м': {'text': 'Малорастворим', 'color': '#F1C40F'},
                'н': {'text': 'Нерастворим', 'color': '#E74C3C'},
                '?': {'text': 'Нет данных', 'color': '#95A5A6'}
            }
        }

    except Exception as e:
        return {
            'error': True,
            'message': f'Ошибка генерации таблицы: {str(e)}'
        }


def search_compound(query: str) -> Dict:
    """Поиск соединения по формуле или названию"""
    try:
        query = query.lower().strip()
        results = []

        # Ищем в матрице растворимости
        for (cation, anion), data in SOLUBILITY_MATRIX.items():
            cation_name = SOLUBILITY_DATA[cation]['name'].lower()
            anion_name = SOLUBILITY_DATA[anion]['name'].lower()

            # Генерируем возможные формулы
            formulas = []
            if cation == 'NH4+':
                formulas.append(f'(nh4){anion.replace("-", "").lower()}')
                formulas.append(f'nh4{anion.replace("-", "").lower()}')
            else:
                cation_part = cation.lower().replace('+', '')
                anion_part = anion.lower().replace('-', '').replace('^', '')
                formulas.append(f'{cation_part}{anion_part}')
                formulas.append(f'{cation_part}{anion_part}'.replace('2', '₂').replace('3', '₃'))

            # Проверяем совпадение
            for formula in formulas:
                if query in formula or query in cation_name or query in anion_name:
                    results.append({
                        'cation': cation,
                        'anion': anion,
                        'formula': formula.upper(),
                        'solubility': data['sol'],
                        'description': data['desc'],
                        'color': data['color']
                    })
                    break

        return {
            'error': False,
            'query': query,
            'results': results[:20],  # Ограничиваем 20 результатами
            'count': len(results)
        }

    except Exception as e:
        return {
            'error': True,
            'message': f'Ошибка поиска: {str(e)}'
        }


def get_content():
    """Возвращает данные плагина таблицы растворимости"""
    return {
        'type': 'solubility_table',
        'config': PLUGIN_CONFIG,
        'capabilities': {
            'check_solubility': True,
            'full_table': True,
            'search': True,
            'rules': True
        },
        'statistics': {
            'cations': len([k for k in SOLUBILITY_DATA.keys() if '+' in k]),
            'anions': len([k for k in SOLUBILITY_DATA.keys() if '-' in k]),
            'compounds': len(SOLUBILITY_MATRIX)
        }
    }