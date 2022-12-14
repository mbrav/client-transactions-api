import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class ProcessTimeMiddleware(BaseHTTPMiddleware):
    """Add request process time to response headers with logger
    
    Create Warning log if request was slow
    """

    slow_warning = 0.2

    async def dispatch(self, request, call_next):
        start_time = time.time()

        response = await call_next(request)

        process_time = time.time() - start_time
        response.headers['X-Process-Time'] = f'{process_time:.5f}'

        log_message = f'Request "{request.url.path}" {response.status_code}' \
            f'client {request.client.host} port {request.client.port} ' \
            f'time {process_time:.5f}s'

        slow_warning = process_time > self.slow_warning
        if response.status_code < 203 and not slow_warning:
            logger.info(log_message)
        elif response.status_code < 500 or slow_warning:
            logger.warning(log_message)
        else:
            logger.error(log_message)

        return response
