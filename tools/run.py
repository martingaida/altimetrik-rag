import os
from pathlib import Path
from datetime import datetime as dt
import click
from dotenv import load_dotenv
from zenml.client import Client
from pipelines.data_etl import data_etl_pipeline
from loguru import logger

# Load environment variables
load_dotenv()

# Debug environment variables
def check_env_vars():
    required_vars = {
        "ZIP_URL": os.getenv("ZIP_URL"),
        "MONGODB_CONNECTION_STRING": os.getenv("MONGODB_CONNECTION_STRING"),
        "QDRANT_HOST": os.getenv("QDRANT_HOST", "localhost"),
        "QDRANT_PORT": os.getenv("QDRANT_PORT", "6333")
    }
    
    missing_vars = [k for k, v in required_vars.items() if v is None]
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    logger.info("Environment variables loaded:")
    for k, v in required_vars.items():
        logger.info(f"{k}: {v}")
    
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
def main(
    no_cache: bool = False,
    run_etl: bool = False,
) -> None:
    if run_etl:
        # Check environment variables
        env_vars = check_env_vars()
        
        # Configure pipeline options
        pipeline_args = {
            "enable_cache": not no_cache,
            "run_name": f"etl_run_{dt.now().strftime('%Y_%m_%d_%H_%M_%S')}",
        }
        
        # Create and run pipeline
        data_etl_pipeline.with_options(**pipeline_args)(
            zip_url=env_vars["ZIP_URL"],
            collection_name="digital_data",
            mongodb_connection_string=env_vars["MONGODB_CONNECTION_STRING"]
        )

if __name__ == "__main__":
    main()