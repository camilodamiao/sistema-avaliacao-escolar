"""
Sistema de Avaliação Escolar - API Principal
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from app.config import (
    get_settings,
    ESCALA_AVALIACAO,
    CATEGORIAS_FUNDAMENTAL,
    CATEGORIAS_INFANTIL,
    TAGS_COMPORTAMENTAIS_PADRAO
)


# 🚨 ÂNCORA: CRÍTICO - Configuração do ciclo de vida da aplicação
# Contexto: Gerencia recursos que devem ser iniciados/fechados com a aplicação
# Dependências: Conexões de banco, cache, etc.
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação"""
    # Startup
    print("🚀 Iniciando Sistema de Avaliação Escolar...")
    print("📊 Ambiente:", get_settings().environment)
    print("🔌 Conectando ao Supabase...")
    
    yield
    
    # Shutdown
    print("👋 Encerrando aplicação...")


# Criar instância do FastAPI
app = FastAPI(
    title="Sistema de Avaliação Escolar",
    description="API para gestão de avaliações trimestrais com IA",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc"  # ReDoc
)


# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 📋 ÂNCORA: REGRA-NEGÓCIO - Endpoints de teste e saúde
# Contexto: Endpoints básicos para verificar funcionamento do sistema

@app.get("/")
async def root():
    """Endpoint raiz - Informações básicas da API"""
    return {
        "message": "Sistema de Avaliação Escolar",
        "version": "1.0.0",
        "status": "online",
        "docs": "/docs",
        "ambiente": get_settings().environment
    }


@app.get("/health")
async def health_check():
    """Verifica saúde da aplicação e conexões"""
    settings = get_settings()
    
    # Verificar configurações
    health_status = {
        "status": "healthy",
        "checks": {
            "api": "ok",
            "supabase_configured": bool(settings.supabase_url),
            "ai_providers": {
                "openai": bool(settings.openai_api_key),
                "anthropic": bool(settings.anthropic_api_key),
                "google": bool(settings.google_api_key)
            }
        }
    }
    
    return health_status


@app.get("/config/info")
async def config_info():
    """Retorna informações de configuração (sem dados sensíveis)"""
    settings = get_settings()
    
    return {
        "environment": settings.environment,
        "default_llm_provider": settings.default_llm_provider,
        "ai_providers_configured": {
            "openai": bool(settings.openai_api_key),
            "anthropic": bool(settings.anthropic_api_key),
            "google": bool(settings.google_api_key)
        },
        "supabase_configured": bool(settings.supabase_url),
        "categorias": {
            "fundamental": CATEGORIAS_FUNDAMENTAL,
            "infantil": CATEGORIAS_INFANTIL
        },
        "escala_avaliacao": ESCALA_AVALIACAO,
        "tags_padrao": TAGS_COMPORTAMENTAIS_PADRAO[:5] + ["..."]  # Mostra apenas 5
    }


# 🚨 ÂNCORA: CRÍTICO - Registro de rotas
# Contexto: Todas as rotas da API devem ser registradas aqui
# Cuidado: Ordem pode afetar precedência de rotas
from app.api.endpoints import turmas, alunos

app.include_router(turmas.router, prefix="/api/v1")
app.include_router(alunos.router, prefix="/api/v1")


if __name__ == "__main__":
    settings = get_settings()
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.environment == "development"
    )