from uuid import uuid4
from fastapi import Request
from fastapi.responses import JSONResponse
from loguru import logger
from app.backend.config import LOG_CONF, LOG_DIR


logger.add(
        LOG_DIR / "info.log",
        level="INFO",
        **LOG_CONF,
    )

logger.add(
        LOG_DIR / "warning.log",
        level="WARNING",
        **LOG_CONF,
    )

logger.add(
    LOG_DIR / "error.log",
    level="ERROR",
    **LOG_CONF,
)


async def log_middleware(request: Request, call_next):
    log_id = str(uuid4())
    with logger.contextualize(log_id=log_id):
        try:
            response = await call_next(request)

            if response.status_code in [401, 402, 403, 404]:
                logger.warning(f"Request to {request.url.path} failed")
                
            else:
                logger.info("Successfully accessed " + request.url.path)
        
        except Exception as ex:
            logger.error(f"Request to {request.url.path} failed: {ex}")
            response = JSONResponse(content={"success": False}, status_code=500)

        return response
