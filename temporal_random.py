#!/usr/bin/env python3
"""
Temporal Random — генератор случайных чисел на основе временной нестабильности.

Версия: 1.4.0
Новые функции:
    - Асинхронная генерация
    - Генерация дат и времени (12/24 часа)
    - Генерация координат (географические)
    - Генерация цветов (hex, rgb, hsl)
    - Генерация мнемонических паролей

Автор: Jipin
Лицензия: MIT
"""

import time
import hashlib
import threading
import argparse
import sys
import asyncio
import datetime
import math
from typing import List, Any, Optional, Union, Tuple


class TemporalRandom:
    """
    Генератор случайных чисел на основе временной нестабильности.
    
    Версия 1.4.0 — новые функции:
        - Асинхронная генерация
        - Даты и время (12/24 часа)
        - Географические координаты
        - Цвета (hex, rgb, hsl)
        - Мнемонические пароли
    """
    
    def __init__(self, seed: Optional[int] = None):
        """
        Инициализация генератора.
        
        Args:
            seed: опциональное начальное значение для воспроизводимости.
        """
        self._counter = 0
        self._entropy = 0
        self._history = []
        self._lock = threading.Lock()
        self._seed = seed
        self._use_seed = seed is not None
        
        # Слова для мнемонических паролей
        self._words = [
            "apple", "banana", "cherry", "dragon", "eagle",
            "falcon", "garden", "hunter", "island", "joker",
            "knight", "lion", "moon", "night", "ocean",
            "panda", "queen", "river", "storm", "tiger",
            "cloud", "dream", "forest", "glory", "heart",
            "jade", "king", "light", "magic", "nature"
        ]
        
        if self._use_seed:
            self._counter = seed
            self._entropy = seed
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self._history.clear()
        return False
    
    def _mix_bits(self, value: int) -> int:
        """Перемешивает биты числа через SHA-256."""
        value_bytes = value.to_bytes(8, 'little')
        hash_bytes = hashlib.sha256(value_bytes).digest()
        return int.from_bytes(hash_bytes[:8], 'little')
    
    def _measure_delta(self) -> int:
        """Измеряет временную разницу выполнения операций."""
        with self._lock:
            self._counter += 1
            
            if self._use_seed:
                self._counter = (self._counter * 1103515245 + 12345) & 0x7FFFFFFF
                self._entropy = (self._entropy * 1664525 + 1013904223) & 0xFFFFFFFF
                return self._mix_bits(self._counter ^ self._entropy)
            
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
        return self._measure_delta() & 1
    
    def random_byte(self) -> int:
        return self._measure_delta() % 256
    
    def random_int(self, min_value: int = 0, max_value: int = 100) -> int:
        if min_value > max_value:
            raise ValueError("min_value не может быть больше max_value")
        range_size = max_value - min_value + 1
        value = self._measure_delta()
        return min_value + (value % range_size)
    
    def random_float(self) -> float:
        high = self._measure_delta() & 0xFFFFFFFF
        low = self._measure_delta() & 0xFFFFFFFF
        value = (high << 32) | low
        return value / (1 << 64)
    
    def random_choice(self, items: List[Any]) -> Any:
        if not items:
            raise ValueError("Список не может быть пустым")
        if len(items) == 1:
            return items[0]
        return items[self.random_int(0, len(items) - 1)]
    
    def random_string(self, length: int = 8, chars: Optional[str] = None) -> str:
        if length < 0:
            raise ValueError("Длина не может быть отрицательной")
        if length == 0:
            return ""
        if chars is None:
            chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
        return ''.join(self.random_choice(chars) for _ in range(length))
    
    def shuffle(self, items: List[Any]) -> List[Any]:
        result = items.copy()
        for i in range(len(result) - 1, 0, -1):
            j = self.random_int(0, i)
            result[i], result[j] = result[j], result[i]
        return result
    
    def sample(self, population: List[Any], k: int) -> List[Any]:
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
        with self._lock:
            self._history.clear()
    

    async def random_int_async(self, min_value: int = 0, max_value: int = 100) -> int:
        """Асинхронная версия random_int."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.random_int, min_value, max_value)
    
    async def random_float_async(self) -> float:
        """Асинхронная версия random_float."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.random_float)
    
    async def random_byte_async(self) -> int:
        """Асинхронная версия random_byte."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.random_byte)
    
    async def random_string_async(self, length: int = 8, chars: Optional[str] = None) -> str:
        """Асинхронная версия random_string."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.random_string, length, chars)
    
    async def generate_batch(self, count: int, min_value: int = 0, max_value: int = 100) -> List[int]:
        """Генерирует batch чисел асинхронно."""
        tasks = [self.random_int_async(min_value, max_value) for _ in range(count)]
        return await asyncio.gather(*tasks)
    
    
    def random_date(self, start: Optional[datetime.date] = None, 
                    end: Optional[datetime.date] = None) -> datetime.date:
        """
        Генерирует случайную дату.
        
        Args:
            start: начальная дата (по умолчанию 2000-01-01)
            end: конечная дата (по умолчанию сегодня)
        
        Returns:
            datetime.date: случайная дата
        """
        if start is None:
            start = datetime.date(2000, 1, 1)
        if end is None:
            end = datetime.date.today()
        
        delta = (end - start).days
        random_days = self.random_int(0, max(0, delta))
        return start + datetime.timedelta(days=random_days)
    
    def random_datetime(self, start: Optional[datetime.datetime] = None,
                        end: Optional[datetime.datetime] = None) -> datetime.datetime:
        """
        Генерирует случайный datetime.
        
        Args:
            start: начальная дата-время (по умолчанию 2000-01-01 00:00:00)
            end: конечная дата-время (по умолчанию сейчас)
        
        Returns:
            datetime.datetime: случайный datetime
        """
        if start is None:
            start = datetime.datetime(2000, 1, 1)
        if end is None:
            end = datetime.datetime.now()
        
        delta = (end - start).total_seconds()
        random_seconds = self.random_int(0, int(max(0, delta)))
        return start + datetime.timedelta(seconds=random_seconds)
    
    def random_time_12h(self) -> str:
        """
        Генерирует случайное время в 12-часовом формате.
        
        Returns:
            str: время в формате "02:30:45 PM"
        """
        hour = self.random_int(1, 12)
        minute = self.random_int(0, 59)
        second = self.random_int(0, 59)
        am_pm = self.random_choice(["AM", "PM"])
        return f"{hour:02d}:{minute:02d}:{second:02d} {am_pm}"
    
    def random_time_24h(self) -> str:
        """
        Генерирует случайное время в 24-часовом формате.
        
        Returns:
            str: время в формате "14:30:45"
        """
        hour = self.random_int(0, 23)
        minute = self.random_int(0, 59)
        second = self.random_int(0, 59)
        return f"{hour:02d}:{minute:02d}:{second:02d}"
    
    def random_timestamp_id(self) -> str:
        """
        Генерирует ID с временной меткой и случайной частью.
        
        Returns:
            str: ID вида "1700000000000-a1b2c3d4"
        """
        timestamp = int(time.time() * 1000)
        random_part = self.random_string(8, "0123456789abcdef")
        return f"{timestamp}-{random_part}"
    
    def random_short_id(self, length: int = 8) -> str:
        """
        Генерирует короткий ID для URL.
        
        Args:
            length: длина ID (по умолчанию 8)
        
        Returns:
            str: короткий ID
        """
        chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        return self.random_string(length, chars)
    

    def random_lat_lng(self) -> Tuple[float, float]:
        """
        Генерирует случайные географические координаты.
        
        Returns:
            tuple: (широта, долгота) в градусах
        """
        lat = self.random_float() * 180 - 90    # -90..90
        lng = self.random_float() * 360 - 180   # -180..180
        return (lat, lng)
    
    def random_point_in_circle(self, cx: float, cy: float, radius: float) -> Tuple[float, float]:
        """
        Генерирует случайную точку внутри круга.
        
        Args:
            cx: центр X
            cy: центр Y
            radius: радиус круга
        
        Returns:
            tuple: (x, y) координаты точки
        """
        angle = self.random_float() * 2 * math.pi
        r = radius * math.sqrt(self.random_float())
        return (cx + r * math.cos(angle), cy + r * math.sin(angle))
    
    def random_point_in_rect(self, x1: float, y1: float, x2: float, y2: float) -> Tuple[float, float]:
        """
        Генерирует случайную точку внутри прямоугольника.
        
        Args:
            x1, y1: левый нижний угол
            x2, y2: правый верхний угол
        
        Returns:
            tuple: (x, y) координаты точки
        """
        min_x = min(x1, x2)
        max_x = max(x1, x2)
        min_y = min(y1, y2)
        max_y = max(y1, y2)
        
        x = self.random_float() * (max_x - min_x) + min_x
        y = self.random_float() * (max_y - min_y) + min_y
        return (x, y)
    
    
    def random_hex_color(self, with_hash: bool = True) -> str:
        """
        Генерирует случайный hex-цвет.
        
        Args:
            with_hash: добавлять # в начале (по умолчанию True)
        
        Returns:
            str: цвет в формате "#RRGGBB" или "RRGGBB"
        """
        color = ''.join(f'{self.random_byte():02x}' for _ in range(3))
        return f"#{color}" if with_hash else color
    
    def random_rgb_color(self) -> Tuple[int, int, int]:
        """
        Генерирует случайный RGB-цвет.
        
        Returns:
            tuple: (r, g, b) каждый 0-255
        """
        return (self.random_byte(), self.random_byte(), self.random_byte())
    
    def random_rgb_color_str(self) -> str:
        """
        Генерирует случайный RGB-цвет в виде строки.
        
        Returns:
            str: цвет в формате "rgb(255, 128, 64)"
        """
        r, g, b = self.random_rgb_color()
        return f"rgb({r}, {g}, {b})"
    
    def random_hsl_color(self) -> Tuple[float, float, float]:
        """
        Генерирует случайный HSL-цвет.
        
        Returns:
            tuple: (h, s, l) где h 0-360, s 0-100, l 0-100
        """
        h = self.random_float() * 360
        s = 50 + self.random_float() * 50      # 50-100
        l = 30 + self.random_float() * 40      # 30-70
        return (h, s, l)
    
    def random_hsl_color_str(self) -> str:
        """
        Генерирует случайный HSL-цвет в виде строки.
        
        Returns:
            str: цвет в формате "hsl(240, 75%, 50%)"
        """
        h, s, l = self.random_hsl_color()
        return f"hsl({h:.0f}, {s:.0f}%, {l:.0f}%)"
    
    def random_color_name(self) -> str:
        """
        Возвращает случайное название цвета.
        
        Returns:
            str: название цвета
        """
        colors = [
            "red", "blue", "green", "yellow", "orange", "purple",
            "pink", "brown", "black", "white", "gray", "cyan",
            "magenta", "lime", "teal", "navy", "olive", "maroon",
            "coral", "indigo", "violet", "gold", "silver", "bronze"
        ]
        return self.random_choice(colors)
    
    
    def random_mnemonic(self, word_count: int = 4, separator: str = "-") -> str:
        """
        Генерирует мнемонический пароль из случайных слов.
        
        Args:
            word_count: количество слов (по умолчанию 4)
            separator: разделитель (по умолчанию "-")
        
        Returns:
            str: мнемонический пароль
        
        Пример:
            >>> rng.random_mnemonic(4)
            "apple-dragon-river-tiger"
        """
        if word_count < 1:
            raise ValueError("word_count должен быть больше 0")
        words = [self.random_choice(self._words) for _ in range(word_count)]
        return separator.join(words)
    
    def random_mnemonic_with_number(self, word_count: int = 3, separator: str = "-") -> str:
        """
        Генерирует мнемонический пароль со случайным числом в конце.
        
        Args:
            word_count: количество слов (по умолчанию 3)
            separator: разделитель (по умолчанию "-")
        
        Returns:
            str: мнемонический пароль с числом
        
        Пример:
            >>> rng.random_mnemonic_with_number(3)
            "apple-dragon-river-42"
        """
        words = [self.random_choice(self._words) for _ in range(word_count)]
        number = self.random_int(10, 999)
        return separator.join(words) + f"{separator}{number}"


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

