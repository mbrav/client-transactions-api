from datetime import datetime

from fastapi import APIRouter, Request

from client_transactions_api import __version__ as version
from client_transactions_api.config import settings

router = APIRouter()


@router.get(path='/')
async def health_check(request: Request):
    """API Health Check """

    response = {
        'status': 'OK',
        'response': 'An async client transaction system API',
        'version': version,
        'client': request.client.host,
        'time': datetime.utcnow().isoformat()
    }
    return response
