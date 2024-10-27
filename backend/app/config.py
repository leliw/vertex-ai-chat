from typing import List
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class KnowledgeBaseConfig(BaseModel):
    embedding_model: str = "text-multilingual-embedding-002"
    embedding_search_limit: int = 5


class GenerativeModelConfig(BaseModel):
    max_output_tokens: int = 8192
    temperature: float = 0.9
    top_p: float = 0.95


class ServerConfig(BaseSettings):
    model_config = SettingsConfigDict(env_nested_delimiter="__")

    version: str = "0.5.9"
    
    models: List[str] = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-1.0-pro"]
    default_model: str = "gemini-1.5-flash"

    google_oauth_client_id: str = ""
    google_oauth_client_secret: str = ""
    
    knowledge_base: KnowledgeBaseConfig = KnowledgeBaseConfig()
    generative_model_config: GenerativeModelConfig = GenerativeModelConfig()


class ClientConfig(BaseModel):
    version: str
    google_oauth_client_id: str
