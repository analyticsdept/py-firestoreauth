import random
from time import sleep

class ExponentialRetry():
    def __init__(self, max_retries):
        self.max_retries = max_retries if (type(max_retries) == int) else 1

    def exponential_retry_with_return(self, func, *args, **kwargs):
        def retry(func, *args, **kwargs):
            success = False
            max_retries = self.max_retries
            retry_count = 0

            while not success:
                try:
                    output = func(*args, **kwargs)
                except Exception as e:
                    retry_count += 1
                    if retry_count == max_retries:
                        raise Exception(f"maximum retries reached >> {str(e)}")
                    else:
                        sleep((2 ** retry_count) + (random.randint(0, 1000) / 1000))
                else:
                    success = True
                    return output
        return retry(func, *args, **kwargs)