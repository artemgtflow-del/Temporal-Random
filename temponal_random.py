#!/usr/bin/env python3
"""
Temporal Random — генератор случайных чисел на основе временной нестабильности.

Версия: 1.3.3

Основан на простом принципе: ни одно действие не выполняется за одинаковое время.
Разница во времени между операциями — это источник энтропии.

Использование как библиотеки:
    from temporal_random import TemporalRandom
    rng = TemporalRandom()
    print(rng.random_int(0, 100))

Использование как CLI:
    python temporal_random.py -n 10
    python temporal_random.py --seed 42 -n 5
    python temporal_random.py --string -l 16

Автор: Jipin
Лицензия: MIT
"""

import time
import hashlib
import threading
import argparse
import sys
from typing import List, Any, Optional, Union


class TemporalRandom:
    """
    Генератор случайных чисел на основе временной нестабильности.
    
    Версия 1.3.3 — стабильный релиз:
        - Хэширование SHA-256 для равномерности
        - Накопление энтропии между вызовами
        - Перемешивание битов
        - Потокобезопасность
        - Type hints
        - Контекстный менеджер
        - Опциональный seed для воспроизводимости
    
    Пример:
        >>> rng = TemporalRandom()
        >>> rng.random_int(0, 100)
        42
        
        >>> rng = TemporalRandom(seed=12345)
        >>> rng.random_int(0, 100)  # всегда будет одинаковое число
        73
    """
    
    def __init__(self, seed: Optional[int] = None):
        """
        Инициализация генератора.
        
        Args:
            seed: опциональное начальное значение для воспроизводимости.
                  Если указано, генератор работает в режиме совместимости
                  с стандартным random (псевдослучайный, но воспроизводимый).
                  Если не указано — использует временную нестабильность.
        """
        self._counter = 0
        self._entropy = 0
        self._history = []
        self._lock = threading.Lock()
        self._seed = seed
        self._use_seed = seed is not None
        
        if self._use_seed:
            self._counter = seed
            self._entropy = seed
    
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
        
        Args:
            value: целое число для перемешивания
        
        Returns:
            int: перемешанное 64-битное число
        """
        value_bytes = value.to_bytes(8, 'little')
        hash_bytes = hashlib.sha256(value_bytes).digest()
        return int.from_bytes(hash_bytes[:8], 'little')
    
    def _measure_delta(self) -> int:
        """
        Измеряет временную разницу выполнения операций.
        
        Returns:
            int: перемешанная временная разница
        """
        with self._lock:
            self._counter += 1
            
            if self._use_seed:
                # Режим воспроизводимости (как random)
                self._counter = (self._counter * 1103515245 + 12345) & 0x7FFFFFFF
                self._entropy = (self._entropy * 1664525 + 1013904223) & 0xFFFFFFFF
                return self._mix_bits(self._counter ^ self._entropy)
            
            # Обычный режим — на основе времени
            time_before = time.perf_counter_ns()
            
            x = self._counter
            for _ in range(5):
                x = (x * 9301 + 49297) % 233280
                _ = x ** 0.5
                _ = x ** 0.333
                _ = x * 3.14159
            
            time_after = time.perf_counter_ns()
            delta = time_after - time_before
            
            self._entropy ^= delta
            self._entropy = (self._entropy * 1664525 + 1013904223) & 0xFFFFFFFF
            
            self._history.append(delta)
            
            return self._mix_bits(delta ^ self._entropy)
    
    def random_bit(self) -> int:
        """Возвращает случайный бит (0 или 1)."""
        return self._measure_delta() & 1
    
    def random_byte(self) -> int:
        """Возвращает случайный байт (0-255)."""
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
        """
        if min_value > max_value:
            raise ValueError("min_value не может быть больше max_value")
        
        range_size = max_value - min_value + 1
        value = self._measure_delta()
        return min_value + (value % range_size)
    
    def random_float(self) -> float:
        """
        Возвращает случайное число с плавающей точкой в диапазоне [0, 1).
        
        Returns:
            float: число от 0 до 1 (не включая 1)
        """
        # Генерируем два 32-битных числа для лучшего распределения
        high = self._measure_delta() & 0xFFFFFFFF
        low = self._measure_delta() & 0xFFFFFFFF
        value = (high << 32) | low
        return value / (1 << 64)
    
    def random_choice(self, items: List[Any]) -> Any:
        """
        Выбирает случайный элемент из списка.
        
        Args:
            items: список или кортеж элементов
        
        Returns:
            element: случайный элемент из списка
        
        Raises:
            ValueError: если список пуст
        """
        if not items:
            raise ValueError("Список не может быть пустым")
        if len(items) == 1:
            return items[0]
        return items[self.random_int(0, len(items) - 1)]
    
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
        """
        if stop is None:
            stop = start
            start = 0
        if step == 0:
            raise ValueError("step не может быть равен 0")
        if step == 1:
            return self.random_int(start, stop - 1)
        
        range_size = (stop - start + step - 1) // step
        if range_size <= 0:
            raise ValueError("Пустой диапазон")
        return start + self.random_int(0, range_size - 1) * step
    
    def seed(self, value: Optional[int] = None) -> None:
        """
        Устанавливает seed для воспроизводимости.
        
        После вызова этого метода генератор переключается в режим
        воспроизводимости (как стандартный random).
        
        Args:
            value: значение seed. Если None — переключается обратно
                   на режим временной нестабильности.
        """
        with self._lock:
            if value is None:
                self._use_seed = False
                self._counter = 0
                self._entropy = 0
            else:
                self._use_seed = True
                self._seed = value
                self._counter = value
                self._entropy = value
    
    def get_statistics(self) -> dict:
        """Возвращает статистику работы генератора."""
        with self._lock:
            if not self._history:
                return {
                    "count": 0,
                    "mean_ns": 0.0,
                    "min_ns": 0,
                    "max_ns": 0,
                    "range_ns": 0,
                    "T": 0.0,
                    "T_percent": 0.0,
                    "seed_mode": self._use_seed,
                    "seed": self._seed if self._use_seed else None
                }
            
            deltas = self._history
            mean = sum(deltas) / len(deltas)
            min_val = min(deltas)
            max_val = max(deltas)
            
            deviations = [abs(d - mean) / mean for d in deltas]
            T = sum(deviations) / len(deviations)
            
            return {
                "count": len(deltas),
                "mean_ns": mean,
                "min_ns": min_val,
                "max_ns": max_val,
                "range_ns": max_val - min_val,
                "T": T,
                "T_percent": T * 100,
                "seed_mode": self._use_seed,
                "seed": self._seed if self._use_seed else None
            }
    
    def clear_history(self) -> None:
        """Очищает историю измерений."""
        with self._lock:
            self._history.clear()


_rng = None

def _get_rng() -> TemporalRandom:
    global _rng
    if _rng is None:
        _rng = TemporalRandom()
    return _rng


def random_int(min_value: int = 0, max_value: int = 100) -> int:
    return _get_rng().random_int(min_value, max_value)


def random_float() -> float:
    return _get_rng().random_float()


def random_byte() -> int:
    return _get_rng().random_byte()


def random_choice(items: List[Any]) -> Any:
    return _get_rng().random_choice(items)


def random_string(length: int = 8, chars: Optional[str] = None) -> str:
    return _get_rng().random_string(length, chars)


def shuffle(items: List[Any]) -> List[Any]:
    return _get_rng().shuffle(items)


def sample(population: List[Any], k: int) -> List[Any]:
    return _get_rng().sample(population, k)


def randrange(start: int, stop: Optional[int] = None, step: int = 1) -> int:
    return _get_rng().randrange(start, stop, step)


def seed(value: Optional[int] = None) -> None:
    _get_rng().seed(value)


def _run_cli():
    """Запускает интерфейс командной строки."""
    parser = argparse.ArgumentParser(
        description="Temporal Random — генератор случайных чисел",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
  %(prog)s -n 10                # 10 чисел от 0 до 100
  %(prog)s -n 5 --float         # 5 чисел с плавающей точкой
  %(prog)s --seed 42 -n 10      # воспроизводимая последовательность
  %(prog)s --string -l 16       # случайный пароль
  %(prog)s --choice A B C D     # случайный выбор из списка
  %(prog)s --stats              # статистика генератора
        """
    )
    
    parser.add_argument(
        '-n', '--count',
        type=int,
        default=1,
        help='Количество чисел (по умолчанию: 1)'
    )
    
    parser.add_argument(
        '-m', '--min',
        type=int,
        default=0,
        help='Минимальное значение (по умолчанию: 0)'
    )
    
    parser.add_argument(
        '-M', '--max',
        type=int,
        default=100,
        help='Максимальное значение (по умолчанию: 100)'
    )
    
    parser.add_argument(
        '--float',
        action='store_true',
        help='Генерировать числа с плавающей точкой в диапазоне [0, 1)'
    )
    
    parser.add_argument(
        '--byte',
        action='store_true',
        help='Генерировать байты (0-255)'
    )
    
    parser.add_argument(
        '--string',
        action='store_true',
        help='Генерировать случайную строку'
    )
    
    parser.add_argument(
        '-l', '--length',
        type=int,
        default=8,
        help='Длина строки (для --string, по умолчанию: 8)'
    )
    
    parser.add_argument(
        '--choice',
        nargs='+',
        help='Случайный выбор из переданных элементов'
    )
    
    parser.add_argument(
        '--seed',
        type=int,
        help='Установить seed для воспроизводимости'
    )
    
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Показать статистику генератора'
    )
    
    parser.add_argument(
        '--no-seed',
        action='store_true',
        help='Отключить режим seed (вернуться к временной нестабильности)'
    )
    
    args = parser.parse_args()
    
    # Создаём генератор
    rng = TemporalRandom(seed=args.seed if args.seed is not None else None)
    
    if args.no_seed:
        rng.seed(None)
    
    # Статистика
    if args.stats:
        stats = rng.get_statistics()
        print("Статистика генератора:")
        print("-" * 40)
        print(f"  Измерений:          {stats['count']}")
        print(f"  Среднее время:      {stats['mean_ns']:.2f} нс")
        print(f"  Минимум:            {stats['min_ns']} нс")
        print(f"  Максимум:           {stats['max_ns']} нс")
        print(f"  Разброс:            {stats['range_ns']} нс")
        print(f"  Коэффициент T:      {stats['T']:.6f}")
        print(f"  T × 100%:           {stats['T_percent']:.4f}%")
        print(f"  Режим seed:         {'Да' if stats['seed_mode'] else 'Нет'}")
        if stats['seed_mode']:
            print(f"  Текущий seed:       {stats['seed']}")
        return
    
    # Choice
    if args.choice:
        print(rng.random_choice(args.choice))
        return
    
    # String
    if args.string:
        print(rng.random_string(args.length))
        return
    
    # Byte
    if args.byte:
        for _ in range(args.count):
            print(rng.random_byte())
        return
    
    # Float
    if args.float:
        for _ in range(args.count):
            print(rng.random_float())
        return

if __name__ == "__main__":
    _run_cli()