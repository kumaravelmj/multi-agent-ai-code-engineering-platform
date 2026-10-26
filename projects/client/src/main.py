from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import FastAPI, Request
from routes.agent_route import router
from utils.exceptions.error_code import ErrorCode,ErrorCodeStatus
from models.agent_model import APIResponse,Error
from utils.exceptions.custom_app_exception import CustomAppException
from settings import HttpStatusCode
from migration.migration import run_migration


import uvicorn
main = FastAPI(
    title="MultiAgent chatbot",
    description="REST API for managing orders",
    version="1.0.0",
)
@main.on_event("startup")
def startup():
    run_migration()

main.include_router(router)


@main.exception_handler(CustomAppException)
async def custom_exception_handler(request: Request, exc: CustomAppException):
    api_response = exc.to_api_response()
    return JSONResponse(
        status_code=exc.status_code,
        content=api_response.to_dict()
    )

@main.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        errors.append(Error(
            code=ErrorCode.VALIDATION_ERROR,
            message=f"{error['loc'][-1]}: {error['msg']}",
            error_code_id=ErrorCodeStatus[ErrorCode.VALIDATION_ERROR]
        ))
    api_response = APIResponse(
        data=None,
        errors=errors,
        code=HttpStatusCode.UNPROCESSABLE_ENTITY
    )
    return JSONResponse(
        status_code=HttpStatusCode.UNPROCESSABLE_ENTITY,
        content=api_response.to_dict()
    )


if __name__ == "__main__":

    uvicorn.run(
        "main:main",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info"
    )
