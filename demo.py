#!/usr/bin/env python3
"""
Демонстрация работы генератора Temporal Random.

Запуск:
    python demo.py

Версия: 1.4.0
"""

from temporal_random import TemporalRandom
import datetime


def print_section(title: str):
    """Печатает раздел сзаголовком."""
    print(f"  {title}")


def main():
    """Запускает демонстрацию работы генератора."""

    print("ГЕНЕРАТОР TEMPORAL RANDOM — ВЕРСИЯ 1.4.0")
    print("НОВЫЕ ФУНКЦИИ: Асинхронность, Даты, Координаты, Цвета, Пароли")
    
    rng = TemporalRandom()
    
    
    print_section("1. БАЗОВЫЕ ФУНКЦИИ")
    
    print("   Случайные целые числа (0-99):")
    for i in range(5):
        print(f"      {i+1}. {rng.random_int(0, 99)}")
    
    print("\n   Случайные числа с плавающей точкой (0-1):")
    for i in range(3):
        print(f"      {rng.random_float():.10f}")
    
    print("\n   Случайные байты (0-255):")
    for i in range(3):
        print(f"      {rng.random_byte():3d} = {rng.random_byte():08b}")

    print_section("2. ДАТЫ И ВРЕМЯ")
    
    print("   Случайная дата (2000-01-01 .. сегодня):")
    print(f"      {rng.random_date()}")
    
    print("\n   Случайная дата в конкретном диапазоне:")
    start = datetime.date(2020, 1, 1)
    end = datetime.date(2025, 12, 31)
    print(f"      Диапазон: {start} .. {end}")
    print(f"      Результат: {rng.random_date(start, end)}")
    
    print("\n   Случайный datetime (2000-01-01 .. сейчас):")
    print(f"      {rng.random_datetime()}")
    
    print("\n   Время в 12-часовом формате:")
    for i in range(3):
        print(f"      {rng.random_time_12h()}")
    
    print("\n   Время в 24-часовом формате:")
    for i in range(3):
        print(f"      {rng.random_time_24h()}")

    print_section("3. ID И КЛЮЧИ")
    
    print("   ID с временной меткой:")
    for i in range(3):
        print(f"      {rng.random_timestamp_id()}")
    
    print("\n   Короткие ID (длина 8 символов):")
    for i in range(3):
        print(f"      {rng.random_short_id(8)}")
    
    print("\n   Короткие ID (длина 12 символов):")
    for i in range(3):
        print(f"      {rng.random_short_id(12)}")
   
    print_section("4. КООРДИНАТЫ")
    
    print("   Случайные географические координаты:")
    for i in range(3):
        lat, lng = rng.random_lat_lng()
        print(f"      {i+1}. Широта: {lat:.6f}, Долгота: {lng:.6f}")
    
    print("\n   Точки внутри круга (центр 0,0, радиус 10):")
    for i in range(3):
        x, y = rng.random_point_in_circle(0, 0, 10)
        print(f"      {i+1}. ({x:.3f}, {y:.3f})")
    
    print("\n   Точки внутри прямоугольника (0,0 .. 100,100):")
    for i in range(3):
        x, y = rng.random_point_in_rect(0, 0, 100, 100)
        print(f"      {i+1}. ({x:.1f}, {y:.1f})")
    
    print_section("5. ЦВЕТА")
    
    print("   Hex-цвета:")
    for i in range(5):
        print(f"      {rng.random_hex_color()}")
    
    print("\n   RGB-цвета:")
    for i in range(3):
        r, g, b = rng.random_rgb_color()
        print(f"      RGB({r:3d}, {g:3d}, {b:3d})")
        print(f"      {rng.random_rgb_color_str()}")
    
    print("\n   HSL-цвета:")
    for i in range(3):
        h, s, l = rng.random_hsl_color()
        print(f"      HSL({h:.0f}°, {s:.0f}%, {l:.0f}%)")
        print(f"      {rng.random_hsl_color_str()}")
    
    print("\n   Названия цветов:")
    for i in range(5):
        print(f"      {rng.random_color_name()}")
    
    print_section("6. МНЕМОНИЧЕСКИЕ ПАРОЛИ")
    
    print("   4 слова через дефис:")
    for i in range(3):
        print(f"      {rng.random_mnemonic(4)}")
    
    print("\n   3 слова через дефис + число:")
    for i in range(3):
        print(f"      {rng.random_mnemonic_with_number(3)}")
    
    print("\n   5 слов через пробел:")
    for i in range(3):
        print(f"      {rng.random_mnemonic(5, ' ')}")
    
    print_section("7. РАБОТА СО СПИСКАМИ")
    
    fruits = ["яблоко", "банан", "вишня", "дыня", "ежевика", "арбуз", "груша"]
    
    print("   Список фруктов:")
    print(f"      {fruits}")
    
    print("\n   Случайный выбор из списка:")
    for i in range(5):
        print(f"      {i+1}. {rng.random_choice(fruits)}")
    
    print("\n   Выборка 3 уникальных элементов:")
    print(f"      {rng.sample(fruits, 3)}")
    
    print("\n   Перемешанный список:")
    print(f"      {rng.shuffle(fruits)}")
    
    print_section("8. ГЕНЕРАЦИЯ СТРОК")
    
    print("   Случайные строки (цифры и буквы):")
    for i in range(3):
        print(f"      {rng.random_string(10)}")
    
    print("\n   Случайные строки (только цифры):")
    digits = "0123456789"
    for i in range(3):
        print(f"      {rng.random_string(8, digits)}")
    
    print("\n   Случайные строки (только заглавные):")
    upper = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    for i in range(3):
        print(f"      {rng.random_string(6, upper)}")
    
    print_section("9. АСИНХРОННАЯ ГЕНЕРАЦИЯ")
    
    import asyncio
    
    async def demo_async():
        print("   Генерация 10 чисел асинхронно:")
        numbers = await rng.generate_batch(10, 0, 50)
        print(f"      {numbers}")
        
        print("\n   Асинхронная генерация строк:")
        tasks = [rng.random_string_async(6) for _ in range(3)]
        strings = await asyncio.gather(*tasks)
        for s in strings:
            print(f"      {s}")
    
    asyncio.run(demo_async())
    print_section("10. СТАТИСТИКА ГЕНЕРАТОРА")
    
    stats = rng.get_statistics()
    print(f"   Измерений:          {stats['count']}")
    print(f"   Среднее время:      {stats['mean_ns']:.2f} нс")
    print(f"   Минимум:            {stats['min_ns']} нс")
    print(f"   Максимум:           {stats['max_ns']} нс")
    print(f"   Разброс:            {stats['range_ns']} нс")
    print(f"   Коэффициент T:      {stats['T']:.6f}")
    print(f"   T × 100%:           {stats['T_percent']:.4f}%")
    print(f"   Режим seed:         {'Да' if stats['seed_mode'] else 'Нет'}")
    if stats['seed_mode']:
        print(f"   Текущий seed:       {stats['seed']}")

    print_section("11. ВОСПРОИЗВОДИМОСТЬ (seed)")
    
    print("   Генератор с seed=42:")
    rng_seed = TemporalRandom(seed=42)
    numbers1 = [rng_seed.random_int(0, 100) for _ in range(5)]
    print(f"      Первый запуск: {numbers1}")
    
    rng_seed2 = TemporalRandom(seed=42)
    numbers2 = [rng_seed2.random_int(0, 100) for _ in range(5)]
    print(f"      Второй запуск: {numbers2}")
    print(f"      Совпадают: {'ДА' if numbers1 == numbers2 else 'НЕТ'}")
    
    print("\n   Генератор без seed (каждый раз разный):")
    rng_no_seed = TemporalRandom()
    nums1 = [rng_no_seed.random_int(0, 100) for _ in range(3)]
    print(f"      Первый запуск: {nums1}")
    
    rng_no_seed2 = TemporalRandom()
    nums2 = [rng_no_seed2.random_int(0, 100) for _ in range(3)]
    print(f"      Второй запуск: {nums2}")
    
    print()
    print("  Все функции работают корректно!")
    print()
    print("  Для справки:")
    print("    python temporal_random.py --help  -  справка по CLI")
    print("    python tests.py                  -  запуск тестов")

if __name__ == "__main__":
    main()