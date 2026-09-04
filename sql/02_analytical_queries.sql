-- ==============================================================================
-- CONSULTAS ANALÍTICAS AVANÇADAS (SQL & DATA WAREHOUSING)
-- PROJETO: FP&A & CONTROLADORIA INDUSTRIAL (BENEFICIAMENTO DE TABACO)
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- 1. DRE GERENCIAL CONSOLIDADA: ORÇADO VS. REALIZADO & ANÁLISE DE VARIÂNCIA
-- ------------------------------------------------------------------------------
-- Consolida o resultado anual por nível contábil da DRE, calculando o desvio nominal e percentual.
WITH Realizado_Agrupado AS (
    SELECT 
        AnoMes / 100 AS Ano,
        ID_Conta,
        SUM(Valor_Realizado) AS Total_Realizado
    FROM Fatos_Lancamentos_Realizados
    GROUP BY AnoMes / 100, ID_Conta
),
Orcado_Agrupado AS (
    SELECT 
        Ano,
        ID_Conta,
        SUM(Valor_Orcado) AS Total_Orcado
    FROM Fatos_Orcamento_Planejado
    GROUP BY Ano, ID_Conta
)
SELECT 
    d.Ordem_DRE,
    d.Nivel1,
    d.Nivel2,
    d.Nome_Conta,
    COALESCE(o.Ano, r.Ano) AS Ano_Fiscal,
    COALESCE(o.Total_Orcado, 0.0) AS Orcado,
    COALESCE(r.Total_Realizado, 0.0) AS Realizado,
    COALESCE(r.Total_Realizado, 0.0) - COALESCE(o.Total_Orcado, 0.0) AS Variancia_Nominal,
    ROUND(
        ((COALESCE(r.Total_Realizado, 0.0) - COALESCE(o.Total_Orcado, 0.0)) / NULLIF(o.Total_Orcado, 0)) * 100.0, 
        2
    ) AS Variancia_Percentual,
    CASE 
        WHEN d.Natureza = 'Credito' AND (COALESCE(r.Total_Realizado, 0) >= COALESCE(o.Total_Orcado, 0)) THEN 'FAVORAVEL'
        WHEN d.Natureza = 'Debito' AND (COALESCE(r.Total_Realizado, 0) <= COALESCE(o.Total_Orcado, 0)) THEN 'FAVORAVEL'
        ELSE 'DESFAVORAVEL'
    END AS Status_Desvio
FROM Dim_PlanoContas d
LEFT JOIN Orcado_Agrupado o ON d.ID_Conta = o.ID_Conta
LEFT JOIN Realizado_Agrupado r ON d.ID_Conta = r.ID_Conta AND o.Ano = r.Ano
ORDER BY Ano_Fiscal, d.Ordem_DRE;

-- ------------------------------------------------------------------------------
-- 2. ACUMULADO NO ANO (YTD) & ANÁLISE SEQUENCIAL (WINDOW FUNCTIONS)
-- ------------------------------------------------------------------------------
-- Demonstra a evolução mês a mês do CPV Industrial acumulado (YTD) vs. Orçamento YTD.
WITH Mensal_CPV AS (
    SELECT 
        c.Ano,
        c.Mes,
        c.AnoMes,
        SUM(f.Valor_Realizado) AS Realizado_Mensal
    FROM Fatos_Lancamentos_Realizados f
    JOIN Dim_PlanoContas p ON f.ID_Conta = p.ID_Conta
    JOIN Dim_Calendario c ON f.Data = c.Data
    WHERE p.Nivel1 = '3. Custo Industrial (CPV)'
    GROUP BY c.Ano, c.Mes, c.AnoMes
),
Mensal_Bgt_CPV AS (
    SELECT 
        Ano,
        Mes,
        AnoMes,
        SUM(Valor_Orcado) AS Orcado_Mensal
    FROM Fatos_Orcamento_Planejado f
    JOIN Dim_PlanoContas p ON f.ID_Conta = p.ID_Conta
    WHERE p.Nivel1 = '3. Custo Industrial (CPV)'
    GROUP BY Ano, Mes, AnoMes
)
SELECT 
    m.Ano,
    m.Mes,
    m.AnoMes,
    m.Realizado_Mensal,
    b.Orcado_Mensal,
    -- Window Function: Soma Acumulada no Ano (YTD)
    SUM(m.Realizado_Mensal) OVER (
        PARTITION BY m.Ano 
        ORDER BY m.Mes 
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS Realizado_YTD,
    SUM(b.Orcado_Mensal) OVER (
        PARTITION BY b.Ano 
        ORDER BY b.Mes 
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS Orcado_YTD,
    -- Window Function: Variação em relação ao Mês Anterior (MoM)
    m.Realizado_Mensal - LAG(m.Realizado_Mensal, 1) OVER (
        PARTITION BY m.Ano 
        ORDER BY m.Mes
    ) AS Variacao_MoM_Realizado
FROM Mensal_CPV m
JOIN Mensal_Bgt_CPV b ON m.AnoMes = b.AnoMes
ORDER BY m.Ano, m.Mes;

-- ------------------------------------------------------------------------------
-- 3. RANKING DE OFENSORES DE CUSTO OPERACIONAL (DENSE_RANK)
-- ------------------------------------------------------------------------------
-- Identifica os centros de custo e contas que apresentaram maior estouro absoluto de orçamento.
WITH Variancia_Contabil AS (
    SELECT 
        cc.Nome_CentroCusto,
        cc.Area_Negocio,
        p.Nome_Conta,
        p.Nivel1,
        SUM(r.Valor_Realizado) AS Total_Real,
        SUM(b.Valor_Orcado) AS Total_Orcado,
        SUM(r.Valor_Realizado) - SUM(b.Valor_Orcado) AS Estouro_Nominal
    FROM Fatos_Lancamentos_Realizados r
    JOIN Fatos_Orcamento_Planejado b ON r.AnoMes = b.AnoMes AND r.ID_Conta = b.ID_Conta AND r.ID_CentroCusto = b.ID_CentroCusto
    JOIN Dim_CentroCusto cc ON r.ID_CentroCusto = cc.ID_CentroCusto
    JOIN Dim_PlanoContas p ON r.ID_Conta = p.ID_Conta
    WHERE p.Natureza = 'Debito' AND r.AnoMes / 100 = 2025
    GROUP BY cc.Nome_CentroCusto, cc.Area_Negocio, p.Nome_Conta, p.Nivel1
)
SELECT 
    DENSE_RANK() OVER (ORDER BY Estouro_Nominal DESC) AS Ranking_Ofensor,
    Nome_CentroCusto,
    Area_Negocio,
    Nome_Conta,
    Nivel1,
    Total_Orcado,
    Total_Real,
    Estouro_Nominal,
    ROUND((Estouro_Nominal / Total_Orcado) * 100.0, 2) AS Desvio_Pct
FROM Variancia_Contabil
WHERE Estouro_Nominal > 0
LIMIT 10;
