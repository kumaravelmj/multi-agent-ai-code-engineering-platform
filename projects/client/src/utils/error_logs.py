from typing import Optional, Dict, Any
from Repositories.error_repo import insert_error_log
from Repositories.database import Database

def log_error(
    file_name: str,
    function_name: str,
    error: str,
    err_code: Optional[str] = None,
    actor: str = "system",
) -> Dict[str, Any]:
    try:
        with Database().SessionLocal() as session:
            return insert_error_log(
                session=session,
                file_name=file_name,
                function_name= function_name,
                error=error,
                err_code=err_code,
                actor=actor,
            )
    except Exception as e:
        return {"ok": False, "code": "50002", "error": f"log_error_failed: {e}"}