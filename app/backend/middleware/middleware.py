import time

class TimingMiddleware:
    '''Промежуточное обеспечение для замеров скорости запросов'''
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        start_time = time.time()
        await self.app(scope, receive, send)
        duration = time.time() - start_time
        print(f'Длительность запроса составила: {duration:.10f} сек.')