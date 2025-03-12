import time


def retry(max_attempts: int, delay: float, backoff: float):
    def decorator(func):
        def wrapper(*args, **kwargs):
            attempt = 1
            while attempt <= max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        raise e
                    sleep_time = delay * (backoff ** (attempt - 1))
                    time.sleep(sleep_time)
                    attempt += 1

        return wrapper

    return decorator
