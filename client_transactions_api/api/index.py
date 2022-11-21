from datetime import datetime

from fastapi import APIRouter, Request

from client_transactions_api.config import settings

router = APIRouter()


@router.get(path='/')
async def health_check(request: Request, message: str = None):
    """API Health Check """

    response = {
        'status': 'OK',
        'response': 'An async client transaction system API',
        'version': settings.VERSION,
        'client': request.client.host,
        'time': datetime.utcnow().isoformat()
    }
    return response
