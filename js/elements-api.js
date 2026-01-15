/**
 * Elements API Client
 * Удобный интерфейс для работы с данными периодической таблицы
 */

class ElementsAPI {
  constructor(baseUrl = "/data/elements") {
    this.baseUrl = baseUrl
    this.cache = null
  }

  /**
   * Получить все элементы
   * @returns {Promise<Object>} Все элементы
   */
  async getAll() {
    if (this.cache) {
      return this.cache
    }

    const response = await fetch(this.baseUrl)
    if (!response.ok) {
      throw new Error("Failed to fetch elements")
    }
    this.cache = await response.json()
    return this.cache
  }

  /**
   * Получить элемент по символу
   * @param {string} symbol - Символ элемента (например, 'H')
   * @returns {Promise<Object>} Данные элемента
   */
  async getBySymbol(symbol) {
    const response = await fetch(`${this.baseUrl}?symbol=${symbol}`)
    if (!response.ok) {
      throw new Error(`Element ${symbol} not found`)
    }
    return await response.json()
  }

  /**
   * Получить элемент по атомному номеру
   * @param {number} number - Атомный номер
   * @returns {Promise<Object>} Данные элемента
   */
  async getByNumber(number) {
    const response = await fetch(`${this.baseUrl}?number=${number}`)
    if (!response.ok) {
      throw new Error(`Element with number ${number} not found`)
    }
    return await response.json()
  }

  /**
   * Получить элементы по категории
   * @param {string} category - Категория (alkali-metal, noble-gas, etc.)
   * @returns {Promise<Object>} Элементы категории
   */
  async getByCategory(category) {
    const response = await fetch(`${this.baseUrl}?category=${category}`)
    if (!response.ok) {
      throw new Error(`Failed to fetch category ${category}`)
    }
    return await response.json()
  }

  /**
   * Получить элементы по периоду
   * @param {number} period - Номер периода (1-7)
   * @returns {Promise<Object>} Элементы периода
   */
  async getByPeriod(period) {
    const response = await fetch(`${this.baseUrl}?period=${period}`)
    if (!response.ok) {
      throw new Error(`Failed to fetch period ${period}`)
    }
    return await response.json()
  }

  /**
   * Получить элементы по группе
   * @param {number} group - Номер группы (1-18)
   * @returns {Promise<Object>} Элементы группы
   */
  async getByGroup(group) {
    const response = await fetch(`${this.baseUrl}?group=${group}`)
    if (!response.ok) {
      throw new Error(`Failed to fetch group ${group}`)
    }
    return await response.json()
  }

  /**
   * Поиск элементов по названию или символу
   * @param {string} query - Поисковый запрос
   * @returns {Promise<Array>} Найденные элементы
   */
  async search(query) {
    const elements = await this.getAll()
    const queryLower = query.toLowerCase()

    return Object.entries(elements)
      .filter(([symbol, data]) => {
        return (
          symbol.toLowerCase().includes(queryLower) ||
          data.name.toLowerCase().includes(queryLower) ||
          data.nameEn.toLowerCase().includes(queryLower) ||
          data.number.toString() === query
        )
      })
      .map(([symbol, data]) => ({ symbol, ...data }))
  }

  /**
   * Получить все категории элементов
   * @returns {Promise<Array>} Список уникальных категорий
   */
  async getCategories() {
    const elements = await this.getAll()
    const categories = new Set(Object.values(elements).map((el) => el.category))
    return Array.from(categories)
  }

  /**
   * Очистить кеш
   */
  clearCache() {
    this.cache = null
  }
}

// Экспорт для использования в других модулях
if (typeof module !== "undefined" && module.exports) {
  module.exports = ElementsAPI
}

// Создать глобальный экземпляр для удобства
const elementsAPI = new ElementsAPI()
