"""
Script para popular o banco de dados com dados de teste
Colégio Solare - Sistema de Avaliação
"""

import asyncio
from datetime import date, datetime
from uuid import uuid4
import os
import sys
from pathlib import Path

# Adiciona o diretório pai ao path para importar os módulos
sys.path.append(str(Path(__file__).parent.parent))

from app.models.database import get_supabase
from app.config import get_settings

# Cores para output no terminal
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}✓ {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.BLUE}→ {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}✗ {msg}{Colors.END}")

async def seed_database():
    """Popula o banco com dados de teste"""
    
    print_info("Iniciando população do banco de dados...")
    supabase = get_supabase()
    
    try:
        # 1. Criar Escola (se usar multi-tenant no futuro)
        print_info("Criando escola...")
        escola_data = {
            "nome": "Colégio Solare - Unidade Teste"
        }
        escola_result = supabase.table("escolas").insert(escola_data).execute()
        escola_id = escola_result.data[0]['id'] if escola_result.data else None
        print_success(f"Escola criada: {escola_data['nome']}")
        
        # 2. Criar Usuários (Professores)
        print_info("Criando professores...")
        professores = [
            {
                "email": "michelle.vilas@solare.edu.br",
                "nome": "Michelle Vilas Boas",
                "senha_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNiGH7V4rGYma",  # senha: 123456
                "tipo": "professor",
                "telefone": "(11) 98765-4321",
                "escola_id": escola_id,
                "ativo": True
            },
            {
                "email": "giovanna.lima@solare.edu.br", 
                "nome": "Giovanna Lima",
                "senha_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNiGH7V4rGYma",
                "tipo": "professor",
                "telefone": "(11) 98765-4322",
                "escola_id": escola_id,
                "ativo": True
            },
            {
                "email": "marcia.mello@solare.edu.br",
                "nome": "Márcia Mello", 
                "senha_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNiGH7V4rGYma",
                "tipo": "coordenador",
                "telefone": "(11) 98765-4320",
                "escola_id": escola_id,
                "ativo": True
            }
        ]
        
        professores_ids = {}
        for prof in professores:
            result = supabase.table("usuarios").insert(prof).execute()
            if result.data:
                professores_ids[prof['nome']] = result.data[0]['id']
                print_success(f"Professor(a) criado(a): {prof['nome']}")
        
        # Atualizar coordenador_id para o coordenador
        coordenador_id = professores_ids.get("Márcia Mello")
        if coordenador_id:
            for nome, prof_id in professores_ids.items():
                if "Professor" in nome or nome == "Michelle Vilas Boas" or nome == "Giovanna Lima":
                    # Atualiza o professor para ter coordenador
                    supabase.table("usuarios").update({
                        "coordenador_id": coordenador_id
                    }).eq("id", prof_id).execute()
                    print_success(f"Professor {nome} vinculado ao coordenador")

        # 3. Criar Turmas
        print_info("Criando turmas...")
        turmas = [
            {
                "serie": "1º Ano",
                "turma": "A", 
                "ano_letivo": 2025,
                "periodo": "manha",
                "nivel": "fundamental",
                "capacidade_maxima": 30,
                "professor_id": professores_ids.get("Michelle Vilas Boas"),
                "escola_id": escola_id,
                "ativo": True
            },
            {
                "serie": "1º Ano",
                "turma": "B",
                "ano_letivo": 2025, 
                "periodo": "tarde",
                "nivel": "fundamental",
                "capacidade_maxima": 30,
                "professor_id": professores_ids.get("Michelle Vilas Boas"),
                "escola_id": escola_id,
                "ativo": True
            },
            {
                "serie": "Infantil II",
                "turma": "Manhã",
                "ano_letivo": 2025,
                "periodo": "manha", 
                "nivel": "infantil",
                "capacidade_maxima": 25,
                "professor_id": professores_ids.get("Giovanna Lima"),
                "escola_id": escola_id,
                "ativo": True
            },
            {
                "serie": "Infantil II",
                "turma": "Tarde",
                "ano_letivo": 2025,
                "periodo": "tarde",
                "nivel": "infantil", 
                "capacidade_maxima": 25,
                "professor_id": professores_ids.get("Giovanna Lima"),
                "escola_id": escola_id,
                "ativo": True
            }
        ]
        
        turmas_ids = {}
        for turma in turmas:
            result = supabase.table("turmas").insert(turma).execute()
            if result.data:
                turma_key = f"{turma['serie']} {turma['turma']}"
                turmas_ids[turma_key] = result.data[0]['id']
                print_success(f"Turma criada: {turma_key}")
        
        # 4. Criar Alunos
        print_info("Criando alunos...")
        
        # Nomes comuns para gerar alunos
        nomes_meninos = ["João", "Pedro", "Lucas", "Gabriel", "Rafael", "Miguel", "Davi", "Arthur", "Bernardo", "Heitor"]
        nomes_meninas = ["Maria", "Ana", "Julia", "Luiza", "Sophia", "Isabella", "Helena", "Valentina", "Laura", "Alice"]
        sobrenomes = ["Silva", "Santos", "Oliveira", "Souza", "Lima", "Pereira", "Costa", "Rodrigues", "Almeida", "Ferreira"]
        
        alunos_criados = 0
        
        # Para cada turma, criar alunos
        for turma_nome, turma_id in turmas_ids.items():
            # Determinar quantos alunos criar (entre 20-28)
            import random
            num_alunos = random.randint(20, 28)
            
            for i in range(num_alunos):
                # Alternar entre meninos e meninas
                if i % 2 == 0:
                    nome = random.choice(nomes_meninos)
                else:
                    nome = random.choice(nomes_meninas)
                
                sobrenome = random.choice(sobrenomes)
                nome_completo = f"{nome} {sobrenome}"
                
                # Determinar idade baseado na série
                if "Infantil" in turma_nome:
                    idade = 4
                    ano_nascimento = 2021
                else:  # 1º Ano
                    idade = 6
                    ano_nascimento = 2019
                
                aluno = {
                    "matricula": f"2025{str(alunos_criados + 1).zfill(4)}",
                    "nome": nome_completo,
                    "data_nascimento": f"{ano_nascimento}-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
                    "turma_id": turma_id,
                    "responsavel_nome": f"Responsável de {nome}",
                    "responsavel_telefone": f"(11) 9{random.randint(1000,9999)}-{random.randint(1000,9999)}",
                    "responsavel_email": f"responsavel.{nome.lower()}{alunos_criados}@email.com",
                    "necessidades_especiais": random.choice([False, False, False, False, True]),  # 20% chance
                    "ativo": True
                }
                
                # Se tem necessidades especiais, adicionar descrição
                if aluno["necessidades_especiais"]:
                    aluno["necessidades_descricao"] = random.choice([
                        "TDAH - Necessita de atenção individualizada",
                        "Dislexia - Em acompanhamento",
                        "TEA nível 1 - Precisa de rotina estruturada",
                        "Dificuldade motora fina"
                    ])
                
                # Adicionar alergias aleatoriamente (10% chance)
                if random.random() < 0.1:
                    aluno["alergias"] = random.choice(["Lactose", "Glúten", "Amendoim", "Corante"])
                
                result = supabase.table("alunos").insert(aluno).execute()
                if result.data:
                    alunos_criados += 1
            
            print_success(f"Criados {num_alunos} alunos para {turma_nome}")
        
        # 5. Criar Tags padrão
        print_info("Criando tags comportamentais...")
        tags_padrao = [
            # Tags positivas
            {"nome": "Participativo", "tipo": "positiva", "categoria": "Comportamento", "cor": "#10b981"},
            {"nome": "Colaborativo", "tipo": "positiva", "categoria": "Comportamento", "cor": "#10b981"},
            {"nome": "Criativo", "tipo": "positiva", "categoria": "Aprendizagem", "cor": "#10b981"},
            {"nome": "Organizado", "tipo": "positiva", "categoria": "Organização", "cor": "#10b981"},
            {"nome": "Líder", "tipo": "positiva", "categoria": "Social", "cor": "#10b981"},
            
            # Tags neutras
            {"nome": "Tímido", "tipo": "neutra", "categoria": "Comportamento", "cor": "#6b7280"},
            {"nome": "Agitado", "tipo": "neutra", "categoria": "Comportamento", "cor": "#6b7280"},
            {"nome": "Disperso", "tipo": "neutra", "categoria": "Atenção", "cor": "#6b7280"},
            
            # Tags negativas
            {"nome": "Dificuldade de concentração", "tipo": "negativa", "categoria": "Atenção", "cor": "#ef4444"},
            {"nome": "Conflitos com colegas", "tipo": "negativa", "categoria": "Social", "cor": "#ef4444"},
        ]
        
        for tag in tags_padrao:
            # Criar para cada professor
            for prof_nome, prof_id in professores_ids.items():
                if "Professor" not in prof_nome:  # Só para professores, não coordenadores
                    tag_copy = tag.copy()
                    tag_copy["usuario_id"] = prof_id
                    supabase.table("tags").insert(tag_copy).execute()
        
        print_success("Tags comportamentais criadas")
        
        # Resumo final
        print("\n" + "="*50)
        print_success("✨ Banco de dados populado com sucesso!")
        print(f"\n📊 Resumo:")
        print(f"   - 1 Escola")
        print(f"   - {len(professores)} Usuários (2 professores, 1 coordenador)")
        print(f"   - {len(turmas)} Turmas")
        print(f"   - {alunos_criados} Alunos")
        print(f"   - {len(tags_padrao) * 2} Tags comportamentais")
        print("\n🔑 Credenciais de teste:")
        print("   Email: michelle.vilas@solare.edu.br")
        print("   Senha: 123456")
        print("="*50)
        
    except Exception as e:
        print_error(f"Erro ao popular banco: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(seed_database())