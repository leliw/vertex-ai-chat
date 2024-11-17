from typing import List, Optional
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

from ampf.base.ampf_base_factory import AmpfBaseFactory


class DefaultUserConfig(BaseModel):
    email: str = "marcin.leliwa@gmail.com"
    password: str = "admin"
    roles: List[str] = ["admin"]


class KnowledgeBaseConfig(BaseModel):
    embedding_model: str = "text-multilingual-embedding-002"
    embedding_search_limit: int = 5


class GenerativeModelConfig(BaseModel):
    max_output_tokens: int = 8192
    temperature: float = 0.9
    top_p: float = 0.95


class SmtpConfig(BaseModel):
    host: str = "smtp.gmail.com"
    port: int = 465
    username: Optional[str] = None
    password: Optional[str] = None
    use_ssl: bool = True


class ResetPasswordMailConfig(BaseModel):
    sender: str = "admin@example.com"
    subject: str = "Resetowanie hasła - Chat"
    body_template: str = """Witaj!
        
Otrzymałeś ten email, ponieważ poprosiłeś o zresetowanie hasła.
Aby zresetować swoje hasło, wpisz kod: {reset_code} w formularzu.
Kod jest ważny przez {reset_code_expire_minutes} minut.
Jeśli nie prosiłeś o zresetowanie hasła, zignoruj ten email.
"""


class ServerConfig(BaseSettings):
    model_config = SettingsConfigDict(env_nested_delimiter="__")

    version: str = "0.6.2"

    jwt_secret_key: str
    default_user: DefaultUserConfig = DefaultUserConfig()

    models: List[str] = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-1.0-pro"]
    default_model: str = "gemini-1.5-flash"

    google_oauth_client_id: str = ""
    google_oauth_client_secret: str = ""

    knowledge_base: KnowledgeBaseConfig = KnowledgeBaseConfig()
    generative_model_config: GenerativeModelConfig = GenerativeModelConfig()
    smtp: SmtpConfig = SmtpConfig()
    reset_password_mail: ResetPasswordMailConfig = ResetPasswordMailConfig()


class ClientConfig(BaseModel):
    version: str
    google_oauth_client_id: str


# UserConfig isn't used jet !!!!
# The key should be username
class UserConfig(BaseModel):
    agent: Optional[str] = None


class UserConfigService:
    def __init__(self, factory: AmpfBaseFactory):
        self.storage = factory.create_compact_storage(
            "user_config", UserConfig, key_name="config"
        )

    def get(self) -> UserConfig:
        return self.storage.get("config")

    def put(self, config: UserConfig):
        self.storage.put("config", config)

    def patch(self, patch_data: UserConfig) -> None:
        key = "config"
        item = self.storage.get(key)
        patch_dict = patch_data.model_dump(exclude_unset=True)
        item.__dict__.update(patch_dict)
        self.storage.put(key, item)
