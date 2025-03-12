import asyncio
from functools import wraps
from collections import OrderedDict

def async_lru_cache(maxsize=128):
    """
    An asynchronous LRU (Least Recently Used) cache decorator for caching the results of async functions.

    Args:
        maxsize (int): Maximum number of items to store in the cache. Defaults to 128.

    Returns:
        Decorator for asynchronous functions.
    """
    def decorator(func):
        cache = OrderedDict()
        lock = asyncio.Lock()

        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Create a cache key based on the function's arguments
            key = args + tuple(sorted(kwargs.items()))
            created_future = False
            async with lock:
                if key in cache:
                    # Cache hit: Retrieve the future and update the usage order
                    future = cache[key]
                    cache.move_to_end(key)
                else:
                    # Cache miss: Create a new future and insert it into the cache
                    future = asyncio.get_event_loop().create_future()
                    cache[key] = future
                    cache.move_to_end(key)
                    # Enforce the cache size limit
                    if len(cache) > maxsize:
                        cache.popitem(last=False)
                    created_future = True  # We are responsible for computing the result
            if not created_future:
                # Wait for the result computed by another coroutine
                return await future
            else:
                try:
                    # Compute the result and set it on the future
                    result = await func(*args, **kwargs)
                    future.set_result(result)
                except Exception as exc:
                    # Set the exception on the future and remove the cache entry
                    future.set_exception(exc)
                    async with lock:
                        del cache[key]
                    raise
                return result
        return wrapper
    return decorator

# Example usage:
@async_lru_cache(maxsize=3)
async def expensive_computation(x):
    print(f"Computing {x}...")
    await asyncio.sleep(1)  # Simulate an expensive operation
    return x * x

# Test the async LRU cache
async def main():
    print(await expensive_computation(2))  # Computes and caches
    print(await expensive_computation(3))  # Computes and caches
    print(await expensive_computation(2))  # Retrieves from cache
    print(await expensive_computation(4))  # Computes and caches, may evict oldest entry
    print(await expensive_computation(5))  # Computes and caches, may evict oldest entry
    print(await expensive_computation(3))  # May or may not be cached based on cache size

if __name__ == "__main__":
    asyncio.run(main())
