# 📋 ÂNCORA: REGRA-NEGÓCIO - Schemas de validação
# Contexto: Define estrutura e validação de todos os dados
# Cuidado: Alterações afetam frontend e validações

from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
from datetime import date, datetime
from typing import Optional, List, Dict, Literal
from uuid import UUID


# 🚨 ÂNCORA: CRÍTICO - Enums do domínio
# Definindo os tipos Literal primeiro
NivelEnsino = Literal["infantil", "fundamental"]
PeriodoAula = Literal["manha", "tarde", "integral"]
TipoUsuario = Literal["professor", "coordenador", "admin"]
StatusRelatorio = Literal["rascunho", "revisao", "aprovado"]
StatusAvaliacao = Literal["rascunho", "concluida"]
TipoTag = Literal["positiva", "negativa", "neutra"]
NivelTag = Literal["infantil", "fundamental", "ambos"]
TipoEnvio = Literal["email", "whatsapp", "api"]
Trimestre = Literal[1, 2, 3]

# ========== SCHEMAS DE TURMA ==========

class TurmaBase(BaseModel):
    serie: str = Field(..., min_length=1, max_length=50, description="Ex: 1º Ano, Infantil II")
    turma: str = Field(..., min_length=1, max_length=10, description="Ex: A, B, C")
    periodo: PeriodoAula
    nivel: NivelEnsino

class TurmaCreate(TurmaBase):
    professor_id: Optional[UUID] = None  # Opcional no início

class TurmaUpdate(BaseModel):
    serie: Optional[str] = None
    turma: Optional[str] = None
    ano_letivo: Optional[int] = None
    periodo: Optional[PeriodoAula] = None
    capacidade_maxima: Optional[int] = None
    professor_id: Optional[UUID] = None
    ativo: Optional[bool] = None


# ========== SCHEMAS DE TURMA ==========

class TurmaBase(BaseModel):
    serie: str = Field(..., min_length=1, max_length=50, description="Ex: 1º Ano, Infantil II")
    turma: str = Field(..., min_length=1, max_length=10, description="Ex: A, B, C")
    ano_letivo: int = Field(default_factory=lambda: datetime.now().year)
    periodo: PeriodoAula
    nivel: NivelEnsino
    capacidade_maxima: Optional[int] = Field(None, ge=1, le=50)

class TurmaCreate(TurmaBase):
    professor_id: Optional[UUID] = None

class TurmaUpdate(BaseModel):
    serie: Optional[str] = None
    turma: Optional[str] = None
    ano_letivo: Optional[int] = None
    periodo: Optional[PeriodoAula] = None
    capacidade_maxima: Optional[int] = None
    professor_id: Optional[UUID] = None
    ativo: Optional[bool] = None

class TurmaResponse(TurmaBase):
    id: UUID
    professor_id: Optional[UUID]
    ativo: bool
    created_at: datetime
    updated_at: datetime
    
    # Campos calculados
    nome_completo: Optional[str] = None
    quantidade_atual: Optional[int] = 0
    
    model_config = ConfigDict(from_attributes=True)
    
    @field_validator('nome_completo', mode='before')
    def gerar_nome_completo(cls, v, values):
        if 'serie' in values.data and 'turma' in values.data:
            return f"{values.data['serie']} {values.data['turma']}"
        return v


# ========== SCHEMAS DE ALUNO ==========

class AlunoBase(BaseModel):
    matricula: str = Field(..., min_length=1, max_length=50)
    nome: str = Field(..., min_length=2, max_length=255)
    data_nascimento: date
    foto_url: Optional[str] = Field(None, max_length=500)
    
    # Responsável
    responsavel_nome: Optional[str] = Field(None, max_length=255)
    responsavel_telefone: Optional[str] = Field(None, max_length=20)
    responsavel_email: Optional[EmailStr] = None
    responsavel_foto_url: Optional[str] = Field(None, max_length=500)
    
    # Necessidades especiais
    necessidades_especiais: bool = False
    necessidades_descricao: Optional[str] = None
    alergias: Optional[str] = None
    restricoes_alimentares: Optional[str] = None
    
    observacoes: Optional[str] = None

class AlunoCreate(AlunoBase):
    turma_id: UUID

class AlunoUpdate(BaseModel):
    nome: Optional[str] = None
    data_nascimento: Optional[date] = None
    foto_url: Optional[str] = None
    turma_id: Optional[UUID] = None
    responsavel_nome: Optional[str] = None
    responsavel_telefone: Optional[str] = None
    responsavel_email: Optional[EmailStr] = None
    responsavel_foto_url: Optional[str] = None
    necessidades_especiais: Optional[bool] = None
    necessidades_descricao: Optional[str] = None
    alergias: Optional[str] = None
    restricoes_alimentares: Optional[str] = None
    observacoes: Optional[str] = None
    ativo: Optional[bool] = None
    data_saida: Optional[date] = None

