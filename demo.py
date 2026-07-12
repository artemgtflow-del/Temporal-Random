"""
Демонстрация работы генератора Temporal Random.

Запуск:
    python demo.py
"""

from temporal_random import TemporalRandom


def main():
    
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
    
    # 6. Перемешивание списка
    print("6. Перемешивание списка:")
    numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    shuffled = rng.shuffle(numbers)
    print(f"   Было: {numbers}")
    print(f"   Стало: {shuffled}")
    print()
    
    # 7. Случайная выборка
    print("7. Случайная выборка (3 элемента из 10):")
    sample = rng.sample(numbers, 3)
    print(f"   Выборка: {sample}")
    print()
    
    # 8. Проверка распределения (главный тест!)
    print("8. Проверка распределения (1000 чисел от 0 до 9):")
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
    
    if chi2 < 16.9:
        print("   ✅ РАСПРЕДЕЛЕНИЕ РАВНОМЕРНОЕ!")
    else:
        print("   ⚠️ Есть небольшие отклонения")
    print()
    
    # 9. Статистика генератора
    print("9. Статистика генератора:")
    stats = rng.get_statistics()
    print(f"   Измерений: {stats['count']}")
    print(f"   Среднее время: {stats['mean_ns']:.2f} нс")
    print(f"   Минимум: {stats['min_ns']} нс")
    print(f"   Максимум: {stats['max_ns']} нс")
    print(f"   Разброс: {stats['range_ns']} нс")
    print(f"   Коэффициент нестабильности T: {stats['T']:.6f}")
    print(f"   T × 100%: {stats['T_percent']:.4f}%")
    print()
    
    # 10. Контекстный менеджер
    print("10. Контекстный менеджер:")
    with TemporalRandom() as rng2:
        print(f"   Случайное число внутри контекста: {rng2.random_int(0, 100)}")
        stats2 = rng2.get_statistics()
        print(f"   Измерений внутри контекста: {stats2['count']}")
    print("   После выхода из контекста история очищена")

if __name__ == "__main__":
    main()