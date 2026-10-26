class ErrorCode:
    MISSING_ENV_VARS = "MissingEnvVarsErrorCode"
    USER_NOT_FOUND = "UserNotFoundErrorCode"
    WORK_ITEM_NOT_FOUND = "WorkItemNotFoundErrorCode"
    ESCALATE_TO_LANE = "EscalateToLaneErrorCode"
    NO_ROWS_AFFECTED = "NoRowsAffectedErrorCode"
    CONFLICT = "DataConflictErrorCode"
    NOT_FOUND = "NotFoundErrorCode"
    INVALID_JSON_FORMAT = "InvalidJSONFormatErrorCode"
    VALIDATION_ERROR = "ValidationErrorCode"
    MISSING_HEADERS = "MissingHeadersErrorCode"
    MISSING_AUTHORIZATION_HEADER = "MissingAuthorizationHeaderErrorCode"
    INVALID_AUTHORIZATION_HEADER = "InvalidAuthorizationHeaderErrorCode"
    EMPTY_AUTHORIZATION_HEADER = "EmptyAuthorizationHeaderErrorCode"
    MISSING_REQUESTER_ID_HEADER = "MissingRequesterIdHeaderErrorCode"
    INVALID_REQUESTER_ID_HEADER = "InvalidRequesterIdHeaderErrorCode"
    EMPTY_REQUESTER_ID_HEADER = "EmptyRequesterIdHeaderErrorCode"
    INTERNAL_SERVER_ERROR = "InternalServerErrorCode"
    DATABASE_ERROR = "DatabaseErrorErrorCode"
    SERIALIZE_EVENT_DATA = "SerializeEventDataErrorCode"
    COMMIT_TRANSACTION = "CommitTransactionErrorCode"
    EXTERNAL_API_FAILED = "ExternalApiFailed"
    UNAUTHORIZED = "UnauthorizedErrorCode"

ErrorCodeStatus = {
   
    ErrorCode.MISSING_ENV_VARS: "TASK_ENV_001",
    ErrorCode.USER_NOT_FOUND: "TASK_SQL_002",
    ErrorCode.WORK_ITEM_NOT_FOUND: "TASK_SQL_008",
    ErrorCode.ESCALATE_TO_LANE: "TASK_ESC_001",
    ErrorCode.NO_ROWS_AFFECTED: "TASK_SQL_009",
    ErrorCode.CONFLICT: "TASK_SQL_011",
    ErrorCode.INVALID_JSON_FORMAT: "TASK_ENV_003",
    ErrorCode.VALIDATION_ERROR: "TASK_VAL_004",
    ErrorCode.MISSING_HEADERS: "TASK_HDR_001",
    ErrorCode.MISSING_AUTHORIZATION_HEADER: "TASK_HDR_002",
    ErrorCode.INVALID_AUTHORIZATION_HEADER: "TASK_HDR_003",
    ErrorCode.EMPTY_AUTHORIZATION_HEADER: "TASK_HDR_004",
    ErrorCode.MISSING_REQUESTER_ID_HEADER: "TASK_HDR_005",
    ErrorCode.INVALID_REQUESTER_ID_HEADER: "TASK_HDR_006",
    ErrorCode.EMPTY_REQUESTER_ID_HEADER: "TASK_HDR_007",
    ErrorCode.INTERNAL_SERVER_ERROR: "TASK_SQL_005",
    ErrorCode.DATABASE_ERROR: "TASK_SQL_006",
    ErrorCode.SERIALIZE_EVENT_DATA: "TASK_SER_001",
    ErrorCode.COMMIT_TRANSACTION: "TASK_SQL_010",
    ErrorCode.EXTERNAL_API_FAILED: "TASK_EX_001",
    ErrorCode.UNAUTHORIZED: "TASK_AUTH_007",
  
}