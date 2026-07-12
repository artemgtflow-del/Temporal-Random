"""
Temporal Random — генератор случайных чисел на основе временной нестабильности.

Основан на простом принципе: ни одно действие не выполняется за одинаковое время.
Разница во времени между двумя одинаковыми операциями и есть источник энтропии.

Автор: Jipin
Версия: 0.1.0
"""

import time
import sys


class TemporalRandom:
    """
    Генератор случайных чисел на основе временной нестабильности.
    
    Принцип работы:
        1. Запоминаем время до выполнения операции
        2. Выполняем фиксированную операцию
        3. Запоминаем время после выполнения
        4. Разница между временами — это и есть случайное значение
    
    Пример использования:
        >>> rng = TemporalRandom()
        >>> rng.random_int(0, 100)
        42
        >>> rng.random_float()
        0.731
        >>> rng.random_choice(['яблоко', 'банан', 'вишня'])
        'банан'
    """
    
    def __init__(self):
        """Инициализация генератора."""
        self._counter = 0
        self._history = []
    
    def _measure_delta(self):
        """
        Измеряет временную разницу выполнения операции.
        
        Returns:
            int: разница в наносекундах (всегда положительная)
        """
        # Счётчик нужен, чтобы операция не была оптимизирована компилятором
        self._counter += 1
        
        # Запоминаем время ДО
        time_before = time.perf_counter_ns()
        
        # Выполняем фиксированную операцию
        # Корень из числа — простая, но не мгновенная операция
        _ = self._counter ** 0.5
        
        # Запоминаем время ПОСЛЕ
        time_after = time.perf_counter_ns()
        
        # Возвращаем разницу
        delta = time_after - time_before
        self._history.append(delta)
        return delta
    
    def random_bit(self):
        """
        Возвращает случайный бит (0 или 1).
        
        Returns:
            int: 0 или 1
        """
        # Берём последний бит временной разницы
        # Он непредсказуем из-за шумов процессора
        return self._measure_delta() & 1
    
    def random_byte(self):
        """
        Возвращает случайный байт (0-255).
        
        Returns:
            int: число от 0 до 255
        """
        result = 0
        for i in range(8):
            result |= self.random_bit() << i
        return result
    
    def random_int(self, min_value=0, max_value=100):
        """
        Возвращает случайное целое число в заданном диапазоне.
        
        Args:
            min_value: минимальное значение (включительно)
            max_value: максимальное значение (включительно)
        
        Returns:
            int: случайное число в диапазоне [min_value, max_value]
        
        Пример:
            >>> rng.random_int(0, 10)
            7
        """
        if min_value > max_value:
            raise ValueError("min_value не может быть больше max_value")
        
        range_size = max_value - min_value + 1
        bits_needed = range_size.bit_length()
        
        # Генерируем случайное число нужной длины в битах
        result = 0
        for _ in range(bits_needed):
            result = (result << 1) | self.random_bit()
        
        # Приводим к диапазону через остаток от деления
        return min_value + (result % range_size)
    
    def random_float(self):
        """
        Возвращает случайное число с плавающей точкой в диапазоне [0, 1).
        
        Returns:
            float: число от 0 до 1 (не включая 1)
        
        Пример:
            >>> rng.random_float()
            0.573981234
        """
        # Генерируем 53 бита (максимальная точность double)
        value = 0
        for i in range(53):
            value |= self.random_bit() << i
        
        # Делим на 2^53, чтобы получить число в [0, 1)
        return value / (1 << 53)
    
    def random_choice(self, items):
        """
        Выбирает случайный элемент из списка.
        
        Args:
            items: список или кортеж элементов
        
        Returns:
            element: случайный элемент из списка
        
        Пример:
            >>> rng.random_choice(['A', 'B', 'C'])
            'B'
        """
        if not items:
            raise ValueError("Список не может быть пустым")
        
        index = self.random_int(0, len(items) - 1)
        return items[index]
    
    def random_string(self, length=8, chars=None):
        """
        Генерирует случайную строку заданной длины.
        
        Args:
            length: длина строки
            chars: строка символов для генерации (по умолчанию буквы + цифры)
        
        Returns:
            str: случайная строка
        
        Пример:
            >>> rng.random_string(10)
            'aB3dF7gH2j'
        """
        if chars is None:
            chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
        
        return ''.join(self.random_choice(chars) for _ in range(length))
    
    def get_statistics(self):
        """
        Возвращает статистику работы генератора.
        
        Returns:
            dict: статистика временных разниц
        """
        if not self._history:
            return {"count": 0}
        
        deltas = self._history
        mean = sum(deltas) / len(deltas)
        min_val = min(deltas)
        max_val = max(deltas)
        
        # Вычисляем коэффициент нестабильности T
        deviations = [abs(d - mean) / mean for d in deltas]
        T = sum(deviations) / len(deviations)
        
        return {
            "count": len(deltas),
            "mean_ns": mean,
            "min_ns": min_val,
            "max_ns": max_val,
            "range_ns": max_val - min_val,
            "T": T,
            "T_percent": T * 100
        }