def random_date(start: Optional[datetime.date] = None, 
                end: Optional[datetime.date] = None) -> datetime.date:
    return _get_rng().random_date(start, end)


def random_datetime(start: Optional[datetime.datetime] = None,
                    end: Optional[datetime.datetime] = None) -> datetime.datetime:
    return _get_rng().random_datetime(start, end)


def random_time_12h() -> str:
    return _get_rng().random_time_12h()


def random_time_24h() -> str:
    return _get_rng().random_time_24h()


def random_timestamp_id() -> str:
    return _get_rng().random_timestamp_id()


def random_short_id(length: int = 8) -> str:
    return _get_rng().random_short_id(length)


def random_lat_lng() -> Tuple[float, float]:
    return _get_rng().random_lat_lng()


def random_point_in_circle(cx: float, cy: float, radius: float) -> Tuple[float, float]:
    return _get_rng().random_point_in_circle(cx, cy, radius)


def random_point_in_rect(x1: float, y1: float, x2: float, y2: float) -> Tuple[float, float]:
    return _get_rng().random_point_in_rect(x1, y1, x2, y2)


def random_hex_color(with_hash: bool = True) -> str:
    return _get_rng().random_hex_color(with_hash)


def random_rgb_color() -> Tuple[int, int, int]:
    return _get_rng().random_rgb_color()