class AlunoResponse(AlunoBase):
    id: UUID
    turma_id: UUID
    ativo: bool
    data_saida: Optional[date] = None
    created_at: datetime
    updated_at: datetime
    
    # Calculado
    idade: Optional[int] = None
    tem_restricoes: Optional[bool] = None
    
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            date: lambda v: v.isoformat() if v else None,
            datetime: lambda v: v.isoformat() if v else None
        }
    )
    
    @field_validator('idade', mode='before')
    def calcular_idade(cls, v, values):
        if 'data_nascimento' in values.data:
            nascimento = values.data['data_nascimento']
            hoje = date.today()
            return hoje.year - nascimento.year - ((hoje.month, hoje.day) < (nascimento.month, nascimento.day))
        return v
    
    @field_validator('tem_restricoes', mode='before')
    def verificar_restricoes(cls, v, values):
        return bool(
            values.data.get('necessidades_especiais') or
            values.data.get('alergias') or
            values.data.get('restricoes_alimentares')
        )


# ========== SCHEMAS DE TAG ==========

class TagBase(BaseModel):
    nome: str = Field(..., min_length=2, max_length=100)
    tipo: TipoTag = "neutra"
    categoria: Optional[str] = Field(None, max_length=50)
    cor: str = Field("#0066cc", pattern="^#[0-9A-Fa-f]{6}$")
    nivel_ensino: NivelTag = "ambos"

class TagCreate(TagBase):
    usuario_id: Optional[UUID] = None  # Se None, será tag global

class TagResponse(TagBase):
    id: UUID
    usuario_id: Optional[UUID]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
    
    @field_validator('cor', mode='before')
    def definir_cor_por_tipo(cls, v, values):
        if not v and 'tipo' in values.data:
            cores_padrao = {
                'positiva': '#28a745',  # Verde
                'negativa': '#dc3545',  # Vermelho
                'neutra': '#6c757d'     # Cinza
            }
            return cores_padrao.get(values.data['tipo'], '#0066cc')
        return v


# ========== SCHEMAS DE AVALIAÇÃO ==========

class AvaliacaoBase(BaseModel):
    data_avaliacao: date
    trimestre: Trimestre
    status: StatusAvaliacao = "rascunho"
    campos_avaliados: Dict[str, int] = Field(..., description="Mapa campo->nota (1-3)")
    observacao_livre: Optional[str] = None
    
    @field_validator('campos_avaliados')
    def validar_notas(cls, v):
        """Valida que todas as notas estão entre 1 e 3"""
        for campo, nota in v.items():
            if nota not in [1, 2, 3]:
                raise ValueError(f"Nota do campo '{campo}' deve ser 1, 2 ou 3")
        return v

class AvaliacaoCreate(AvaliacaoBase):
    aluno_id: UUID
    tags_ids: List[UUID] = Field(default_factory=list)

class AvaliacaoUpdate(BaseModel):
    status: Optional[StatusAvaliacao] = None
    campos_avaliados: Optional[Dict[str, int]] = None
    observacao_livre: Optional[str] = None
    tags_ids: Optional[List[UUID]] = None

class AvaliacaoResponse(AvaliacaoBase):
    id: UUID
    aluno_id: UUID
    ano: int
    professor_id: Optional[UUID]
    tags: List[TagResponse] = []
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ========== SCHEMAS DE RELATÓRIO ==========

class RevisaoHistorico(BaseModel):
    data: datetime
    usuario_id: UUID
    usuario_nome: str
    comentario: Optional[str]
    versao_anterior: Optional[str]

class RelatorioCreate(BaseModel):
    aluno_id: UUID
    trimestre: Trimestre
    ano: int

class RelatorioUpdate(BaseModel):
    texto_final: Optional[str] = None
    status: Optional[StatusRelatorio] = None
    adicionar_revisao: Optional[RevisaoHistorico] = None

class RelatorioResponse(BaseModel):
    id: UUID
    aluno_id: UUID
    trimestre: Trimestre
    ano: int
    texto_final: str
    historico_revisoes: List[RevisaoHistorico] = []
    dados_consolidados: Dict
    status: StatusRelatorio
    pdf_url: Optional[str]
    enviado_em: Optional[datetime]
    enviado_por: Optional[TipoEnvio]
    professor_id: Optional[UUID]
    coordenador_id: Optional[UUID]
    aprovado_em: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ========== SCHEMAS DE RESPOSTA PADRÃO ==========

class MessageResponse(BaseModel):
    message: str
    
class ErrorResponse(BaseModel):
    detail: str
    
class PaginationParams(BaseModel):
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)