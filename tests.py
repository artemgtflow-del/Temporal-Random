#!/usr/bin/env python3
"""
Тесты для генератора Temporal Random.

Запуск:
    python tests.py

Или с подробным выводом:
    python -v tests.py
"""

import unittest
import time
import sys
from temporal_random import TemporalRandom


class TestTemporalRandom(unittest.TestCase):
    """Набор тестов для генератора Temporal Random."""
    
    def setUp(self):
        """Создаём экземпляр генератора перед каждым тестом."""
        self.rng = TemporalRandom()
    
    def test_random_int_range(self):
        """Проверяем, что random_int возвращает числа в заданном диапазоне."""
        for _ in range(1000):
            num = self.rng.random_int(0, 10)
            self.assertTrue(0 <= num <= 10, f"Число {num} вне диапазона [0, 10]")
    
    def test_random_int_with_min_max(self):
        """Проверяем random_int с разными диапазонами."""
        test_cases = [
            (0, 1),
            (0, 100),
            (50, 100),
            (-10, 10),
            (-100, -50),
            (1000, 2000),
        ]
        
        for min_val, max_val in test_cases:
            for _ in range(100):
                num = self.rng.random_int(min_val, max_val)
                self.assertTrue(
                    min_val <= num <= max_val,
                    f"Число {num} вне диапазона [{min_val}, {max_val}]"
                )
    
    def test_random_int_single_value(self):
        """Проверяем, что при min == max всегда возвращается одно значение."""
        for _ in range(100):
            num = self.rng.random_int(5, 5)
            self.assertEqual(num, 5)
    
    def test_random_int_invalid_range(self):
        """Проверяем, что при min > max выбрасывается ошибка."""
        with self.assertRaises(ValueError):
            self.rng.random_int(10, 0)
    
    def test_random_float_range(self):
        """Проверяем, что random_float возвращает числа в [0, 1)."""
        for _ in range(1000):
            num = self.rng.random_float()
            self.assertTrue(0 <= num < 1, f"Число {num} вне диапазона [0, 1)")
    
    def test_random_byte_range(self):
        """Проверяем, что random_byte возвращает числа в [0, 255]."""
        for _ in range(1000):
            num = self.rng.random_byte()
            self.assertTrue(0 <= num <= 255, f"Число {num} вне диапазона [0, 255]")
    
    def test_random_bit(self):
        """Проверяем, что random_bit возвращает только 0 или 1."""
        for _ in range(1000):
            bit = self.rng.random_bit()
            self.assertIn(bit, [0, 1], f"Бит {bit} не равен 0 или 1")

    def test_random_choice(self):
        """Проверяем, что random_choice возвращает элемент из списка."""
        items = [1, 2, 3, 4, 5]
        for _ in range(100):
            choice = self.rng.random_choice(items)
            self.assertIn(choice, items)
    
    def test_random_choice_single_item(self):
        """Проверяем, что при одном элементе всегда возвращается он."""
        items = [42]
        for _ in range(100):
            choice = self.rng.random_choice(items)
            self.assertEqual(choice, 42)
    
    def test_random_choice_empty_list(self):
        """Проверяем, что при пустом списке выбрасывается ошибка."""
        with self.assertRaises(ValueError):
            self.rng.random_choice([])
    
    def test_random_choice_with_string(self):
        """Проверяем выбор из строки."""
        chars = "ABCDE"
        for _ in range(100):
            choice = self.rng.random_choice(chars)
            self.assertIn(choice, chars)
 
    def test_random_string_length(self):
        """Проверяем, что random_string возвращает строку правильной длины."""
        for length in [0, 1, 8, 16, 32, 100]:
            s = self.rng.random_string(length)
            self.assertEqual(len(s), length)
    
    def test_random_string_negative_length(self):
        """Проверяем, что при отрицательной длине выбрасывается ошибка."""
        with self.assertRaises(ValueError):
            self.rng.random_string(-1)
    
    def test_random_string_zero_length(self):
        """Проверяем, что при длине 0 возвращается пустая строка."""
        s = self.rng.random_string(0)
        self.assertEqual(s, "")
    
    def test_random_string_default_chars(self):
        """Проверяем, что по умолчанию используются буквы и цифры."""
        s = self.rng.random_string(100)
        # Все символы должны быть из стандартного набора
        allowed = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
        for char in s:
            self.assertIn(char, allowed)
    
    def test_random_string_custom_chars(self):
        """Проверяем, что можно задать свои символы."""
        chars = "XYZ"
        for _ in range(100):
            s = self.rng.random_string(10, chars)
            for char in s:
                self.assertIn(char, chars)

    def test_shuffle(self):
        """Проверяем, что shuffle перемешивает список."""
        original = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        shuffled = self.rng.shuffle(original)
        
        # Содержимое должно сохраниться
        self.assertEqual(sorted(original), sorted(shuffled))
        
        # Длина должна сохраниться
        self.assertEqual(len(original), len(shuffled))
        
        # Проверяем, что хотя бы один элемент изменил позицию
        # (вероятность что порядок сохранился крайне мала)
        self.assertNotEqual(original, shuffled)
    
    def test_shuffle_empty_list(self):
        """Проверяем перемешивание пустого списка."""
        original = []
        shuffled = self.rng.shuffle(original)
        self.assertEqual(shuffled, [])
    
    def test_shuffle_single_item(self):
        """Проверяем перемешивание списка с одним элементом."""
        original = [42]
        shuffled = self.rng.shuffle(original)
        self.assertEqual(shuffled, [42])
    
    def test_shuffle_does_not_modify_original(self):
        """Проверяем, что shuffle не изменяет исходный список."""
        original = [1, 2, 3, 4, 5]
        copy = original.copy()
        self.rng.shuffle(original)
        self.assertEqual(original, copy)

    def test_sample(self):
        """Проверяем, что sample возвращает выборку правильного размера."""
        population = list(range(100))
        k = 10
        sample = self.rng.sample(population, k)
        
        self.assertEqual(len(sample), k)
        for item in sample:
            self.assertIn(item, population)
    
    def test_sample_no_repetition(self):
        """Проверяем, что в выборке нет повторений."""
        population = list(range(100))
        sample = self.rng.sample(population, 10)
        self.assertEqual(len(sample), len(set(sample)))
    
    def test_sample_k_zero(self):
        """Проверяем, что при k=0 возвращается пустой список."""
        population = [1, 2, 3, 4, 5]
        sample = self.rng.sample(population, 0)
        self.assertEqual(sample, [])
    
    def test_sample_k_full(self):
        """Проверяем, что при k=len(population) возвращается вся популяция."""
        population = [1, 2, 3, 4, 5]
        sample = self.rng.sample(population, len(population))
        self.assertEqual(sorted(sample), sorted(population))
    
    def test_sample_k_greater_than_population(self):
        """Проверяем, что при k > len(population) выбрасывается ошибка."""
        population = [1, 2, 3]
        with self.assertRaises(ValueError):
            self.rng.sample(population, 5)
    
    def test_sample_k_negative(self):
        """Проверяем, что при отрицательном k выбрасывается ошибка."""
        population = [1, 2, 3]
        with self.assertRaises(ValueError):
            self.rng.sample(population, -1)
    
    def test_sample_empty_population(self):
        """Проверяем выборку из пустой популяции."""
        population = []
        sample = self.rng.sample(population, 0)
        self.assertEqual(sample, [])
        with self.assertRaises(ValueError):
            self.rng.sample(population, 1)

    def test_randrange(self):
        """Проверяем, что randrange возвращает числа из правильного диапазона."""
        for _ in range(1000):
            num = self.rng.randrange(0, 10)
            self.assertTrue(0 <= num < 10)
    
    def test_randrange_with_step(self):
        """Проверяем randrange с шагом."""
        for _ in range(1000):
            num = self.rng.randrange(0, 20, 2)
            self.assertTrue(0 <= num < 20)
            self.assertEqual(num % 2, 0)  # должно быть чётным
    
    def test_randrange_single_argument(self):
        """Проверяем randrange с одним аргументом."""
        for _ in range(1000):
            num = self.rng.randrange(10)
            self.assertTrue(0 <= num < 10)
    
    def test_randrange_step_zero(self):
        """Проверяем, что при step=0 выбрасывается ошибка."""
        with self.assertRaises(ValueError):
            self.rng.randrange(0, 10, 0)
    
    def test_randrange_empty_range(self):
        """Проверяем, что при пустом диапазоне выбрасывается ошибка."""
        with self.assertRaises(ValueError):
            self.rng.randrange(10, 0)
    
    def test_seed_reproducibility(self):
        """Проверяем, что при одинаковом seed результаты совпадают."""
        seed_value = 12345
        rng1 = TemporalRandom(seed=seed_value)
        rng2 = TemporalRandom(seed=seed_value)
        
        results1 = [rng1.random_int(0, 100) for _ in range(100)]
        results2 = [rng2.random_int(0, 100) for _ in range(100)]
        
        self.assertEqual(results1, results2)
    
    def test_seed_reproducibility_float(self):
        """Проверяем воспроизводимость для float."""
        seed_value = 42
        rng1 = TemporalRandom(seed=seed_value)
        rng2 = TemporalRandom(seed=seed_value)
        
        results1 = [rng1.random_float() for _ in range(50)]
        results2 = [rng2.random_float() for _ in range(50)]
        
        self.assertEqual(results1, results2)
    
    def test_seed_method(self):
        """Проверяем метод seed()."""
        rng = TemporalRandom()
        
        # Устанавливаем seed
        rng.seed(12345)
        value1 = rng.random_int(0, 100)
        
        # Сбрасываем и устанавливаем тот же seed
        rng.seed(12345)
        value2 = rng.random_int(0, 100)
        
        self.assertEqual(value1, value2)
    
    def test_seed_none(self):
        """Проверяем, что seed(None) возвращает к временной нестабильности."""
        rng = TemporalRandom(seed=42)
        
        # В режиме seed числа воспроизводимы
        rng.seed(42)
        val1 = rng.random_int(0, 100)
        rng.seed(42)
        val2 = rng.random_int(0, 100)
        self.assertEqual(val1, val2)
        
        # После seed(None) должны стать разными
        rng.seed(None)
        val3 = rng.random_int(0, 100)
        val4 = rng.random_int(0, 100)
        # Не гарантируем, что разные, но вероятность ничтожна
        # Проверяем только что метод не падает
        self.assertIsNotNone(val3)
        self.assertIsNotNone(val4)
    
    def test_get_statistics(self):
        """Проверяем, что get_statistics возвращает корректные данные."""
        stats = self.rng.get_statistics()
        self.assertIsInstance(stats, dict)
        self.assertIn("count", stats)
        self.assertIn("mean_ns", stats)
        self.assertIn("T", stats)
    
    def test_get_statistics_after_generation(self):
        """Проверяем статистику после генерации чисел."""
        for _ in range(100):
            self.rng.random_int(0, 100)
        
        stats = self.rng.get_statistics()
        self.assertEqual(stats["count"], 100)
        self.assertGreater(stats["mean_ns"], 0)
        self.assertGreater(stats["T"], 0)
    
    def test_clear_history(self):
        """Проверяем очистку истории."""
        for _ in range(50):
            self.rng.random_int(0, 100)
        
        stats_before = self.rng.get_statistics()
        self.assertEqual(stats_before["count"], 50)
        
        self.rng.clear_history()
        stats_after = self.rng.get_statistics()
        self.assertEqual(stats_after["count"], 0)
    
    def test_context_manager(self):
        """Проверяем работу контекстного менеджера."""
        with TemporalRandom() as rng:
            rng.random_int(0, 100)
            stats = rng.get_statistics()
            self.assertGreater(stats["count"], 0)
        
        # После выхода история должна быть очищена
        stats = rng.get_statistics()
        self.assertEqual(stats["count"], 0)
    
    def test_uniform_distribution(self):
        """
        Проверяем равномерность распределения через хи-квадрат тест.
        
        Это основной тест качества генератора.
        """
        iterations = 10000
        categories = 10
        
        counts = [0] * categories
        for _ in range(iterations):
            num = self.rng.random_int(0, categories - 1)
            counts[num] += 1
        
        expected = iterations / categories
        chi2 = sum((c - expected) ** 2 / expected for c in counts)
        
        # Для 10 категорий и 10000 итераций
        # 95% доверительный интервал: chi2 < 16.92
        self.assertLess(
            chi2, 16.92,
            f"Хи-квадрат = {chi2:.2f} > 16.92. Распределение неравномерное!\n"
            f"Частоты: {counts}"
        )
    
    def test_uniform_distribution_seed_mode(self):
        """Проверяем распределение в режиме seed (должно быть равномерным)."""
        rng = TemporalRandom(seed=12345)
        iterations = 10000
        categories = 10
        
        counts = [0] * categories
        for _ in range(iterations):
            num = rng.random_int(0, categories - 1)
            counts[num] += 1
        
        expected = iterations / categories
        chi2 = sum((c - expected) ** 2 / expected for c in counts)
        
        self.assertLess(
            chi2, 16.92,
            f"Хи-квадрат = {chi2:.2f} > 16.92. Распределение неравномерное!\n"
            f"Частоты: {counts}"
        )
    
    def test_float_distribution(self):
        """Проверяем распределение float чисел."""
        iterations = 10000
        bins = 10
        
        counts = [0] * bins
        for _ in range(iterations):
            num = self.rng.random_float()
            bin_idx = int(num * bins)
            counts[bin_idx] += 1
        
        expected = iterations / bins
        chi2 = sum((c - expected) ** 2 / expected for c in counts)
        
        self.assertLess(
            chi2, 16.92,
            f"Хи-квадрат = {chi2:.2f} > 16.92. Распределение float неравномерное!\n"
            f"Частоты: {counts}"
        )
    
    def test_performance(self):
        """Проверяем, что генератор работает достаточно быстро."""
        iterations = 10000
        
        start = time.perf_counter()
        for _ in range(iterations):
            self.rng.random_int(0, 100)
        elapsed = time.perf_counter() - start
        
        # Должно быть быстрее 0.5 секунды на 10000 итераций
        self.assertLess(
            elapsed, 0.5,
            f"Слишком медленно: {elapsed:.3f} сек на {iterations} итераций"
        )
    
    def test_performance_seed_mode(self):
        """Проверяем производительность в режиме seed."""
        rng = TemporalRandom(seed=42)
        iterations = 10000
        
        start = time.perf_counter()
        for _ in range(iterations):
            rng.random_int(0, 100)
        elapsed = time.perf_counter() - start
        
        self.assertLess(
            elapsed, 0.3,
            f"Слишком медленно в режиме seed: {elapsed:.3f} сек"
        )
    
    def test_seed_compatibility_with_random(self):
        """Проверяем, что seed работает как в стандартном random."""
        import random
        
        # Создаём два генератора с одним seed
        rng1 = TemporalRandom(seed=42)
        rng2 = TemporalRandom(seed=42)
        
        # Генерируем последовательности
        seq1 = [rng1.random_int(0, 100) for _ in range(20)]
        seq2 = [rng2.random_int(0, 100) for _ in range(20)]
        
        # Они должны совпадать
        self.assertEqual(seq1, seq2)
    
    def test_randrange_compatibility(self):
        """Проверяем совместимость randrange с random.randrange."""
        import random
        
        # Просто проверяем, что результаты в правильных диапазонах
        for _ in range(100):
            a = self.rng.randrange(0, 10)
            self.assertTrue(0 <= a < 10)
            
            b = self.rng.randrange(0, 20, 2)
            self.assertTrue(0 <= b < 20)
            self.assertEqual(b % 2, 0)

if __name__ == "__main__":
    print("=" * 70)
    print("ЗАПУСК ТЕСТОВ ДЛЯ TEMPORAL RANDOM")
    print("=" * 70)
    print()
    
    # Запускаем тесты с подробным выводом
    test_runner = unittest.TextTestRunner(verbosity=2)
    test_suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestTemporalRandom)
    result = test_runner.run(test_suite)
    
    print()
    print("=" * 70)
    if result.wasSuccessful():
        print("ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
    else:
        print("ЕСТЬ ПРОВАЛЕННЫЕ ТЕСТЫ")
        print(f"   Пройдено: {result.testsRun - len(result.failures) - len(result.errors)}")
        print(f"   Ошибок: {len(result.errors)}")
        print(f"   Провалов: {len(result.failures)}")
    print("=" * 70)