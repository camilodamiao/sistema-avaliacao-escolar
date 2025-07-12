"""
🚨 ÂNCORA: CRÍTICO - Conexão com banco de dados
Contexto: Gerencia conexão única com Supabase
Cuidado: Todas as operações de banco passam por aqui
Dependências: Todos os services dependem desta conexão
"""

from supabase import create_client, Client
from app.config import get_settings
from typing import Optional

# Instância global do cliente Supabase
_supabase_client: Optional[Client] = None


def get_supabase() -> Client:
    """
    Retorna cliente Supabase (Singleton)
    Cria apenas uma conexão e reutiliza
    """
    global _supabase_client
    
    if _supabase_client is None:
        settings = get_settings()
        _supabase_client = create_client(
            settings.supabase_url,
            settings.supabase_key
        )
        print("✅ Conexão com Supabase estabelecida")
    
    return _supabase_client


# 🚨 ÂNCORA: CRÍTICO - Script SQL para criar tabelas
# Contexto: Execute este SQL no Supabase para criar a estrutura
# Cuidado: Ordem importa devido às foreign keys
# Atualizado: 11/07/2025 - Incluindo todos os novos campos aprovados

SQL_CREATE_TABLES = """
-- Configurar timezone para Brasília
SET timezone = 'America/Sao_Paulo';

-- Tabela de escolas (para futuro multi-tenant)
CREATE TABLE IF NOT EXISTS escolas (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de professores/usuários
CREATE TABLE IF NOT EXISTS usuarios (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    nome VARCHAR(255) NOT NULL,
    senha_hash VARCHAR(255) NOT NULL,
    telefone VARCHAR(20),  -- NOVO: telefone opcional
    tipo VARCHAR(50) CHECK (tipo IN ('professor', 'coordenador', 'admin')) DEFAULT 'professor',
    escola_id UUID REFERENCES escolas(id),
    coordenador_id UUID REFERENCES usuarios(id)
    ativo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de turmas
CREATE TABLE IF NOT EXISTS turmas (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    serie VARCHAR(50) NOT NULL,  -- ALTERADO: "1º Ano", "Infantil II"
    turma VARCHAR(10) NOT NULL,   -- ALTERADO: "A", "B", "C"
    ano_letivo INTEGER NOT NULL DEFAULT EXTRACT(YEAR FROM CURRENT_DATE),  -- NOVO
    periodo VARCHAR(20) CHECK (periodo IN ('manha', 'tarde', 'integral')),
    nivel VARCHAR(20) CHECK (nivel IN ('infantil', 'fundamental')) NOT NULL,
    capacidade_maxima INTEGER,  -- NOVO: limite de alunos
    professor_id UUID REFERENCES usuarios(id),
    escola_id UUID REFERENCES escolas(id),
    ativo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(serie, turma, ano_letivo, periodo)  -- Evita duplicar turmas
);

-- Tabela de alunos
CREATE TABLE IF NOT EXISTS alunos (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    matricula VARCHAR(50) UNIQUE NOT NULL,  -- NOVO: matrícula única
    nome VARCHAR(255) NOT NULL,
    data_nascimento DATE NOT NULL,
    foto_url VARCHAR(500),  -- NOVO: foto do aluno
    turma_id UUID REFERENCES turmas(id),
    
    -- Dados do responsável
    responsavel_nome VARCHAR(255),
    responsavel_telefone VARCHAR(20),
    responsavel_email VARCHAR(255),
    responsavel_foto_url VARCHAR(500),  -- NOVO: foto do responsável
    
    -- Necessidades especiais e restrições
    necessidades_especiais BOOLEAN DEFAULT FALSE,  -- NOVO
    necessidades_descricao TEXT,  -- NOVO
    alergias TEXT,  -- NOVO
    restricoes_alimentares TEXT,  -- NOVO
    
    -- Controle
    observacoes TEXT,
    ativo BOOLEAN DEFAULT TRUE,
    data_saida DATE,  -- NOVO: quando deixou a escola
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de tags comportamentais
CREATE TABLE IF NOT EXISTS tags (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    tipo VARCHAR(20) CHECK (tipo IN ('positiva', 'negativa', 'neutra')) DEFAULT 'neutra',  -- NOVO
    categoria VARCHAR(50),
    cor VARCHAR(7) DEFAULT '#0066cc',
    nivel_ensino VARCHAR(20) CHECK (nivel_ensino IN ('infantil', 'fundamental', 'ambos')) DEFAULT 'ambos',  -- NOVO
    usuario_id UUID REFERENCES usuarios(id),  -- ALTERADO: tags por professor
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(nome, usuario_id)  -- Evita duplicar tags do mesmo professor
);

-- Tabela de avaliações diárias
CREATE TABLE IF NOT EXISTS avaliacoes (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    aluno_id UUID REFERENCES alunos(id) NOT NULL,
    data_avaliacao DATE NOT NULL,
    trimestre INTEGER CHECK (trimestre IN (1, 2, 3)) NOT NULL,
    ano INTEGER NOT NULL,
    status VARCHAR(20) CHECK (status IN ('rascunho', 'concluida')) DEFAULT 'rascunho',  -- NOVO
    campos_avaliados JSONB NOT NULL,
    observacao_livre TEXT,
    professor_id UUID REFERENCES usuarios(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(aluno_id, data_avaliacao)
);

-- Tabela de relação avaliação-tags (muitos para muitos)
CREATE TABLE IF NOT EXISTS avaliacao_tags (
    avaliacao_id UUID REFERENCES avaliacoes(id) ON DELETE CASCADE,
    tag_id UUID REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (avaliacao_id, tag_id)
);

-- Tabela de relatórios trimestrais
CREATE TABLE IF NOT EXISTS relatorios (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    aluno_id UUID REFERENCES alunos(id) NOT NULL,
    trimestre INTEGER CHECK (trimestre IN (1, 2, 3)) NOT NULL,
    ano INTEGER NOT NULL,
    texto_final TEXT NOT NULL,  -- ALTERADO: apenas versão final
    historico_revisoes JSONB DEFAULT '[]'::jsonb,  -- NOVO: array de revisões
    dados_consolidados JSONB NOT NULL,
    status VARCHAR(20) CHECK (status IN ('rascunho', 'revisao', 'aprovado')) DEFAULT 'rascunho',
    pdf_url VARCHAR(500),  -- NOVO: link do PDF
    enviado_em TIMESTAMP WITH TIME ZONE,  -- NOVO
    enviado_por VARCHAR(20) CHECK (enviado_por IN ('email', 'whatsapp', 'api')),  -- NOVO
    professor_id UUID REFERENCES usuarios(id),
    coordenador_id UUID REFERENCES usuarios(id),
    aprovado_em TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(aluno_id, trimestre, ano)
);

-- Índices para performance
CREATE INDEX idx_avaliacoes_aluno_data ON avaliacoes(aluno_id, data_avaliacao);
CREATE INDEX idx_avaliacoes_trimestre ON avaliacoes(trimestre, ano);
CREATE INDEX idx_alunos_turma ON alunos(turma_id);
CREATE INDEX idx_turmas_professor ON turmas(professor_id);
CREATE INDEX idx_tags_usuario ON tags(usuario_id);
CREATE INDEX idx_alunos_necessidades ON alunos(necessidades_especiais) WHERE necessidades_especiais = TRUE;

-- Triggers para updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_escolas_updated_at BEFORE UPDATE ON escolas FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_usuarios_updated_at BEFORE UPDATE ON usuarios FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_turmas_updated_at BEFORE UPDATE ON turmas FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_alunos_updated_at BEFORE UPDATE ON alunos FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_avaliacoes_updated_at BEFORE UPDATE ON avaliacoes FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_relatorios_updated_at BEFORE UPDATE ON relatorios FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Comentários nas tabelas para documentação
COMMENT ON TABLE escolas IS 'Tabela de escolas para futuro multi-tenant';
COMMENT ON TABLE usuarios IS 'Professores, coordenadores e administradores do sistema';
COMMENT ON TABLE turmas IS 'Turmas/classes com série, turma e capacidade';
COMMENT ON TABLE alunos IS 'Dados completos dos alunos incluindo necessidades especiais';
COMMENT ON TABLE tags IS 'Tags comportamentais personalizadas por professor';
COMMENT ON TABLE avaliacoes IS 'Avaliações diárias com status de rascunho/concluída';
COMMENT ON TABLE relatorios IS 'Relatórios trimestrais com histórico de revisões';

-- Script para deletar todas as tabelas (use com cuidado!)
-- DROP TABLE IF EXISTS avaliacao_tags CASCADE;
-- DROP TABLE IF EXISTS relatorios CASCADE;
-- DROP TABLE IF EXISTS avaliacoes CASCADE;
-- DROP TABLE IF EXISTS tags CASCADE;
-- DROP TABLE IF EXISTS alunos CASCADE;
-- DROP TABLE IF EXISTS turmas CASCADE;
-- DROP TABLE IF EXISTS usuarios CASCADE;
-- DROP TABLE IF EXISTS escolas CASCADE;
-- DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE;
"""