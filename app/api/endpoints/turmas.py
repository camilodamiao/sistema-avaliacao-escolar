"""
Endpoints para gestão de turmas
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from uuid import UUID

from app.models.database import get_supabase
from app.models.schemas import (
    TurmaCreate, TurmaUpdate, TurmaResponse,
    MessageResponse, ErrorResponse
)

router = APIRouter(
    prefix="/turmas",
    tags=["Turmas"],
    responses={404: {"model": ErrorResponse}}
)


@router.post("/", response_model=TurmaResponse, status_code=201)
async def criar_turma(turma: TurmaCreate):
    """
    Cria uma nova turma
    
    - **serie**: Série ou ano (ex: "1º Ano", "Infantil II")
    - **turma**: Identificador da turma (ex: "A", "B", "C")
    - **ano_letivo**: Ano letivo (padrão: ano atual)
    - **periodo**: manha, tarde ou integral
    - **nivel**: infantil ou fundamental
    - **capacidade_maxima**: Limite de alunos (opcional)
    """
    try:
        supabase = get_supabase()
        
        # Preparar dados para inserção
        data = turma.model_dump()
        
        # Inserir no banco
        result = supabase.table("turmas").insert(data).execute()
        
        if not result.data:
            raise HTTPException(status_code=400, detail="Erro ao criar turma")
        
        # Adicionar campos calculados
        turma_response = TurmaResponse(**result.data[0])
        turma_response.nome_completo = f"{turma_response.serie} {turma_response.turma}"
        turma_response.quantidade_atual = 0  # Nova turma tem 0 alunos
            
        return turma_response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[TurmaResponse])
async def listar_turmas(
    nivel: Optional[str] = Query(None, description="Filtrar por nível"),
    periodo: Optional[str] = Query(None, description="Filtrar por período"),
    ano_letivo: Optional[int] = Query(None, description="Filtrar por ano letivo"),
    ativo: bool = Query(True, description="Mostrar apenas turmas ativas")
):
    """
    Lista todas as turmas com filtros opcionais
    """
    try:
        supabase = get_supabase()
        
        # Começar query
        query = supabase.table("turmas").select("*")
        
        # Aplicar filtros
        if nivel:
            query = query.eq("nivel", nivel)
        if periodo:
            query = query.eq("periodo", periodo)
        if ano_letivo:
            query = query.eq("ano_letivo", ano_letivo)
        query = query.eq("ativo", ativo)
        
        # Ordenar por série e turma
        query = query.order("serie").order("turma")
        
        result = query.execute()
        
        turmas = []
        for turma_data in result.data:
            turma = TurmaResponse(**turma_data)
            turma.nome_completo = f"{turma.serie} {turma.turma}"
            
            # Contar alunos ativos na turma
            count_result = supabase.table("alunos")\
                .select("id", count="exact")\
                .eq("turma_id", str(turma.id))\
                .eq("ativo", True)\
                .execute()
            
            turma.quantidade_atual = count_result.count or 0
            turmas.append(turma)
        
        return turmas
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{turma_id}", response_model=TurmaResponse)
async def obter_turma(turma_id: UUID):
    """
    Obtém uma turma específica pelo ID
    """
    try:
        supabase = get_supabase()
        
        result = supabase.table("turmas")\
            .select("*")\
            .eq("id", str(turma_id))\
            .single()\
            .execute()
            
        if not result.data:
            raise HTTPException(status_code=404, detail="Turma não encontrada")
        
        turma = TurmaResponse(**result.data)
        turma.nome_completo = f"{turma.serie} {turma.turma}"
        
        # Contar alunos ativos
        count_result = supabase.table("alunos")\
            .select("id", count="exact")\
            .eq("turma_id", str(turma_id))\
            .eq("ativo", True)\
            .execute()
        
        turma.quantidade_atual = count_result.count or 0
            
        return turma
        
    except Exception as e:
        if "single" in str(e):
            raise HTTPException(status_code=404, detail="Turma não encontrada")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{turma_id}", response_model=TurmaResponse)
async def atualizar_turma(turma_id: UUID, turma_update: TurmaUpdate):
    """
    Atualiza uma turma existente
    """
    try:
        supabase = get_supabase()
        
        # Preparar apenas campos não-nulos
        update_data = turma_update.model_dump(exclude_unset=True)
        
        if not update_data:
            raise HTTPException(status_code=400, detail="Nenhum campo para atualizar")
        
        result = supabase.table("turmas")\
            .update(update_data)\
            .eq("id", str(turma_id))\
            .execute()
            
        if not result.data:
            raise HTTPException(status_code=404, detail="Turma não encontrada")
        
        turma = TurmaResponse(**result.data[0])
        turma.nome_completo = f"{turma.serie} {turma.turma}"
        
        # Contar alunos ativos
        count_result = supabase.table("alunos")\
            .select("id", count="exact")\
            .eq("turma_id", str(turma_id))\
            .eq("ativo", True)\
            .execute()
        
        turma.quantidade_atual = count_result.count or 0
            
        return turma
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{turma_id}", response_model=MessageResponse)
async def deletar_turma(turma_id: UUID):
    """
    Desativa uma turma (soft delete)
    """
    try:
        supabase = get_supabase()
        
        # Soft delete - apenas marca como inativo
        result = supabase.table("turmas")\
            .update({"ativo": False})\
            .eq("id", str(turma_id))\
            .execute()
            
        if not result.data:
            raise HTTPException(status_code=404, detail="Turma não encontrada")
            
        return MessageResponse(message="Turma desativada com sucesso")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{turma_id}/alunos-count")
async def contar_alunos_turma(turma_id: UUID):
    """
    Conta quantos alunos ativos tem na turma
    """
    try:
        supabase = get_supabase()
        
        # Verificar se turma existe
        turma = supabase.table("turmas")\
            .select("id, serie, turma")\
            .eq("id", str(turma_id))\
            .single()\
            .execute()
            
        if not turma.data:
            raise HTTPException(status_code=404, detail="Turma não encontrada")
        
        # Contar alunos
        result = supabase.table("alunos")\
            .select("id", count="exact")\
            .eq("turma_id", str(turma_id))\
            .eq("ativo", True)\
            .execute()
            
        return {
            "turma_id": turma_id,
            "turma_nome": f"{turma.data['serie']} {turma.data['turma']}",
            "total_alunos": result.count or 0
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))