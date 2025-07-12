"""
🚨 ÂNCORA: CRÍTICO - Configuração central do sistema
Contexto: Todas as configurações do sistema devem passar por aqui
Cuidado: Alterações podem afetar todo o sistema
Dependências: Todos os módulos dependem dessas configurações
"""

from pydantic_settings import BaseSettings
from typing import Optional, Literal
from functools import lru_cache


class Settings(BaseSettings):
    """Configurações do sistema carregadas do ambiente"""
    
    # Supabase
    supabase_url: str
    supabase_key: str
    
    # API Keys para IA
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    
    # Configuração do servidor
    host: str = "0.0.0.0"
    port: int = 8000
    environment: Literal["development", "production"] = "development"
    
    # JWT
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24 horas
    
    # Configuração de IA
    default_llm_provider: Literal["openai", "anthropic", "google"] = "openai"
    default_llm_model: str = "gpt-3.5-turbo"
    llm_temperature: float = 0.7
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Retorna instância única das configurações (Singleton)
    Usa cache para evitar recarregar o .env múltiplas vezes
    """
    return Settings()


# 🚨 ÂNCORA: CRÍTICO - Constantes do domínio educacional
# Contexto: Valores fixos baseados na análise dos relatórios
# Cuidado: Não alterar sem consultar os templates de avaliação

ESCALA_AVALIACAO = {
    1: "Realiza com autonomia",
    2: "Em desenvolvimento", 
    3: "Precisa de intervenção"
}

CATEGORIAS_FUNDAMENTAL = [
    "Português", "Matemática", "História", "Geografia", "Ciências",
    "Artes", "Educação Física", "Música", "Inglês", "Eu no Mundo"
]

CATEGORIAS_INFANTIL = [
    "Integração e Adaptação", "Socioemocional", "Linguagem", 
    "Cognição", "Motricidade Fina", "Educação Física", 
    "Artes", "Inglês", "Música"
]

# Tags comportamentais padrão
TAGS_COMPORTAMENTAIS_PADRAO = [
    "Interage bem com colegas",
    "Demonstra liderança",
    "Aprende melhor visualmente",
    "Necessita de apoio individual",
    "Muito participativo",
    "Tímido mas atento",
    "Criativo e imaginativo",
    "Organizado",
    "Precisa melhorar organização",
    "Excelente memória",
    "Raciocínio lógico desenvolvido",
    "Boa coordenação motora",
    "Dificuldade de concentração",
    "Muito concentrado",
    "Respeitoso e educado"
]