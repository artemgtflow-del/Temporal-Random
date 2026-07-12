# Temporal-Random

Генератор случайных чисел на основе временной нестабильности.

## Идея
Ни одно действие не выполняется за одинаковое время. Разница во времени между двумя одинаковыми операциями — это источник энтропии.

## Использование
```python
from temporal_random import TemporalRandom

rng = TemporalRandom()
print(rng.random_int(0, 100))