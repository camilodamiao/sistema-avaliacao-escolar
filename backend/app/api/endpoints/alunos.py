"""
Endpoints para gestão de alunos
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from uuid import UUID
from datetime import date

from app.models.database import get_supabase
from app.models.schemas import (
    AlunoCreate, AlunoUpdate, AlunoResponse,
    MessageResponse, ErrorResponse
)

router = APIRouter(
    prefix="/alunos",
    tags=["Alunos"],
    responses={404: {"model": ErrorResponse}}
)


@router.post("/", response_model=AlunoResponse, status_code=201)
async def criar_aluno(aluno: AlunoCreate):
    """
    Cria um novo aluno
    
    - **matricula**: Código único do aluno (definido pela escola)
    - **nome**: Nome completo do aluno
    - **data_nascimento**: Data de nascimento (YYYY-MM-DD)
    - **turma_id**: ID da turma onde o aluno será matriculado
    - **responsavel_nome**: Nome do responsável
    - **responsavel_telefone**: Telefone para contato
    - **responsavel_email**: Email do responsável
    - **necessidades_especiais**: Se tem necessidades especiais
    - **necessidades_descricao**: Descrição das necessidades (obrigatório se necessidades_especiais = true)
    - **alergias**: Lista de alergias (opcional)
    - **restricoes_alimentares**: Restrições alimentares (opcional)
    """
    try:
        supabase = get_supabase()
        
        # Verificar se matrícula já existe
        existing = supabase.table("alunos")\
            .select("id")\
            .eq("matricula", aluno.matricula)\
            .execute()
            
        if existing.data:
            raise HTTPException(
                status_code=400, 
                detail=f"Matrícula '{aluno.matricula}' já está em uso"
            )
        
        # Verificar se turma existe
        try:
            turma = supabase.table("turmas")\
                .select("id, capacidade_maxima")\
                .eq("id", str(aluno.turma_id))\
                .single()\
                .execute()
        except Exception:
            raise HTTPException(
                status_code=404, 
                detail=f"Turma com ID '{aluno.turma_id}' não encontrada. Verifique se o ID está correto."
            )
            
        if not turma.data:
            raise HTTPException(status_code=404, detail="Turma não encontrada")
        
        # Verificar capacidade da turma (se definida)
        if turma.data.get('capacidade_maxima'):
            count_result = supabase.table("alunos")\
                .select("id", count="exact")\
                .eq("turma_id", str(aluno.turma_id))\
                .eq("ativo", True)\
                .execute()
                
            if count_result.count >= turma.data['capacidade_maxima']:
                raise HTTPException(
                    status_code=400, 
                    detail="Turma já atingiu a capacidade máxima"
                )
        
        # Validar necessidades especiais
        if aluno.necessidades_especiais and not aluno.necessidades_descricao:
            raise HTTPException(
                status_code=400,
                detail="Descrição das necessidades especiais é obrigatória"
            )
        
        # Validar data de nascimento
        if aluno.data_nascimento >= date.today():
            raise HTTPException(
                status_code=400,
                detail="Data de nascimento não pode ser futura"
            )
        
        # Preparar dados para inserção
        # 🚨 ÂNCORA: CRÍTICO - Serialização JSON para datas
        # Contexto: model_dump(mode='json') converte objetos date para string ISO
        # Dependências: Necessário para evitar erro de serialização JSON
        
        data = aluno.model_dump(mode="json")
        
        # Inserir no banco
        result = supabase.table("alunos").insert(data).execute()
        
        if not result.data:
            raise HTTPException(status_code=400, detail="Erro ao criar aluno")
            
        return AlunoResponse(**result.data[0])
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[AlunoResponse])
async def listar_alunos(
    turma_id: Optional[UUID] = Query(None, description="Filtrar por turma"),
    necessidades_especiais: Optional[bool] = Query(None, description="Filtrar por necessidades especiais"),
    ativo: bool = Query(True, description="Mostrar apenas alunos ativos"),
    ordenar_por: str = Query("nome", description="Ordenar por: nome, idade, matricula"),
    limite: int = Query(50, ge=1, le=100, description="Limite de resultados"),
    offset: int = Query(0, ge=0, description="Offset para paginação")
):
    """
    Lista alunos com filtros opcionais
    """
    try:
        supabase = get_supabase()
        
        # Começar query
        query = supabase.table("alunos").select("*")
        
        # Aplicar filtros
        if turma_id:
            query = query.eq("turma_id", str(turma_id))
        if necessidades_especiais is not None:
            query = query.eq("necessidades_especiais", necessidades_especiais)
        query = query.eq("ativo", ativo)
        
        # Ordenação
        if ordenar_por == "idade":
            query = query.order("data_nascimento", desc=False)  # Mais velho primeiro
        elif ordenar_por == "matricula":
            query = query.order("matricula")
        else:  # default: nome
            query = query.order("nome")
        
        # Paginação
        query = query.limit(limite).offset(offset)
        
        result = query.execute()
        
        return [AlunoResponse(**aluno) for aluno in result.data]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{aluno_id}", response_model=AlunoResponse)
async def obter_aluno(aluno_id: UUID):
    """
    Obtém um aluno específico pelo ID
    """
    try:
        supabase = get_supabase()
        
        result = supabase.table("alunos")\
            .select("*")\
            .eq("id", str(aluno_id))\
            .single()\
            .execute()
            
        if not result.data:
            raise HTTPException(status_code=404, detail="Aluno não encontrado")
            
        return AlunoResponse(**result.data)
        
    except Exception as e:
        if "single" in str(e):
            raise HTTPException(status_code=404, detail="Aluno não encontrado")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{aluno_id}", response_model=AlunoResponse)
async def atualizar_aluno(aluno_id: UUID, aluno_update: AlunoUpdate):
    """
    Atualiza dados de um aluno
    """
    try:
        supabase = get_supabase()
        
        # Preparar apenas campos não-nulos
        update_data = aluno_update.model_dump(exclude_unset=True)
        
        if not update_data:
            raise HTTPException(status_code=400, detail="Nenhum campo para atualizar")
        
        # Validações específicas se campos estão sendo atualizados
        if "matricula" in update_data:
            # Verificar se nova matrícula já existe
            existing = supabase.table("alunos")\
                .select("id")\
                .eq("matricula", update_data["matricula"])\
                .neq("id", str(aluno_id))\
                .execute()
                
            if existing.data:
                raise HTTPException(
                    status_code=400,
                    detail=f"Matrícula '{update_data['matricula']}' já está em uso"
                )
        
        if "turma_id" in update_data:
            # Verificar se nova turma existe e tem capacidade
            turma = supabase.table("turmas")\
                .select("id, capacidade_maxima")\
                .eq("id", str(update_data["turma_id"]))\
                .single()\
                .execute()
                
            if not turma.data:
                raise HTTPException(status_code=404, detail="Turma não encontrada")
                
            # Verificar capacidade
            if turma.data.get('capacidade_maxima'):
                count_result = supabase.table("alunos")\
                    .select("id", count="exact")\
                    .eq("turma_id", str(update_data["turma_id"]))\
                    .eq("ativo", True)\
                    .neq("id", str(aluno_id))\
                    .execute()
                    
                if count_result.count >= turma.data['capacidade_maxima']:
                    raise HTTPException(
                        status_code=400,
                        detail="Turma já atingiu a capacidade máxima"
                    )
        
        if "necessidades_especiais" in update_data:
            if update_data["necessidades_especiais"] and "necessidades_descricao" not in update_data:
                # Verificar se já tem descrição
                current = supabase.table("alunos")\
                    .select("necessidades_descricao")\
                    .eq("id", str(aluno_id))\
                    .single()\
                    .execute()
                    
                if not current.data.get("necessidades_descricao"):
                    raise HTTPException(
                        status_code=400,
                        detail="Descrição das necessidades especiais é obrigatória"
                    )
        
        if "data_nascimento" in update_data:
            if update_data["data_nascimento"] >= date.today():
                raise HTTPException(
                    status_code=400,
                    detail="Data de nascimento não pode ser futura"
                )
        
        # Atualizar
        result = supabase.table("alunos")\
            .update(update_data)\
            .eq("id", str(aluno_id))\
            .execute()
            
        if not result.data:
            raise HTTPException(status_code=404, detail="Aluno não encontrado")
            
        return AlunoResponse(**result.data[0])
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{aluno_id}", response_model=MessageResponse)
async def deletar_aluno(aluno_id: UUID):
    """
    Desativa um aluno (soft delete) e registra data de saída
    """
    try:
        supabase = get_supabase()
        
        # Soft delete com data de saída
        result = supabase.table("alunos")\
            .update({
                "ativo": False,
                "data_saida": date.today().isoformat()
            })\
            .eq("id", str(aluno_id))\
            .execute()
            
        if not result.data:
            raise HTTPException(status_code=404, detail="Aluno não encontrado")
            
        return MessageResponse(message="Aluno desativado com sucesso")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 🚨 ÂNCORA: CRÍTICO - Endpoint específico para listar alunos de uma turma
# Contexto: Endpoint separado para melhor organização e performance
# Dependências: Usado pelo frontend na tela de avaliação
@router.get("/turma/{turma_id}", response_model=List[AlunoResponse])
async def listar_alunos_turma(
    turma_id: UUID,
    apenas_ativos: bool = Query(True, description="Mostrar apenas alunos ativos")
):
    """
    Lista todos os alunos de uma turma específica
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
        
        # Buscar alunos
        query = supabase.table("alunos")\
            .select("*")\
            .eq("turma_id", str(turma_id))
            
        if apenas_ativos:
            query = query.eq("ativo", True)
            
        query = query.order("nome")
        
        result = query.execute()
        
        return [AlunoResponse(**aluno) for aluno in result.data]
        
    except Exception as e:
        if "single" in str(e):
            raise HTTPException(status_code=404, detail="Turma não encontrada")
        raise HTTPException(status_code=500, detail=str(e))