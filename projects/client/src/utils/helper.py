import asyncio
import boto3
import functools
import logging
from langchain_aws import ChatBedrock
from settings import config


logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def log_decorator(func):
    if asyncio.iscoroutinefunction(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            logger.info(f"-> {func.__name__} called")
            result = await func(*args, **kwargs)
            logger.info(f"<- {func.__name__} completed")
            return result
        return async_wrapper
    else:
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            logger.info(f"-> {func.__name__} called")
            result = func(*args, **kwargs)
            logger.info(f"<- {func.__name__} completed")
            return result
        return sync_wrapper


def get_bedrock_client():
    # Prefer the standard AWS credential chain (profile, environment, IAM role).
    # Explicit static keys are supported for compatibility but should not be committed.
    credentials = {}
    if config.AWS_ACCESS_KEY and config.AWS_SECRET_KEY:
        credentials = {
            "aws_access_key_id": config.AWS_ACCESS_KEY,
            "aws_secret_access_key": config.AWS_SECRET_KEY,
        }
    return boto3.client(
        service_name="bedrock-runtime",
        region_name=config.REGION,
        **credentials,
    )


@log_decorator
def get_llm(max_tokens: int = 500, temperature: float = 0.7) -> ChatBedrock:
    return ChatBedrock(
        client=get_bedrock_client(),
        model_id=config.MODEL_ID,
        provider="amazon",
        model_kwargs={
            "max_tokens": max_tokens,
            "temperature": temperature,
        },
    )

def get_db_uri():
    return(f"postgresql://{config.db_username}:{config.db_password}"
           f"@{config.db_host}:{config.db_port}/{config.db_name}")
