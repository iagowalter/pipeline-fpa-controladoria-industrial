-- ==============================================================================
-- SCRIPT DDL: MODELO DIMENSIONAL (STAR SCHEMA - KIMBALL)
-- PROJETO: FP&A & CONTROLADORIA INDUSTRIAL (BENEFICIAMENTO DE TABACO)
-- ==============================================================================

-- 1. Dimensão Plano de Contas Gerencial
DROP TABLE IF EXISTS Dim_PlanoContas;
CREATE TABLE Dim_PlanoContas (
    ID_Conta VARCHAR(20) PRIMARY KEY,
    Nome_Conta VARCHAR(150) NOT NULL,
    Nivel1 VARCHAR(100) NOT NULL,
    Nivel2 VARCHAR(100) NOT NULL,
    Natureza VARCHAR(20) NOT NULL CHECK (Natureza IN ('Debito', 'Credito')),
    Ordem_DRE INTEGER NOT NULL
);

-- 2. Dimensão Centros de Custo Fabris e Corporativos
DROP TABLE IF EXISTS Dim_CentroCusto;
CREATE TABLE Dim_CentroCusto (
    ID_CentroCusto VARCHAR(20) PRIMARY KEY,
    Nome_CentroCusto VARCHAR(150) NOT NULL,
    Tipo_Unidade VARCHAR(50) NOT NULL,
    Area_Negocio VARCHAR(100) NOT NULL
);

-- 3. Dimensão Calendário Fiscal e Safra
DROP TABLE IF EXISTS Dim_Calendario;
CREATE TABLE Dim_Calendario (
    Data DATE PRIMARY KEY,
    Ano INTEGER NOT NULL,
    Mes INTEGER NOT NULL,
    AnoMes INTEGER NOT NULL,
    NomeMes VARCHAR(20) NOT NULL,
    Trimestre INTEGER NOT NULL,
    Semestre INTEGER NOT NULL,
    Safra_Ano VARCHAR(50) NOT NULL
);

-- 4. Fato Orçamento Planejado (Granularidade Mensal)
DROP TABLE IF EXISTS Fatos_Orcamento_Planejado;
CREATE TABLE Fatos_Orcamento_Planejado (
    ID_Orcamento INTEGER PRIMARY KEY AUTOINCREMENT,
    AnoMes INTEGER NOT NULL,
    Ano INTEGER NOT NULL,
    Mes INTEGER NOT NULL,
    ID_Conta VARCHAR(20) NOT NULL,
    ID_CentroCusto VARCHAR(20) NOT NULL,
    Valor_Orcado DECIMAL(18, 2) NOT NULL,
    FOREIGN KEY (ID_Conta) REFERENCES Dim_PlanoContas(ID_Conta),
    FOREIGN KEY (ID_CentroCusto) REFERENCES Dim_CentroCusto(ID_CentroCusto)
);

-- 5. Fato Lançamentos Contábeis Reais (Granularidade Diária / Livro Razão)
DROP TABLE IF EXISTS Fatos_Lancamentos_Realizados;
CREATE TABLE Fatos_Lancamentos_Realizados (
    ID_Lancamento VARCHAR(50) PRIMARY KEY,
    Data DATE NOT NULL,
    AnoMes INTEGER NOT NULL,
    ID_Conta VARCHAR(20) NOT NULL,
    ID_CentroCusto VARCHAR(20) NOT NULL,
    Valor_Realizado DECIMAL(18, 2) NOT NULL,
    Historico_Contabil VARCHAR(255) NOT NULL,
    FOREIGN KEY (Data) REFERENCES Dim_Calendario(Data),
    FOREIGN KEY (ID_Conta) REFERENCES Dim_PlanoContas(ID_Conta),
    FOREIGN KEY (ID_CentroCusto) REFERENCES Dim_CentroCusto(ID_CentroCusto)
);

-- Criação de Índices Analíticos para Otimização de Performance
CREATE INDEX IF NOT EXISTS idx_fatos_real_data ON Fatos_Lancamentos_Realizados(Data);
CREATE INDEX IF NOT EXISTS idx_fatos_real_conta ON Fatos_Lancamentos_Realizados(ID_Conta);
CREATE INDEX IF NOT EXISTS idx_fatos_real_cc ON Fatos_Lancamentos_Realizados(ID_CentroCusto);
CREATE INDEX IF NOT EXISTS idx_fatos_bgt_anomes ON Fatos_Orcamento_Planejado(AnoMes);
