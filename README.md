[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.3.3-brightgreen.svg)](https://github.com/artemgtflow-del/temporal-random/releases)

# Temporal-Random

Генератор случайных чисел на основе временной нестабильности.

## Идея
Ни одно действие не выполняется за одинаковое время. Разница во времени между двумя одинаковыми операциями — это источник энтропии.

## Использование
```python
from temporal_random import TemporalRandom

rng = TemporalRandom()
print(rng.random_int(0, 100))

```
EN

# Temporal-Random

Random number generator based on temporal instability.

## Idea
No action is performed in exactly the same time. The difference in time between two identical operations is a source of entropy.

## Usage
```python
from temporal_random import TemporalRandom

rng = TemporalRandom()
print(rng.random_int(0, 100))