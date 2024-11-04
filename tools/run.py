import os
from pathlib import Path
from datetime import datetime as dt
import click
from dotenv import load_dotenv
from zenml.client import Client
from pipelines.etl import data_etl_pipeline
from pipelines.ingestion import data_ingestion_pipeline
from loguru import logger
from settings import settings

# Load environment variables
load_dotenv()

# Debug environment variables
def check_env_vars():
    required_vars = {
        "MONGODB_CONNECTION_STRING": settings.MONGODB_CONNECTION_STRING,
        "MONGODB_DATABASE_NAME": settings.MONGODB_DATABASE_NAME,
        "MONGODB_COLLECTION_NAME": settings.MONGODB_COLLECTION_NAME,
        "OPENAI_API_KEY": settings.OPENAI_API_KEY,
        "ZIP_URL": settings.ZIP_URL,  # If this is still needed for ETL
    }
    
    missing_vars = [k for k, v in required_vars.items() if not v]
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    logger.info("Environment variables loaded successfully")
    
    return required_vars

@click.command()
@click.option(
    "--no-cache",
    is_flag=True,
    default=False,
    help="Disable caching for the pipeline run.",
)
@click.option(
    "--run-etl",
    is_flag=True,
    default=False,
    help="Whether to run the ETL pipeline.",
)
@click.option(
    "--run-ingestion",
    is_flag=True,
    default=False,
    help="Whether to run the ingestion pipeline.",
)
def main(
    no_cache: bool = False,
    run_etl: bool = False,
    run_ingestion: bool = False,
) -> None:
    # Check environment variables
    env_vars = check_env_vars()
    
    # Configure pipeline options
    pipeline_args = {
        "enable_cache": not no_cache,
    }
    
    if run_etl:
        logger.info("Running ETL pipeline...")
        pipeline_args["run_name"] = f"etl_run_{dt.now().strftime('%Y_%m_%d_%H_%M_%S')}"
        
        # Create and run ETL pipeline
        data_etl_pipeline.with_options(**pipeline_args)(
            zip_url=settings.ZIP_URL,
            collection_name=settings.MONGODB_COLLECTION_NAME,
            mongodb_connection_string=settings.MONGODB_CONNECTION_STRING
        )
        logger.info("ETL pipeline completed")
    
    if run_ingestion:
        logger.info("Running ingestion pipeline")
        pipeline_args = {}
        if no_cache:
            pipeline_args["enable_cache"] = False
        
        pipeline_args["run_name"] = f"ingestion_run_{dt.now().strftime('%Y_%m_%d_%H_%M_%S')}"
        
        # Create and run ingestion pipeline
        data_ingestion_pipeline.with_options(**pipeline_args)()
        logger.info("Ingestion pipeline completed")

if __name__ == "__main__":
    # Set up logging
    log_path = Path("logs")
    log_path.mkdir(exist_ok=True)
    
    logger.add(
        log_path / f"pipeline_{dt.now().strftime('%Y_%m_%d_%H_%M_%S')}.log",
        rotation="500 MB",
        retention="10 days",
        level="INFO"
    )
    
    try:
        main()
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")
        raise