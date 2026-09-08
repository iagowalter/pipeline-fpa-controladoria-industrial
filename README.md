# Controladoria Industrial & FP&A: Gestão Orçamentária e DRE Gerencial

> **Nota do Projeto:** Estudo de caso prático de Controladoria Industrial e Planejamento e Controle Financeiro (FP&A) modelado sobre as particularidades operacionais de processamento e exportação de tabaco em folha (*Leaf Merchant*) no Polo Industrial de Venâncio Aires - RS (Alliance One Brasil). Os dados são 100% sintéticos, parametrizados e calibrados para refletir a sazonalidade de safra sul-brasileira, a estrutura de centros de custo fabris e a dinâmica cambial e tributária de exportação, em conformidade com as diretrizes de governança e LGPD.

Este projeto entrega uma solução *end-to-end* de Business Intelligence e Engenharia de Dados: desde a geração parametrizada de lançamentos diários e orçamentários, esteira ETL com motor de rateio de custos corporativos indiretos em Python, modelagem dimensional em Star Schema (*Ralph Kimball*) no SQLite Data Warehouse, até a camada analítica semântica com 26 medidas DAX e painel executivo de 3 visões no Power BI Service.

---

## Acesso ao Dashboard

🔗 **[Acessar o Relatório Interativo no Power BI Service](https://app.powerbi.com/view?r=eyJrIjoiMmVhYjVhZGEtYzQ3Mi00MTE5LWE4YmYtNzMwZjIyYzI1MDNlIiwidCI6ImRmN2Q2NTBkLWMyNmMtNDVhOC1hYjZhLTQwNTNhOGRhNDk5MCJ9)**

---

## Objetivo e Contexto de Negócio

No agronegócio exportador de tabaco, as companhias processadoras (*Leaf Merchants*) compram fumo cru em folha de milhares de produtores rurais integrados nos estados do Rio Grande do Sul, Santa Catarina e Paraná durante o primeiro quadrimestre do ano. O beneficiamento mecânico em linhas de debulha (*Threshing Lines*) e secadores contínuos (*Redryers*) ocorre em ritmo ininterrupto entre março e julho, enquanto os embarques de exportação concentram-se no Porto de Rio Grande (RS) de maio a novembro.

Gerenciar o fluxo financeiro e os desvios de custo (*Variances*) nesse ambiente exige um controle rigoroso de FP&A entre o Orçado e o Realizado. O painel responde diretamente às seguintes perguntas estratégicas da diretoria e dos gestores industriais:

* **Desempenho da DRE e EBITDA:** Como o Lucro Bruto, EBITDA e Lucro Líquido reais estão performando frente ao orçamento anual e em relação ao mesmo período do ano anterior (YoY)?
* **Variação YTD (Year-to-Date):** O desvio acumulado no ano fiscal é decorrente de atraso no cronograma de embarques ou aumento real de custos de produção?
* **Ofensores de Custos Fabris:** Quais etapas do processamento (Recepção, Debulha, Secadores, Embalagem C-48 ou Manutenção/Vapor) apresentam maior estouro de orçamento?
* **Rateio de Estrutura:** Como os custos administrativos e de TI da Sede Corporativa afetam o custo unitário das linhas fabris de Venâncio Aires após a absorção contábil?
* **Impacto Cambial e Fretes:** Como as oscilações cambiais (USD/BRL) e as despesas com frete rodoviário até o porto impactaram a margem de contribuição da safra?

---

## Estrutura do Relatório

O relatório interativo foi estruturado em três visões analíticas complementares:

### 1. Cockpit Executivo & EBITDA
Visão macro voltada à Diretoria Financeira e Presidência, com indicadores consolidados de Receita Bruta, Receita Líquida, Margem Bruta, Margem EBITDA e Lucro Líquido, acompanhados de gráficos de cascata (*Waterfall*) de desvios orçamentários e tendência temporal da safra.

![Cockpit Executivo & EBITDA](img/tela1_cockpit_fpa.png)

* **Principais análises:**
  * Indicadores de topo com comparação simultânea Realizado vs. Orçado vs. Ano Anterior (YoY).
  * Waterfall de variância explicando a ponte de desvio entre o EBITDA Orçado e o EBITDA Realizado.
  * Curva de faturamento mensal e evolução do volume de exportação por safra.

---

### 2. DRE Gerencial Contábil (Full-Height)
Demonstrativo de Resultados do Exercício estruturado em matriz contábil analítica multinível, respeitando a hierarquia financeira padrão (*Plano de Contas Contábil e Gerencial*).

![DRE Gerencial Contábil](img/tela2_dre_gerencial.png)

* **Principais análises:**
  * Abertura completa de Receita Bruta, Deduções, CPV Industrial, OPEX, Depreciação, Resultado Financeiro e Lucro Líquido.
  * Colunas de controle: Realizado, Orçado, Desvio Nominal (R$), Desvio Percentual (%), Realizado YTD, Orçado YTD, Desvio YTD (R$), Desvio YTD (%), Realizado LY e Crescimento YoY (%).
  * Formatação condicional inteligente baseada na natureza das contas contábeis (Crédito vs. Débito).

---

### 3. Custos Fabris & Centros de Custo (Polo Venâncio Aires)
Visão operacional focada na Gerência Industrial e Controladoria de Fábrica, permitindo o diagnóstico minucioso de cada linha produtiva e etapa de suporte.

![Custos Fabris & Centros de Custo](img/tela3_custos_fabris.png)

* **Principais análises:**
  * Matriz de desvios por centro de custo (Classificação, Debulha, Secadores, Prensagem C-48, Caldeiras a Biomassa, Fretes Porto e Agronomia).
  * Ranking dos principais ofensores orçamentários (linhas com maior desvio desfavorável).
  * Avaliação do impacto do rateio de despesas corporativas sobre a operação fabril.

---

## Arquitetura da Solução

```mermaid
flowchart TD
    subgraph Ingestao ["1. Ingestão de Dados (Bronze)"]
        A1["ERP Industrial & Lançamentos Contábeis (GL Diário)"]
        A2["Planejamento Orçamentário Anual (FP&A / Safra)"]
    end

    subgraph Processamento ["2. Engenharia, Rateio & DataOps (Silver)"]
        B1["ETL Python (Sanitização, Tipagem e Formatação)"]
        B2["Motor de Rateio Contábil de Custos Corporativos (60% Fábrica)"]
        B3["Suíte de Testes Automatizados de Data Quality"]
        B4["Esteira de Logs em /logs/pipeline_fpa.log"]
    end

    subgraph Armazenamento ["3. Data Warehouse Relacional (Gold)"]
        C1[("SQLite DW: fpa_industrial_dw.db")]
        C2["Dim_PlanoContas (Hierarquia DRE e Natureza)"]
        C3["Dim_CentroCusto (Polo Venâncio Aires, Campo e Sede)"]
        C4["Dim_Calendario (Safras 2024 a 2026)"]
        C5["Fatos_Orcamento_Planejado"]
        C6["Fatos_Lancamentos_Realizados"]
    end

    subgraph Consumo ["4. Camada Semântica & Analytics (BI)"]
        D1["Consultas SQL Analíticas (Window Functions, YTD e YoY)"]
        D2["Modelo Semântico Power BI (Star Schema & 26 Medidas DAX)"]
        D3["Dashboard Interativo Publicado no Power BI Service"]
    end

    A1 --> B1
    A2 --> B1
    B1 --> B2
    B2 --> B3
    B3 --> B4
    B3 --> C1
    C1 --> C2 & C3 & C4 & C5 & C6
    C1 --> D1
    C1 --> D2
    D2 --> D3
```

---

## Modelagem Dimensional (Star Schema)

A modelagem segue rigorosamente a metodologia *Kimball*, estruturada em Esquema Estrela puro com relacionamentos unidirecionais `1:N` a partir das dimensões para as tabelas fato, eliminando tabelas de relacionamento bidirecional e desativando a inteligência de tempo automática.

```mermaid
erDiagram
    Dim_Calendario ||--o{ Fatos_Lancamentos_Realizados : "Data (1:N)"
    Dim_Calendario ||--o{ Fatos_Orcamento_Planejado : "Data (1:N)"
    Dim_PlanoContas ||--o{ Fatos_Lancamentos_Realizados : "ID_Conta (1:N)"
    Dim_PlanoContas ||--o{ Fatos_Orcamento_Planejado : "ID_Conta (1:N)"
    Dim_CentroCusto ||--o{ Fatos_Lancamentos_Realizados : "ID_CentroCusto (1:N)"
    Dim_CentroCusto ||--o{ Fatos_Orcamento_Planejado : "ID_CentroCusto (1:N)"

    Dim_PlanoContas {
        string ID_Conta PK
        string Nome_Conta
        string Nivel1
        string Nivel2
        string Natureza
        int Ordem_DRE
    }

    Dim_CentroCusto {
        string ID_CentroCusto PK
        string Nome_CentroCusto
        string Tipo_Unidade
        string Area_Negocio
    }

    Dim_Calendario {
        date Data PK
        int Ano
        int Mes
        int AnoMes
        string NomeMes
        int Trimestre
        string Safra_Ano
    }

    Fatos_Lancamentos_Realizados {
        string ID_Lancamento PK
        date Data FK
        int AnoMes
        string ID_Conta FK
        string ID_CentroCusto FK
        decimal Valor_Realizado
        string Historico_Contabil
    }

    Fatos_Orcamento_Planejado {
        int ID_Orcamento PK
        date Data FK
        int AnoMes
        int Ano
        int Mes
        string ID_Conta FK
        string ID_CentroCusto FK
        decimal Valor_Orcado
    }
```

---

## Engenharia de Métricas DAX

As medidas foram centralizadas na tabela `_Medidas` e organizadas em Display Folders especializadas:

* **`01. Realizado & Orcado`**: Cálculos de Realizado, Orçado, Realizado LY, Orçado LY, YTD Real, YTD Orçado e LY YTD.
* **`02. Variancia & Desvios`**: Variações nominais e percentuais mês a mês e acumuladas no ano (`[Desvio Orcado R$]`, `[Desvio Orcado %]`, `[Desvio YTD R$]`, `[Desvio YTD %]`, `[Crescimento YoY R$]`, `[Crescimento YoY %]`).
* **`03. DRE & Indicadores de Resultado`**: Cálculos estruturados por agregação hierárquica e cálculo de margens (`[Receita Liquida Real]`, `[Margem Bruta % Real]`, `[EBITDA Real]`, `[Margem EBITDA % Real]`, `[Lucro Liquido Real]`).
* **`04. Auxiliares & Formatacao`**: Regras de formatação condicional hexadecimal considerando a natureza contábil da conta (Crédito vs. Débito) e tratamento de subtotais.

---

## Como Executar o Pipeline

```bash
# 1. Instalar as dependências do ambiente Python
pip install pandas numpy

# 2. Executar o gerador de dados sintéticos e o pipeline ETL
python src/etl_pipeline.py

# 3. Executar a suíte de auditoria e qualidade de dados
python src/data_quality.py
```

---

Para consultar o dicionário detalhado de campos, catálogo completo das medidas DAX e regras contábeis, acesse a [DOCUMENTACAO.md](DOCUMENTACAO.md).

---

## Autor

**Iago Walter**  
Engenheiro de Produção | Business Intelligence & Análise de Dados  
Santa Cruz do Sul / Vera Cruz — RS  
[LinkedIn](https://www.linkedin.com/in/iago-walter/) | [GitHub](https://github.com/iagowalter)
