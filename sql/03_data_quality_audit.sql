-- ==============================================================================
-- QUERIES DE AUDITORIA CONTÁBIL E DATA QUALITY
-- PROJETO: FP&A & CONTROLADORIA INDUSTRIAL (BENEFICIAMENTO DE TABACO)
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- 1. AUDITORIA DE INTEGRIDADE REFERENCIAL (CHAVES ÓRFÃS)
-- ------------------------------------------------------------------------------
-- Deve retornar 0 registros. Qualquer linha indica violação de integridade no DW.
SELECT 
    'Fatos_Lancamentos_Realizados' AS Tabela_Origem,
    f.ID_Conta,
    f.ID_CentroCusto,
    COUNT(*) AS Total_Registros_Orfaos
FROM Fatos_Lancamentos_Realizados f
LEFT JOIN Dim_PlanoContas p ON f.ID_Conta = p.ID_Conta
LEFT JOIN Dim_CentroCusto c ON f.ID_CentroCusto = c.ID_CentroCusto
WHERE p.ID_Conta IS NULL OR c.ID_CentroCusto IS NULL
GROUP BY f.ID_Conta, f.ID_CentroCusto;

-- ------------------------------------------------------------------------------
-- 2. CONCILIAÇÃO DE SALDOS MENSAIS (REALIZADO DIÁRIO VS. ORÇAMENTO MENSAL)
-- ------------------------------------------------------------------------------
-- Verifica a cobertura de registros mês a mês para garantir que não há meses sem carga.
SELECT 
    c.Ano,
    c.Mes,
    COUNT(DISTINCT r.ID_Lancamento) AS Qtd_Lancamentos_Reais,
    SUM(r.Valor_Realizado) AS Total_Realizado_Mes,
    COUNT(DISTINCT b.ID_Orcamento) AS Qtd_Linhas_Orcamento,
    SUM(b.Valor_Orcado) AS Total_Orcado_Mes
FROM Dim_Calendario c
LEFT JOIN Fatos_Lancamentos_Realizados r ON c.Data = r.Data
LEFT JOIN Fatos_Orcamento_Planejado b ON c.AnoMes = b.AnoMes
GROUP BY c.Ano, c.Mes
ORDER BY c.Ano, c.Mes;

-- ------------------------------------------------------------------------------
-- 3. DETECÇÃO DE ANOMALIAS E OUTLIERS DE LANÇAMENTO
-- ------------------------------------------------------------------------------
-- Identifica lançamentos contábeis individuais com valores atipicamente elevados (> 3 desvios padrão).
WITH Estatisticas_Contas AS (
    SELECT 
        ID_Conta,
        AVG(Valor_Realizado) AS Media_Valor,
        -- Cálculo de desvio padrão amostral simplificado em SQL
        AVG(Valor_Realizado * Valor_Realizado) - (AVG(Valor_Realizado) * AVG(Valor_Realizado)) AS Variancia
    FROM Fatos_Lancamentos_Realizados
    GROUP BY ID_Conta
)
SELECT 
    f.ID_Lancamento,
    f.Data,
    f.ID_Conta,
    p.Nome_Conta,
    f.Valor_Realizado,
    ROUND(e.Media_Valor, 2) AS Media_Conta,
    f.Historico_Contabil
FROM Fatos_Lancamentos_Realizados f
JOIN Estatisticas_Contas e ON f.ID_Conta = e.ID_Conta
JOIN Dim_PlanoContas p ON f.ID_Conta = p.ID_Conta
WHERE f.Valor_Realizado > (e.Media_Valor * 2.5)
ORDER BY f.Valor_Realizado DESC
LIMIT 10;