def random_rgb_color_str() -> str:
    return _get_rng().random_rgb_color_str()


def random_hsl_color() -> Tuple[float, float, float]:
    return _get_rng().random_hsl_color()


def random_hsl_color_str() -> str:
    return _get_rng().random_hsl_color_str()


def random_color_name() -> str:
    return _get_rng().random_color_name()


def random_mnemonic(word_count: int = 4, separator: str = "-") -> str:
    return _get_rng().random_mnemonic(word_count, separator)


def random_mnemonic_with_number(word_count: int = 3, separator: str = "-") -> str:
    return _get_rng().random_mnemonic_with_number(word_count, separator)

def _run_cli():
    parser = argparse.ArgumentParser(
        description="Temporal Random — генератор случайных чисел",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
  %(prog)s -n 10                          # 10 чисел от 0 до 100
  %(prog)s -n 5 --float                   # 5 чисел с плавающей точкой
  %(prog)s --seed 42 -n 10                # воспроизводимая последовательность
  %(prog)s --string -l 16                 # случайный пароль
  %(prog)s --choice A B C D               # случайный выбор
  
  # НОВЫЕ ФУНКЦИИ:
  %(prog)s --date                         # случайная дата
  %(prog)s --time-12h                     # время в 12-часовом формате
  %(prog)s --time-24h                     # время в 24-часовом формате
  %(prog)s --coords                       # случайные координаты
  %(prog)s --hex-color                    # случайный hex-цвет
  %(prog)s --rgb-color                    # случайный RGB-цвет
  %(prog)s --mnemonic -w 4                # мнемонический пароль
        """
    )
    
    # Основные параметры
    parser.add_argument('-n', '--count', type=int, default=1, help='Количество чисел')
    parser.add_argument('-m', '--min', type=int, default=0, help='Минимальное значение')
    parser.add_argument('-M', '--max', type=int, default=100, help='Максимальное значение')
    
    # Режимы (новые)
    parser.add_argument('--float', action='store_true', help='Числа с плавающей точкой')
    parser.add_argument('--byte', action='store_true', help='Байты 0-255')
    parser.add_argument('--string', action='store_true', help='Случайная строка')
    parser.add_argument('-l', '--length', type=int, default=8, help='Длина строки')
    parser.add_argument('--choice', nargs='+', help='Выбор из списка')
    
    # НОВЫЕ РЕЖИМЫ
    parser.add_argument('--date', action='store_true', help='Случайная дата')
    parser.add_argument('--datetime', action='store_true', help='Случайный datetime')
    parser.add_argument('--time-12h', action='store_true', help='Время 12-часовой формат')
    parser.add_argument('--time-24h', action='store_true', help='Время 24-часовой формат')
    parser.add_argument('--timestamp-id', action='store_true', help='ID с меткой времени')
    parser.add_argument('--short-id', type=int, nargs='?', const=8, help='Короткий ID')
    
    parser.add_argument('--coords', action='store_true', help='Случайные координаты')
    parser.add_argument('--circle', nargs=3, type=float, metavar=('CX', 'CY', 'R'), 
                        help='Точка внутри круга')
    parser.add_argument('--rect', nargs=4, type=float, metavar=('X1', 'Y1', 'X2', 'Y2'),
                        help='Точка внутри прямоугольника')
    
    parser.add_argument('--hex-color', action='store_true', help='Случайный hex-цвет')
    parser.add_argument('--rgb-color', action='store_true', help='Случайный RGB-цвет')
    parser.add_argument('--hsl-color', action='store_true', help='Случайный HSL-цвет')
    parser.add_argument('--color-name', action='store_true', help='Случайное название цвета')
    
    parser.add_argument('--mnemonic', action='store_true', help='Мнемонический пароль')
    parser.add_argument('-w', '--words', type=int, default=4, help='Количество слов')
    parser.add_argument('-s', '--separator', type=str, default='-', help='Разделитель')
    
    # Управление
    parser.add_argument('--seed', type=int, help='Установить seed')
    parser.add_argument('--no-seed', action='store_true', help='Отключить seed')
    parser.add_argument('--stats', action='store_true', help='Статистика')
    
    args = parser.parse_args()
    
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
    
    # --- НОВЫЕ РЕЖИМЫ ---
    
    if args.date:
        print(rng.random_date())
        return
    
    if args.datetime:
        print(rng.random_datetime())
        return
    
    if args.time_12h:
        print(rng.random_time_12h())
        return
    
    if args.time_24h:
        print(rng.random_time_24h())
        return
    
    if args.timestamp_id:
        print(rng.random_timestamp_id())
        return
    
    if args.short_id is not None:
        print(rng.random_short_id(args.short_id))
        return
    
    if args.coords:
        lat, lng = rng.random_lat_lng()
        print(f"Широта: {lat:.6f}, Долгота: {lng:.6f}")
        return
    
    if args.circle:
        cx, cy, radius = args.circle
        x, y = rng.random_point_in_circle(cx, cy, radius)
        print(f"X: {x:.6f}, Y: {y:.6f}")
        return
    
    if args.rect:
        x1, y1, x2, y2 = args.rect
        x, y = rng.random_point_in_rect(x1, y1, x2, y2)
        print(f"X: {x:.6f}, Y: {y:.6f}")
        return
    
    if args.hex_color:
        print(rng.random_hex_color())
        return
    
    if args.rgb_color:
        r, g, b = rng.random_rgb_color()
        print(f"RGB({r}, {g}, {b})")
        return
    
    if args.hsl_color:
        h, s, l = rng.random_hsl_color()
        print(f"HSL({h:.0f}°, {s:.0f}%, {l:.0f}%)")
        return
    
    if args.color_name:
        print(rng.random_color_name())
        return
    
    if args.mnemonic:
        if args.separator:
            print(rng.random_mnemonic(args.words, args.separator))
        else:
            print(rng.random_mnemonic(args.words))
        return
    
    # --- СТАНДАРТНЫЕ РЕЖИМЫ ---
    
    if args.choice:
        print(rng.random_choice(args.choice))
        return
    
    if args.string:
        print(rng.random_string(args.length))
        return
    
    if args.byte:
        for _ in range(args.count):
            print(rng.random_byte())
        return
    
    if args.float:
        for _ in range(args.count):
            print(rng.random_float())
        return

if __name__ == "__main__":
    _run_cli()