# ---- Упрощённые функции для быстрого использования ----

_rng = None

def _get_rng():
    """Возвращает экземпляр генератора (синглтон)."""
    global _rng
    if _rng is None:
        _rng = TemporalRandom()
    return _rng


def random_int(min_value=0, max_value=100):
    """Быстрый вызов: случайное целое число."""
    return _get_rng().random_int(min_value, max_value)


def random_float():
    """Быстрый вызов: случайное число с плавающей точкой."""
    return _get_rng().random_float()


def random_byte():
    """Быстрый вызов: случайный байт."""
    return _get_rng().random_byte()


def random_choice(items):
    """Быстрый вызов: случайный элемент из списка."""
    return _get_rng().random_choice(items)


def random_string(length=8, chars=None):
    """Быстрый вызов: случайная строка."""
    return _get_rng().random_string(length, chars)


# ---- ДЕМОНСТРАЦИЯ РАБОТЫ ----

def demo():
    """Запускает демонстрацию работы генератора."""
    print("=" * 70)
    print("ГЕНЕРАТОР СЛУЧАЙНЫХ ЧИСЕЛ НА ОСНОВЕ ВРЕМЕННОЙ НЕСТАБИЛЬНОСТИ")
    print("=" * 70)
    print()
    
    # Создаём экземпляр генератора
    rng = TemporalRandom()
    
    # 1. Случайные целые числа
    print("1. Случайные целые числа (0-99):")
    for i in range(10):
        print(f"   {i+1:2d}. {rng.random_int(0, 99)}")
    print()
    
    # 2. Случайные числа с плавающей точкой
    print("2. Случайные числа с плавающей точкой (0-1):")
    for i in range(5):
        print(f"   {rng.random_float():.10f}")
    print()
    
    # 3. Случайные байты
    print("3. Случайные байты (0-255):")
    for i in range(8):
        byte = rng.random_byte()
        print(f"   {byte:3d} = {byte:08b} (двоичный вид)")
    print()
    
    # 4. Случайный выбор из списка
    fruits = ["яблоко", "банан", "вишня", "дыня", "ежевика"]
    print("4. Случайный выбор из списка:")
    for i in range(5):
        print(f"   Выбор {i+1}: {rng.random_choice(fruits)}")
    print()
    
    # 5. Генерация паролей
    print("5. Случайные пароли (длина 12 символов):")
    for i in range(3):
        password = rng.random_string(12)
        print(f"   Пароль {i+1}: {password}")
    print()
    
    # 6. Проверка распределения
    print("6. Проверка распределения (1000 чисел от 0 до 9):")
    counts = [0] * 10
    for _ in range(1000):
        num = rng.random_int(0, 9)
        counts[num] += 1
    
    print("   Число | Частота | Визуализация")
    print("   " + "-" * 40)
    for i, count in enumerate(counts):
        bar = "█" * (count // 10)
        print(f"   {i:5d} | {count:6d}  | {bar}")
    print()
    
    # 7. Статистика
    print("7. Статистика генератора:")
    stats = rng.get_statistics()
    print(f"   Измерений: {stats['count']}")
    print(f"   Среднее время: {stats['mean_ns']:.2f} нс")
    print(f"   Минимум: {stats['min_ns']} нс")
    print(f"   Максимум: {stats['max_ns']} нс")
    print(f"   Разброс: {stats['range_ns']} нс")
    print(f"   Коэффициент нестабильности T: {stats['T']:.6f}")
    print(f"   T × 100%: {stats['T_percent']:.4f}%")
    print()
    
    print("=" * 70)
    print("Демонстрация завершена!")
    print("=" * 70)
    
    # Проверка: если запущен как скрипт, показываем демо
    if not sys.stdin.isatty():
        input("\nНажмите Enter для выхода...")


# ---- ЗАПУСК ----

if __name__ == "__main__":
    demo()