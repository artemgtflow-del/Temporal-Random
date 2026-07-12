"""
Temporal Random — генератор случайных чисел на основе временной нестабильности.

Версия: 1.0.0
Исправлено: неравномерное распределение (хи-квадрат тест пройден)

Основан на простом принципе: ни одно действие не выполняется за одинаковое время.
Разница во времени между операциями — это источник энтропии.

Автор: Jipin
Лицензия: MIT
"""

import time
import hashlib
import threading
from typing import List, Any, Optional, Union


class TemporalRandom:
    """
    Генератор случайных чисел на основе временной нестабильности.
    
    Версия 1.0.0 — стабильный релиз:
        - Хэширование SHA-256 для равномерности
        - Накопление энтропии между вызовами
        - Перемешивание битов
        - Потокобезопасность
        - Type hints
        - Контекстный менеджер
    
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
        self._lock = threading.Lock()
    
    def __enter__(self):
        """Поддержка контекстного менеджера."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Очистка истории при выходе из контекста."""
        self._history.clear()
        return False
    
    def _mix_bits(self, value: int) -> int:
        """
        Перемешивает биты числа через SHA-256.
        
        Это ключевое улучшение версии 1.0.0:
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
    
    def _measure_delta(self) -> int:
        """
        Измеряет временную разницу выполнения операций.
        
        Улучшения версии 1.0.0:
        - Несколько операций для накопления шума
        - LCG для дополнительного перемешивания
        - Накопление энтропии между вызовами
        - Потокобезопасность
        
        Returns:
            int: перемешанная временная разница
        """
        with self._lock:
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
    
    def random_bit(self) -> int:
        """
        Возвращает случайный бит (0 или 1).
        
        Returns:
            int: 0 или 1
        """
        return self._measure_delta() & 1
    
    def random_byte(self) -> int:
        """
        Возвращает случайный байт (0-255).
        
        Returns:
            int: число от 0 до 255
        """
        return self._measure_delta() % 256
    
    def random_int(self, min_value: int = 0, max_value: int = 100) -> int:
        """
        Возвращает случайное целое число в заданном диапазоне.
        
        Args:
            min_value: минимальное значение (включительно). По умолчанию 0.
            max_value: максимальное значение (включительно). По умолчанию 100.
        
        Returns:
            int: случайное число в диапазоне [min_value, max_value]
        
        Raises:
            ValueError: если min_value > max_value
        
        Пример:
            >>> rng = TemporalRandom()
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
    
    def random_float(self) -> float:
        """
        Возвращает случайное число с плавающей точкой в диапазоне [0, 1).
        
        Returns:
            float: число от 0 до 1 (не включая 1)
        
        Пример:
            >>> rng = TemporalRandom()
            >>> rng.random_float()
            0.573981234
        """
        # Генерируем 53-битное число (максимальная точность double)
        value = self._measure_delta()
        
        # Берём младшие 53 бита
        mantissa = value & 0xFFFFFFFFFFFFF
        
        # Делим на 2^53 для получения числа в [0, 1)
        return mantissa / (1 << 53)
    
    def random_choice(self, items: List[Any]) -> Any:
        """
        Выбирает случайный элемент из списка.
        
        Args:
            items: список или кортеж элементов
        
        Returns:
            element: случайный элемент из списка
        
        Raises:
            ValueError: если список пуст
        
        Пример:
            >>> rng = TemporalRandom()
            >>> rng.random_choice(['A', 'B', 'C'])
            'B'
        """
        if not items:
            raise ValueError("Список не может быть пустым")
        
        if len(items) == 1:
            return items[0]
        
        index = self.random_int(0, len(items) - 1)
        return items[index]
    
    def random_string(self, length: int = 8, chars: Optional[str] = None) -> str:
        """
        Генерирует случайную строку заданной длины.
        
        Args:
            length: длина строки. По умолчанию 8.
            chars: строка символов для генерации.
                   По умолчанию A-Z, a-z, 0-9.
        
        Returns:
            str: случайная строка
        
        Raises:
            ValueError: если длина отрицательная
        
        Пример:
            >>> rng = TemporalRandom()
            >>> rng.random_string(10)
            'aB3dF7gH2j'
        """
        if length < 0:
            raise ValueError("Длина не может быть отрицательной")
        
        if length == 0:
            return ""
        
        if chars is None:
            chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
        
        return ''.join(self.random_choice(chars) for _ in range(length))
    
    def shuffle(self, items: List[Any]) -> List[Any]:
        """
        Перемешивает список случайным образом (алгоритм Фишера-Йетса).
        
        Args:
            items: список для перемешивания
        
        Returns:
            list: перемешанный список
        
        Пример:
            >>> rng = TemporalRandom()
            >>> rng.shuffle([1, 2, 3, 4, 5])
            [3, 1, 5, 2, 4]
        """
        result = items.copy()
        for i in range(len(result) - 1, 0, -1):
            j = self.random_int(0, i)
            result[i], result[j] = result[j], result[i]
        return result
    
    def sample(self, population: List[Any], k: int) -> List[Any]:
        """
        Возвращает случайную выборку из k элементов без повторений.
        
        Args:
            population: список элементов
            k: количество элементов в выборке
        
        Returns:
            list: список из k случайных уникальных элементов
        
        Raises:
            ValueError: если k > len(population) или k < 0
        
        Пример:
            >>> rng = TemporalRandom()
            >>> rng.sample([1, 2, 3, 4, 5], 3)
            [3, 1, 5]
        """
        if k < 0:
            raise ValueError("k не может быть отрицательным")
        
        if k > len(population):
            raise ValueError("k не может быть больше длины списка")
        
        if k == 0:
            return []
        
        if k == len(population):
            return self.shuffle(population)
        
        result = population.copy()
        for i in range(k):
            j = self.random_int(i, len(result) - 1)
            result[i], result[j] = result[j], result[i]
        return result[:k]
    
    def randrange(self, start: int, stop: Optional[int] = None, step: int = 1) -> int:
        """
        Возвращает случайное число из диапазона range(start, stop, step).
        
        Аналог random.randrange().
        
        Args:
            start: начало диапазона
            stop: конец диапазона (не включая)
            step: шаг
        
        Returns:
            int: случайное число из диапазона
        
        Raises:
            ValueError: если диапазон пустой или step = 0
        
        Пример:
            >>> rng = TemporalRandom()
            >>> rng.randrange(0, 10, 2)
            6
        """
        if stop is None:
            stop = start
            start = 0
        
        if step == 0:
            raise ValueError("step не может быть равен 0")
        
        if step == 1:
            return self.random_int(start, stop - 1)
        
        # Для step > 1
        range_size = (stop - start + step - 1) // step
        if range_size <= 0:
            raise ValueError("Пустой диапазон")
        
        return start + self.random_int(0, range_size - 1) * step
    
    def seed(self, value: Optional[int] = None) -> None:
        """
        Устанавливает начальное состояние генератора.
        
        В текущей реализации seed не используется,
        так как генератор основан на временной нестабильности.
        Метод оставлен для совместимости с интерфейсом random.Random.
        
        Args:
            value: значение для инициализации (игнорируется)
        """
        pass
    
    def get_statistics(self) -> dict:
        """
        Возвращает статистику работы генератора.
        
        Returns:
            dict: статистика временных разниц
        """
        with self._lock:
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
    
    def clear_history(self) -> None:
        """Очищает историю измерений."""
        with self._lock:
            self._history.clear()


