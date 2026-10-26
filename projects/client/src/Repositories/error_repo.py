# utils/error_log.py
from typing import Optional, Dict, Any
from Repositories.database import Database  # <-- create sessions here

# repositories/error_repo.py
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from Repositories.schema.schema import ErrorLog
import logging

logger = logging.getLogger(__name__)

def insert_error_log(
    session: Session,
    file_name: str,
    function_name: str,
    error: str,
    err_code: Optional[str] = None,
    actor: str = "system",
) -> Dict[str, Any]:

    try:
        log = ErrorLog(
            file_name=file_name,
            function_name=function_name,
            error=error,
            err_code=err_code,
            created_by=actor,
            updated_by=actor,
        )
        session.add(log)
        session.commit()
        session.refresh(log) 
        return {"ok": True, "code": 200, "id": log.id}
    except Exception as e:
        session.rollback()
        logger.exception("Failed to insert error log: %s", e)
        return {"ok": False, "code": "50001", "error": f"error_log_insert_failed: {e}"}