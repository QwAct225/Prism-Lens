import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API Settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_TITLE: str = "ArXiv Papers API"
    API_VERSION: str = "1.0.0"

    # Project directories
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR: str = os.path.join(BASE_DIR, "data")
    PLOTS_DIR: str = os.path.join(DATA_DIR, "plots")
    JOBS_DIR: str = os.path.join(DATA_DIR, "jobs")

    # File paths
    RAW_CSV_PATH: str = os.path.join(DATA_DIR, "arxiv_papers_raw.csv")
    CLEANED_CSV_PATH: str = os.path.join(DATA_DIR, "arxiv_papers_cleaned.csv")
    EMBEDDINGS_PATH: str = os.path.join(DATA_DIR, "embeddings.npy")

    # Scraper script path
    SCRAPER_SCRIPT_PATH: str = os.path.join(BASE_DIR, "scripts", "run_scraper.py")
    PREPROCESSING_SCRIPT_PATH: str = os.path.join(BASE_DIR, "scripts", "run_preprocessing.py")
    VISUALIZATION_SCRIPT_PATH: str = os.path.join(BASE_DIR, "scripts", "run_visualization.py")
    EMBEDDING_SCRIPT_PATH: str = os.path.join(BASE_DIR, "scripts", "run_embedding.py")

    class Config:
        env_file = ".env"


settings = Settings()