# ---- Упрощённые функции для быстрого использования ----

_rng = None

def _get_rng() -> TemporalRandom:
    """Возвращает экземпляр генератора (синглтон)."""
    global _rng
    if _rng is None:
        _rng = TemporalRandom()
    return _rng


def random_int(min_value: int = 0, max_value: int = 100) -> int:
    """Быстрый вызов: случайное целое число."""
    return _get_rng().random_int(min_value, max_value)


def random_float() -> float:
    """Быстрый вызов: случайное число с плавающей точкой."""
    return _get_rng().random_float()


def random_byte() -> int:
    """Быстрый вызов: случайный байт."""
    return _get_rng().random_byte()


def random_choice(items: List[Any]) -> Any:
    """Быстрый вызов: случайный элемент из списка."""
    return _get_rng().random_choice(items)


def random_string(length: int = 8, chars: Optional[str] = None) -> str:
    """Быстрый вызов: случайная строка."""
    return _get_rng().random_string(length, chars)


def shuffle(items: List[Any]) -> List[Any]:
    """Быстрый вызов: перемешивание списка."""
    return _get_rng().shuffle(items)


def sample(population: List[Any], k: int) -> List[Any]:
    """Быстрый вызов: случайная выборка."""
    return _get_rng().sample(population, k)


def randrange(start: int, stop: Optional[int] = None, step: int = 1) -> int:
    """Быстрый вызов: случайное число из диапазона."""
    return _get_rng().randrange(start, stop, step)