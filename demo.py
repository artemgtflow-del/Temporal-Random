#!/usr/bin/env python3
"""
Демонстрация работы генератора Temporal Random.

Запуск:
    python demo.py
"""

from temporal_random import TemporalRandom


def main():

    # Режим без seed
    print("РЕЖИМ ВРЕМЕННОЙ НЕСТАБИЛЬНОСТИ (без seed)")
    rng = TemporalRandom()
    
    print("   Первые 5 чисел: ", end="")
    for _ in range(5):
        print(rng.random_int(0, 100), end=" ")
    print()
    print("   Ещё 5 чисел:    ", end="")
    for _ in range(5):
        print(rng.random_int(0, 100), end=" ")
    print("\n")
    
    # Режим с seed
    print("РЕЖИМ ВОСПРОИЗВОДИМОСТИ (с seed=42)")
    rng_seed = TemporalRandom(seed=42)
    
    print("   Первые 5 чисел: ", end="")
    for _ in range(5):
        print(rng_seed.random_int(0, 100), end=" ")
    print()
    print("   Ещё 5 чисел:    ", end="")
    for _ in range(5):
        print(rng_seed.random_int(0, 100), end=" ")
    print()
    print("   (При повторном запуске с тем же seed результаты совпадут)")
    print()
    
    # Другие функции
    print("ДРУГИЕ ВОЗМОЖНОСТИ")
    rng2 = TemporalRandom()
    
    print(f"   Случайный байт: {rng2.random_byte()}")
    print(f"   Случайный float: {rng2.random_float():.10f}")
    print(f"   Случайный пароль: {rng2.random_string(12)}")
    
    fruits = ["яблоко", "банан", "вишня", "дыня", "ежевика"]
    print(f"   Случайный фрукт: {rng2.random_choice(fruits)}")
    
    numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    print(f"   Перемешанный список: {rng2.shuffle(numbers)}")
    print(f"   Выборка 3 элементов: {rng2.sample(numbers, 3)}")
    print()
    
    # Статистика
    print("СТАТИСТИКА")
    stats = rng.get_statistics()
    print(f"   Измерений: {stats['count']}")
    print(f"   T: {stats['T']:.6f} ({stats['T_percent']:.2f}%)")
    print(f"   Среднее время: {stats['mean_ns']:.2f} нс")

if __name__ == "__main__":
    main()