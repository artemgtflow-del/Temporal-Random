#!/usr/bin/env python3
"""
Тесты для генератора Temporal Random.

Запуск:
    python tests.py
    python -v tests.py
"""

import unittest
import time
import sys
import datetime
import asyncio
import math
from temporal_random import TemporalRandom


class TestTemporalRandom(unittest.TestCase):
    """Набор тестов для генератора Temporal Random."""
    
    def setUp(self):
        self.rng = TemporalRandom()
    
    def test_random_int_range(self):
        for _ in range(1000):
            num = self.rng.random_int(0, 10)
            self.assertTrue(0 <= num <= 10)
    
    def test_random_int_with_min_max(self):
        test_cases = [(0, 1), (0, 100), (50, 100), (-10, 10), (-100, -50), (1000, 2000)]
        for min_val, max_val in test_cases:
            for _ in range(100):
                num = self.rng.random_int(min_val, max_val)
                self.assertTrue(min_val <= num <= max_val)
    
    def test_random_int_single_value(self):
        for _ in range(100):
            self.assertEqual(self.rng.random_int(5, 5), 5)
    
    def test_random_int_invalid_range(self):
        with self.assertRaises(ValueError):
            self.rng.random_int(10, 0)
    
    def test_random_float_range(self):
        for _ in range(1000):
            num = self.rng.random_float()
            self.assertTrue(0 <= num < 1)
    
    def test_random_byte_range(self):
        for _ in range(1000):
            num = self.rng.random_byte()
            self.assertTrue(0 <= num <= 255)
    
    def test_random_bit(self):
        for _ in range(1000):
            bit = self.rng.random_bit()
            self.assertIn(bit, [0, 1])
    
    def test_random_choice(self):
        items = [1, 2, 3, 4, 5]
        for _ in range(100):
            choice = self.rng.random_choice(items)
            self.assertIn(choice, items)
    
    def test_random_choice_single_item(self):
        items = [42]
        for _ in range(100):
            self.assertEqual(self.rng.random_choice(items), 42)
    
    def test_random_choice_empty_list(self):
        with self.assertRaises(ValueError):
            self.rng.random_choice([])
    
    def test_random_choice_with_string(self):
        chars = "ABCDE"
        for _ in range(100):
            choice = self.rng.random_choice(chars)
            self.assertIn(choice, chars)
    
    def test_random_string_length(self):
        for length in [0, 1, 8, 16, 32, 100]:
            s = self.rng.random_string(length)
            self.assertEqual(len(s), length)
    
    def test_random_string_negative_length(self):
        with self.assertRaises(ValueError):
            self.rng.random_string(-1)
    
    def test_random_string_zero_length(self):
        self.assertEqual(self.rng.random_string(0), "")
    
    def test_random_string_default_chars(self):
        s = self.rng.random_string(100)
        allowed = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
        for char in s:
            self.assertIn(char, allowed)
    
    def test_random_string_custom_chars(self):
        chars = "XYZ"
        for _ in range(100):
            s = self.rng.random_string(10, chars)
            for char in s:
                self.assertIn(char, chars)
    
    def test_shuffle(self):
        original = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        shuffled = self.rng.shuffle(original)
        self.assertEqual(sorted(original), sorted(shuffled))
        self.assertEqual(len(original), len(shuffled))
        self.assertNotEqual(original, shuffled)
    
    def test_shuffle_empty_list(self):
        original = []
        shuffled = self.rng.shuffle(original)
        self.assertEqual(shuffled, [])
    
    def test_shuffle_single_item(self):
        original = [42]
        shuffled = self.rng.shuffle(original)
        self.assertEqual(shuffled, [42])
    
    def test_shuffle_does_not_modify_original(self):
        original = [1, 2, 3, 4, 5]
        copy = original.copy()
        self.rng.shuffle(original)
        self.assertEqual(original, copy)
    
    def test_sample(self):
        population = list(range(100))
        k = 10
        sample = self.rng.sample(population, k)
        self.assertEqual(len(sample), k)
        for item in sample:
            self.assertIn(item, population)
    
    def test_sample_no_repetition(self):
        population = list(range(100))
        sample = self.rng.sample(population, 10)
        self.assertEqual(len(sample), len(set(sample)))
    
    def test_sample_k_zero(self):
        population = [1, 2, 3, 4, 5]
        sample = self.rng.sample(population, 0)
        self.assertEqual(sample, [])
    
    def test_sample_k_full(self):
        population = [1, 2, 3, 4, 5]
        sample = self.rng.sample(population, len(population))
        self.assertEqual(sorted(sample), sorted(population))
    
    def test_sample_k_greater_than_population(self):
        population = [1, 2, 3]
        with self.assertRaises(ValueError):
            self.rng.sample(population, 5)
    
    def test_sample_k_negative(self):
        population = [1, 2, 3]
        with self.assertRaises(ValueError):
            self.rng.sample(population, -1)
    
    def test_sample_empty_population(self):
        population = []
        sample = self.rng.sample(population, 0)
        self.assertEqual(sample, [])
        with self.assertRaises(ValueError):
            self.rng.sample(population, 1)
    
    def test_randrange(self):
        for _ in range(1000):
            num = self.rng.randrange(0, 10)
            self.assertTrue(0 <= num < 10)
    
    def test_randrange_with_step(self):
        for _ in range(1000):
            num = self.rng.randrange(0, 20, 2)
            self.assertTrue(0 <= num < 20)
            self.assertEqual(num % 2, 0)
    
    def test_randrange_single_argument(self):
        for _ in range(1000):
            num = self.rng.randrange(10)
            self.assertTrue(0 <= num < 10)
    
    def test_randrange_step_zero(self):
        with self.assertRaises(ValueError):
            self.rng.randrange(0, 10, 0)
    
    def test_randrange_empty_range(self):
        with self.assertRaises(ValueError):
            self.rng.randrange(10, 0)
    
    def test_seed_reproducibility(self):
        seed_value = 12345
        rng1 = TemporalRandom(seed=seed_value)
        rng2 = TemporalRandom(seed=seed_value)
        results1 = [rng1.random_int(0, 100) for _ in range(100)]
        results2 = [rng2.random_int(0, 100) for _ in range(100)]
        self.assertEqual(results1, results2)
    
    def test_seed_reproducibility_float(self):
        seed_value = 42
        rng1 = TemporalRandom(seed=seed_value)
        rng2 = TemporalRandom(seed=seed_value)
        results1 = [rng1.random_float() for _ in range(50)]
        results2 = [rng2.random_float() for _ in range(50)]
        self.assertEqual(results1, results2)
    
    def test_seed_method(self):
        rng = TemporalRandom()
        rng.seed(12345)
        value1 = rng.random_int(0, 100)
        rng.seed(12345)
        value2 = rng.random_int(0, 100)
        self.assertEqual(value1, value2)
    
    def test_seed_none(self):
        rng = TemporalRandom(seed=42)
        rng.seed(42)
        val1 = rng.random_int(0, 100)
        rng.seed(42)
        val2 = rng.random_int(0, 100)
        self.assertEqual(val1, val2)
        rng.seed(None)
        val3 = rng.random_int(0, 100)
        val4 = rng.random_int(0, 100)
        self.assertIsNotNone(val3)
        self.assertIsNotNone(val4)
    
    def test_get_statistics(self):
        stats = self.rng.get_statistics()
        self.assertIsInstance(stats, dict)
        self.assertIn("count", stats)
        self.assertIn("mean_ns", stats)
        self.assertIn("T", stats)
    
    def test_get_statistics_after_generation(self):
        for _ in range(100):
            self.rng.random_int(0, 100)
        stats = self.rng.get_statistics()
        self.assertEqual(stats["count"], 100)
        self.assertGreater(stats["mean_ns"], 0)
        self.assertGreater(stats["T"], 0)
    
    def test_clear_history(self):
        for _ in range(50):
            self.rng.random_int(0, 100)
        stats_before = self.rng.get_statistics()
        self.assertEqual(stats_before["count"], 50)
        self.rng.clear_history()
        stats_after = self.rng.get_statistics()
        self.assertEqual(stats_after["count"], 0)
    
    def test_context_manager(self):
        with TemporalRandom() as rng:
            rng.random_int(0, 100)
            stats = rng.get_statistics()
            self.assertGreater(stats["count"], 0)
        stats = rng.get_statistics()
        self.assertEqual(stats["count"], 0)
    
    def test_uniform_distribution(self):
        iterations = 10000
        categories = 10
        counts = [0] * categories
        for _ in range(iterations):
            num = self.rng.random_int(0, categories - 1)
            counts[num] += 1
        expected = iterations / categories
        chi2 = sum((c - expected) ** 2 / expected for c in counts)
        self.assertLess(chi2, 16.92, f"Хи-квадрат = {chi2:.2f} > 16.92")
    
    def test_uniform_distribution_seed_mode(self):
        rng = TemporalRandom(seed=12345)
        iterations = 10000
        categories = 10
        counts = [0] * categories
        for _ in range(iterations):
            num = rng.random_int(0, categories - 1)
            counts[num] += 1
        expected = iterations / categories
        chi2 = sum((c - expected) ** 2 / expected for c in counts)
        self.assertLess(chi2, 16.92, f"Хи-квадрат = {chi2:.2f} > 16.92")
    
    def test_float_distribution(self):
        iterations = 10000
        bins = 10
        counts = [0] * bins
        for _ in range(iterations):
            num = self.rng.random_float()
            bin_idx = int(num * bins)
            if bin_idx >= bins:
                bin_idx = bins - 1
            counts[bin_idx] += 1
        expected = iterations / bins
        chi2 = sum((c - expected) ** 2 / expected for c in counts)
        self.assertLess(chi2, 18.31, f"Хи-квадрат = {chi2:.2f} > 18.31")
    
    def test_performance(self):
        iterations = 10000
        start = time.perf_counter()
        for _ in range(iterations):
            self.rng.random_int(0, 100)
        elapsed = time.perf_counter() - start
        self.assertLess(elapsed, 0.5, f"Слишком медленно: {elapsed:.3f} сек")
    
    def test_performance_seed_mode(self):
        rng = TemporalRandom(seed=42)
        iterations = 10000
        start = time.perf_counter()
        for _ in range(iterations):
            rng.random_int(0, 100)
        elapsed = time.perf_counter() - start
        self.assertLess(elapsed, 0.3, f"Слишком медленно: {elapsed:.3f} сек")
    
    def test_seed_compatibility_with_random(self):
        import random
        rng1 = TemporalRandom(seed=42)
        rng2 = TemporalRandom(seed=42)
        seq1 = [rng1.random_int(0, 100) for _ in range(20)]
        seq2 = [rng2.random_int(0, 100) for _ in range(20)]
        self.assertEqual(seq1, seq2)
    
    def test_randrange_compatibility(self):
        import random
        for _ in range(100):
            a = self.rng.randrange(0, 10)
            self.assertTrue(0 <= a < 10)
            b = self.rng.randrange(0, 20, 2)
            self.assertTrue(0 <= b < 20)
            self.assertEqual(b % 2, 0)
    
    def test_random_date(self):
        date1 = self.rng.random_date()
        date2 = self.rng.random_date()
        self.assertIsInstance(date1, datetime.date)
        self.assertIsInstance(date2, datetime.date)
        today = datetime.date.today()
        self.assertTrue(date1 <= today)
        self.assertTrue(date2 <= today)
        start = datetime.date(2020, 1, 1)
        end = datetime.date(2025, 12, 31)
        date3 = self.rng.random_date(start, end)
        self.assertTrue(start <= date3 <= end)
    
    def test_random_datetime(self):
        dt1 = self.rng.random_datetime()
        dt2 = self.rng.random_datetime()
        self.assertIsInstance(dt1, datetime.datetime)
        self.assertIsInstance(dt2, datetime.datetime)
        now = datetime.datetime.now()
        self.assertTrue(dt1 <= now)
        self.assertTrue(dt2 <= now)
        start = datetime.datetime(2020, 1, 1)
        end = datetime.datetime(2025, 12, 31)
        dt3 = self.rng.random_datetime(start, end)
        self.assertTrue(start <= dt3 <= end)
    
    def test_random_time_12h(self):
        for _ in range(100):
            time_str = self.rng.random_time_12h()
            self.assertTrue("AM" in time_str or "PM" in time_str)
            parts = time_str.replace(" AM", "").replace(" PM", "").split(":")
            self.assertEqual(len(parts), 3)
            hour = int(parts[0])
            minute = int(parts[1])
            second = int(parts[2])
            self.assertTrue(1 <= hour <= 12)
            self.assertTrue(0 <= minute <= 59)
            self.assertTrue(0 <= second <= 59)
    
    def test_random_time_24h(self):
        for _ in range(100):
            time_str = self.rng.random_time_24h()
            parts = time_str.split(":")
            self.assertEqual(len(parts), 3)
            hour = int(parts[0])
            minute = int(parts[1])
            second = int(parts[2])
            self.assertTrue(0 <= hour <= 23)
            self.assertTrue(0 <= minute <= 59)
            self.assertTrue(0 <= second <= 59)
    
    def test_random_timestamp_id(self):
        for _ in range(100):
            id_str = self.rng.random_timestamp_id()
            parts = id_str.split("-")
            self.assertEqual(len(parts), 2)
            timestamp = int(parts[0])
            random_part = parts[1]
            self.assertEqual(len(random_part), 8)
            self.assertTrue(all(c in "0123456789abcdef" for c in random_part))
            self.assertGreater(timestamp, 0)
    
    def test_random_short_id(self):
        for length in [4, 8, 12, 16]:
            id_str = self.rng.random_short_id(length)
            self.assertEqual(len(id_str), length)
            allowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
            for char in id_str:
                self.assertIn(char, allowed)
    
    def test_random_lat_lng(self):
        for _ in range(100):
            lat, lng = self.rng.random_lat_lng()
            self.assertTrue(-90 <= lat <= 90)
            self.assertTrue(-180 <= lng <= 180)
    
    def test_random_point_in_circle(self):
        cx, cy, radius = 0, 0, 10
        for _ in range(100):
            x, y = self.rng.random_point_in_circle(cx, cy, radius)
            distance = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
            self.assertLessEqual(distance, radius)
    
    def test_random_point_in_rect(self):
        x1, y1, x2, y2 = 0, 0, 100, 100
        for _ in range(100):
            x, y = self.rng.random_point_in_rect(x1, y1, x2, y2)
            self.assertTrue(0 <= x <= 100)
            self.assertTrue(0 <= y <= 100)
    
    def test_random_hex_color(self):
        for _ in range(100):
            color = self.rng.random_hex_color()
            self.assertEqual(len(color), 7)
            self.assertEqual(color[0], "#")
            self.assertTrue(all(c in "0123456789abcdef" for c in color[1:]))
    
    def test_random_hex_color_without_hash(self):
        for _ in range(100):
            color = self.rng.random_hex_color(with_hash=False)
            self.assertEqual(len(color), 6)
            self.assertTrue(all(c in "0123456789abcdef" for c in color))
    
    def test_random_rgb_color(self):
        for _ in range(100):
            r, g, b = self.rng.random_rgb_color()
            self.assertTrue(0 <= r <= 255)
            self.assertTrue(0 <= g <= 255)
            self.assertTrue(0 <= b <= 255)
    
    def test_random_rgb_color_str(self):
        for _ in range(100):
            color_str = self.rng.random_rgb_color_str()
            self.assertTrue(color_str.startswith("rgb("))
            self.assertTrue(color_str.endswith(")"))
            parts = color_str[4:-1].split(",")
            self.assertEqual(len(parts), 3)
            for part in parts:
                num = int(part.strip())
                self.assertTrue(0 <= num <= 255)
    
    def test_random_hsl_color(self):
        for _ in range(100):
            h, s, l = self.rng.random_hsl_color()
            self.assertTrue(0 <= h <= 360)
            self.assertTrue(0 <= s <= 100)
            self.assertTrue(0 <= l <= 100)
    
    def test_random_hsl_color_str(self):
        for _ in range(100):
            color_str = self.rng.random_hsl_color_str()
            self.assertTrue(color_str.startswith("hsl("))
            self.assertTrue(color_str.endswith(")"))
            parts = color_str[4:-1].replace("%", "").split(",")
            self.assertEqual(len(parts), 3)
            h = float(parts[0].strip())
            s = float(parts[1].strip())
            l = float(parts[2].strip())
            self.assertTrue(0 <= h <= 360)
            self.assertTrue(0 <= s <= 100)
            self.assertTrue(0 <= l <= 100)
    
    def test_random_color_name(self):
        colors = [
            "red", "blue", "green", "yellow", "orange", "purple",
            "pink", "brown", "black", "white", "gray", "cyan",
            "magenta", "lime", "teal", "navy", "olive", "maroon",
            "coral", "indigo", "violet", "gold", "silver", "bronze"
        ]
        for _ in range(100):
            color = self.rng.random_color_name()
            self.assertIn(color, colors)
    
    def test_random_mnemonic(self):
        for _ in range(100):
            password = self.rng.random_mnemonic(4)
            parts = password.split("-")
            self.assertEqual(len(parts), 4)
            for word in parts:
                self.assertIsInstance(word, str)
                self.assertGreater(len(word), 0)
    
    def test_random_mnemonic_with_number(self):
        for _ in range(100):
            password = self.rng.random_mnemonic_with_number(3)
            parts = password.split("-")
            self.assertEqual(len(parts), 4)
            for word in parts[:-1]:
                self.assertIsInstance(word, str)
                self.assertGreater(len(word), 0)
            number = int(parts[-1])
            self.assertTrue(10 <= number <= 999)
    
    def test_random_mnemonic_custom_separator(self):
        for _ in range(100):
            password = self.rng.random_mnemonic(4, "_")
            parts = password.split("_")
            self.assertEqual(len(parts), 4)
    
    def test_random_mnemonic_zero_words(self):
        with self.assertRaises(ValueError):
            self.rng.random_mnemonic(0)
    
    def test_async_random_int(self):
        async def test():
            result = await self.rng.random_int_async(0, 100)
            self.assertTrue(0 <= result <= 100)
        asyncio.run(test())
    
    def test_async_random_float(self):
        async def test():
            result = await self.rng.random_float_async()
            self.assertTrue(0 <= result < 1)
        asyncio.run(test())
    
    def test_async_random_byte(self):
        async def test():
            result = await self.rng.random_byte_async()
            self.assertTrue(0 <= result <= 255)
        asyncio.run(test())
    
    def test_async_random_string(self):
        async def test():
            result = await self.rng.random_string_async(10)
            self.assertEqual(len(result), 10)
        asyncio.run(test())
    
    def test_async_generate_batch(self):
        async def test():
            results = await self.rng.generate_batch(50, 0, 10)
            self.assertEqual(len(results), 50)
            for num in results:
                self.assertTrue(0 <= num <= 10)
        asyncio.run(test())
    
    def test_random_time_12h_format(self):
        for _ in range(100):
            time_str = self.rng.random_time_12h()
            self.assertRegex(time_str, r'^\d{2}:\d{2}:\d{2} (AM|PM)$')
    
    def test_random_time_24h_format(self):
        for _ in range(100):
            time_str = self.rng.random_time_24h()
            self.assertRegex(time_str, r'^\d{2}:\d{2}:\d{2}$')


if __name__ == "__main__":
    verbosity = 2 if "-v" in sys.argv else 1
    test_runner = unittest.TextTestRunner(verbosity=verbosity)
    test_suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestTemporalRandom)
    result = test_runner.run(test_suite)
    
    if result.wasSuccessful():
        print(f"\nВсе {result.testsRun} тестов пройдены успешно!")
    else:
        print(f"\nПройдено: {result.testsRun - len(result.failures) - len(result.errors)}")
        print(f"   Ошибок: {len(result.errors)}")
        print(f"   Провалов: {len(result.failures)}")