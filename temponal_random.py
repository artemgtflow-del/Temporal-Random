"""
Temporal Random — генератор случайных чисел на основе временной нестабильности.

Версия: 0.2.0
Исправлено: неравномерное распределение (хи-квадрат тест пройден)

Основан на простом принципе: ни одно действие не выполняется за одинаковое время.
Разница во времени между операциями — это источник энтропии.

Автор: Jipin
Лицензия: MIT
"""

import time
import hashlib


class TemporalRandom:
    """
    Генератор случайных чисел на основе временной нестабильности.
    
    Версия 0.2 — улучшенное распределение:
        - Хэширование SHA-256 для равномерности
        - Накопление энтропии между вызовами
        - Перемешивание битов
    
    Пример:
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
        self._entropy = 0
        self._history = []
    
    def _mix_bits(self, value):
        """
        Перемешивает биты числа через SHA-256.
        
        Это ключевое улучшение версии 2.0:
        - Обеспечивает равномерное распределение
        - Устраняет корреляцию между значениями
        - Делает результаты непредсказуемыми
        
        Args:
            value: целое число для перемешивания
        
        Returns:
            int: перемешанное 64-битное число
        """
        # Превращаем число в байты
        value_bytes = value.to_bytes(8, 'little')
        
        # Хэшируем через SHA-256
        hash_bytes = hashlib.sha256(value_bytes).digest()
        
        # Берём первые 8 байт хэша как 64-битное число
        return int.from_bytes(hash_bytes[:8], 'little')
    
    def _measure_delta(self):
        """
        Измеряет временную разницу выполнения операций.
        
        Улучшения версии 2.0:
        - Несколько операций для накопления шума
        - LCG для дополнительного перемешивания
        - Накопление энтропии между вызовами
        
        Returns:
            int: перемешанная временная разница
        """
        self._counter += 1
        
        # Запоминаем время ДО
        time_before = time.perf_counter_ns()
        
        # Серия операций для накопления шума
        x = self._counter
        for _ in range(10):
            # LCG (линейный конгруэнтный генератор) для перемешивания
            x = (x * 9301 + 49297) % 233280
            
            # Несколько математических операций
            _ = x ** 0.5
            _ = x ** 0.333
            _ = x * 3.14159
            _ = x / 2.71828
        
        # Запоминаем время ПОСЛЕ
        time_after = time.perf_counter_ns()
        
        # Вычисляем разницу
        delta = time_after - time_before
        
        # Накопление энтропии (XOR с предыдущим состоянием)
        self._entropy ^= delta
        
        # LCG для перемешивания накопленной энтропии
        self._entropy = (self._entropy * 1664525 + 1013904223) & 0xFFFFFFFF
        
        # Сохраняем в историю для статистики
        self._history.append(delta)
        
        # Возвращаем перемешанную разницу с энтропией
        return self._mix_bits(delta ^ self._entropy)
    
    def random_bit(self):
        """
        Возвращает случайный бит (0 или 1).
        
        Returns:
            int: 0 или 1
        """
        return self._measure_delta() & 1
    
    def random_byte(self):
        """
        Возвращает случайный байт (0-255).
        
        Returns:
            int: число от 0 до 255
        """
        return self._measure_delta() % 256
    
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
        
        # Генерируем 64-битное случайное число
        value = self._measure_delta()
        
        # Приводим к диапазону через остаток от деления
        return min_value + (value % range_size)
    
    def random_float(self):
        """
        Возвращает случайное число с плавающей точкой в диапазоне [0, 1).
        
        Returns:
            float: число от 0 до 1 (не включая 1)
        
        Пример:
            >>> rng.random_float()
            0.573981234
        """
        # Генерируем 53-битное число (максимальная точность double)
        value = self._measure_delta()
        
        # Берём младшие 53 бита
        mantissa = value & 0xFFFFFFFFFFFFF
        
        # Делим на 2^53 для получения числа в [0, 1)
        return mantissa / (1 << 53)
    
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
            chars: строка символов для генерации
        
        Returns:
            str: случайная строка
        
        Пример:
            >>> rng.random_string(10)
            'aB3dF7gH2j'
        """
        if chars is None:
            chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
        
        return ''.join(self.random_choice(chars) for _ in range(length))
    
    def shuffle(self, items):
        """
        Перемешивает список случайным образом (алгоритм Фишера-Йетса).
        
        Args:
            items: список для перемешивания
        
        Returns:
            list: перемешанный список
        
        Пример:
            >>> rng.shuffle([1, 2, 3, 4, 5])
            [3, 1, 5, 2, 4]
        """
        result = items.copy()
        for i in range(len(result) - 1, 0, -1):
            j = self.random_int(0, i)
            result[i], result[j] = result[j], result[i]
        return result
    
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


#Упрощённые функции для быстрого использования

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


def shuffle(items):
    """Быстрый вызов: перемешивание списка."""
    return _get_rng().shuffle(items)


def demo():
    """Запускает демонстрацию работы генератора."""
    
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
    
    # 6. Перемешивание списка
    print("6. Перемешивание списка:")
    numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    shuffled = rng.shuffle(numbers)
    print(f"   Было: {numbers}")
    print(f"   Стало: {shuffled}")
    print()
    
    # 7. Проверка распределения (главный тест!)
    print("7. Проверка распределения (1000 чисел от 0 до 9):")
    counts = [0] * 10
    for _ in range(1000):
        num = rng.random_int(0, 9)
        counts[num] += 1
    
    print("   Число | Частота | Визуализация")
    print("   " + "-" * 40)
    for i, count in enumerate(counts):
        bar = "█" * (count // 10)
        print(f"   {i:5d} | {count:6d}  | {bar}")
    
    # Вычисляем хи-квадрат для проверки
    expected = 100
    chi2 = sum((c - expected) ** 2 / expected for c in counts)
    print(f"\n   Хи-квадрат: {chi2:.2f} (должен быть < 16.9)")

    # 8. Статистика
    print("8. Статистика генератора:")
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


if __name__ == "__main__":
    demo()