class HttpStatusCode:
    OK = 200
    CREATED = 201
    NO_CONTENT = 204
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    CONFLICT = 409
    UNPROCESSABLE_ENTITY = 422
    INTERNAL_SERVER_ERROR = 500
    SERVICE_UNAVAILABLE = 503
    
from dataclasses import dataclass
import os
from dotenv import load_dotenv
load_dotenv()
@dataclass
class Config:
    db_port: str
    db_host: str
    db_name: str
    db_username: str
    db_password: str
    MODEL_ID :str
    PROVIDER :str
    AWS_ACCESS_KEY :str
    AWS_SECRET_KEY :str
    REGION :str
    MCP_SERVER_URL : str


    
def get_config():
    return Config(
        db_port=os.getenv('DB_PORT', '5432'),
        db_host=os.getenv('DB_HOST', 'localhost'),
        db_name=os.getenv('DB_NAME', 'orders'),
        db_username=os.getenv('DB_USERNAME', 'postgres'),
        db_password=os.getenv('DB_PASSWORD', ''),
        MODEL_ID =os.getenv('MODEL_ID',""),
        PROVIDER  =os.getenv('PROVIDER',"amazon" ),
        AWS_ACCESS_KEY =os.getenv('AWS_ACCESS_KEY',"" ),
        AWS_SECRET_KEY =os.getenv('AWS_SECRET_KEY',"" ),
        REGION = os.getenv('REGION',"us-east-1"),
        MCP_SERVER_URL =os.getenv( 'MCP_SERVER_URL' ,"http://localhost:8000/mcp")
    )

config = get_config()