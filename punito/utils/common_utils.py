import time
from loguru import logger
from functools import wraps

def measure_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start

        hours = int(elapsed // 3600)
        minutes = int((elapsed % 3600) // 60)
        seconds = elapsed % 60

        parts = []
        if hours > 0:
            parts.append(f"{hours} h")
        if minutes > 0:
            parts.append(f"{minutes} min")
        parts.append(f"{seconds:.3f} sec")

        formatted = " ".join(parts)
        logger.info(f"{func.__qualname__} executed in {formatted}")
        return result
    return wrapper
