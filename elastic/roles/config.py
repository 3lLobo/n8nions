import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class ElasticConfig:
    """Configuration for an Elasticsearch connection."""
    host: str
    api_key: str

class AppConfig:
    """Main application configuration loader."""
    SOURCE = ElasticConfig(
        host=os.getenv("SOURCE_ES_HOST", ""),
        api_key=os.getenv("SOURCE_ES_API_KEY", "")
    )
    DESTINATION = ElasticConfig(
        host=os.getenv("DEST_ES_HOST", ""),
        api_key=os.getenv("DEST_ES_API_KEY", "")
    )
    ROLE_NAME = os.getenv("ROLE_NAME", "my_role")
