# Documentação Técnica e Governança de Dados: FP&A & Controladoria Industrial

Este documento detalha a arquitetura do Data Warehouse relacional, o modelo dimensional em Esquema Estrela (*Star Schema*), o dicionário completo de dados, as etapas de engenharia e ETL (Python & SQL), o catálogo integral de medidas DAX e as regras contábeis e de governança aplicadas ao estudo de caso da **Alliance One Brasil Exportadora de Tabacos Ltda.** (Polo Venâncio Aires - RS).

---

## 1. Arquitetura do Modelo Dimensional (Star Schema)

A modelagem segue estritamente a metodologia de Ralph Kimball, separando claramente o contexto de negócio (Dimensões) dos eventos transacionais e orçamentários (Fatos).

### Relacionamentos do Modelo Semântico

| Tabela Origem (1) | Tabela Destino (N) | Chave de Relacionamento | Cardinalidade | Direção do Filtro |
| :--- | :--- | :--- | :--- | :--- |
| `Dim_Calendario` | `Fatos_Lancamentos_Realizados` | `Data` | 1:N | Única (Dimensão -> Fato) |
| `Dim_Calendario` | `Fatos_Orcamento_Planejado` | `Data` | 1:N | Única (Dimensão -> Fato) |
| `Dim_PlanoContas` | `Fatos_Lancamentos_Realizados` | `ID_Conta` | 1:N | Única (Dimensão -> Fato) |
| `Dim_PlanoContas` | `Fatos_Orcamento_Planejado` | `ID_Conta` | 1:N | Única (Dimensão -> Fato) |
| `Dim_CentroCusto` | `Fatos_Lancamentos_Realizados` | `ID_CentroCusto` | 1:N | Única (Dimensão -> Fato) |
| `Dim_CentroCusto` | `Fatos_Orcamento_Planejado` | `ID_CentroCusto` | 1:N | Única (Dimensão -> Fato) |

*Nota Técnica:* A inteligência de tempo automática (*Auto Date/Time*) do Power BI foi desativada no arquivo `.pbix`, sendo todo o suporte temporal assegurado pela dimensão dedicada `Dim_Calendario`.

---

## 2. Dicionário de Dados

### 2.1. Tabelas Dimensão

#### `Dim_PlanoContas`
Estrutura hierárquica do Plano de Contas contábil e gerencial, responsável pela renderização ordenada do Demonstrativo de Resultados do Exercício (DRE).

| Campo | Tipo de Dado | Restrição | Descrição e Regra de Negócio |
| :--- | :--- | :--- | :--- |
| `ID_Conta` | VARCHAR(20) | PK | Código estruturado da conta contábil (Ex: `1.01.001`, `3.01.001`). |
| `Nome_Conta` | VARCHAR(150) | NOT NULL | Nomenclatura oficial da conta de resultado. |
| `Nivel1` | VARCHAR(100) | NOT NULL | Agrupador macro da DRE (`1. Receita Bruta`, `3. Custo Industrial (CPV)`, etc.). |
| `Nivel2` | VARCHAR(100) | NOT NULL | Subgrupo analítico da operação (`Processamento Industrial`, `Fretes`). |
| `Natureza` | VARCHAR(20) | NOT NULL | Natureza contábil para tratamento de sinais (`Credito` ou `Debito`). |
| `Ordem_DRE` | INTEGER | NOT NULL | Sequência numérica ordinal para ordenação contábil nativa na matriz. |

#### `Dim_CentroCusto`
Mapeamento dos centros de responsabilidade do Polo Industrial de Venâncio Aires, áreas de fomento agronômico e governança corporativa.

| Campo | Tipo de Dado | Restrição | Descrição e Regra de Negócio |
| :--- | :--- | :--- | :--- |
| `ID_CentroCusto` | VARCHAR(20) | PK | Código identificador do centro de custo (Ex: `CC1001`, `CC2001`). |
| `Nome_CentroCusto` | VARCHAR(150) | NOT NULL | Descrição da linha produtiva ou departamento. |
| `Tipo_Unidade` | VARCHAR(50) | NOT NULL | Classificação da unidade (`Fabrica Venancio Aires`, `Operacional`, `Sede Administrativa`). |
| `Area_Negocio` | VARCHAR(100) | NOT NULL | Macroárea funcional (`Operacoes Fabris`, `Logistica Exportacao`, `Corporativo`). |

#### `Dim_Calendario`
Dimensão temporal contínua cobrindo as safras de 2024 a 2026.

| Campo | Tipo de Dado | Restrição | Descrição e Regra de Negócio |
| :--- | :--- | :--- | :--- |
| `Data` | DATE | PK | Data civil no padrão ISO (`YYYY-MM-DD`). |
| `Ano` | INTEGER | NOT NULL | Ano do exercício civil. |
| `Mes` | INTEGER | NOT NULL | Número do mês (1 a 12). |
| `AnoMes` | INTEGER | NOT NULL | Chave numérica de competência (`YYYYMM`). |
| `NomeMes` | VARCHAR(20) | NOT NULL | Abreviação textual do mês em português (`Jan`, `Fev`, etc.). |
| `Trimestre` | INTEGER | NOT NULL | Trimestre fiscal (1 a 4). |
| `Semestre` | INTEGER | NOT NULL | Semestre civil (1 ou 2). |
| `Safra_Ano` | VARCHAR(50) | NOT NULL | Descritivo da safra agrícola (`Safra 2024`, `Safra 2025`, `Safra 2026`). |

---

### 2.2. Tabelas Fato

#### `Fatos_Lancamentos_Realizados`
Registros diários de lançamentos do razão contábil (General Ledger), abrangendo faturamento, custos de matéria-prima, processamento fabril, fretes e rateios.

| Campo | Tipo de Dado | Restrição | Descrição e Regra de Negócio |
| :--- | :--- | :--- | :--- |
| `ID_Lancamento` | VARCHAR(50) | PK | Identificador exclusivo do documento (`DOC-XXXXXX` ou `RAT-XXXXXX`). |
| `Data` | DATE | FK | Data da ocorrência do fato contábil. |
| `AnoMes` | INTEGER | NOT NULL | Competência mensal associada. |
| `ID_Conta` | VARCHAR(20) | FK | Chave estrangeira ligada à `Dim_PlanoContas`. |
| `ID_CentroCusto` | VARCHAR(20) | FK | Chave estrangeira ligada à `Dim_CentroCusto`. |
| `Valor_Realizado` | DECIMAL(18, 2) | NOT NULL | Valor financeiro realizado em moeda corrente (R$). |
| `Historico_Contabil`| VARCHAR(255) | NOT NULL | Detalhamento da transação para fins de auditoria contábil. |

#### `Fatos_Orcamento_Planejado`
Valores orçados definidos durante a rodada anual de planejamento financeiro (FP&A) por competência mensal, conta e centro de custo.

| Campo | Tipo de Dado | Restrição | Descrição e Regra de Negócio |
| :--- | :--- | :--- | :--- |
| `ID_Orcamento` | INTEGER | PK (Auto) | Chave primária sequencial do planejamento. |
| `Data` | DATE | FK | Data do primeiro dia do mês de competência (`YYYY-MM-01`). |
| `AnoMes` | INTEGER | NOT NULL | Chave inteira de competência (`YYYYMM`). |
| `Ano` | INTEGER | NOT NULL | Ano do exercício orçamentário. |
| `Mes` | INTEGER | NOT NULL | Mês do exercício orçamentário. |
| `ID_Conta` | VARCHAR(20) | FK | Chave estrangeira ligada à `Dim_PlanoContas`. |
| `ID_CentroCusto` | VARCHAR(20) | FK | Chave estrangeira ligada à `Dim_CentroCusto`. |
| `Valor_Orcado` | DECIMAL(18, 2) | NOT NULL | Valor orçado planejado em Reais (R$). |

---

## 3. Etapas de Engenharia de Dados & ETL

O fluxo de dados foi construído com foco em rastreabilidade, modularidade e tratamento de cultura numérica:

1. **Ingestão e Geração Parametrizada (`src/generator.py`):**
   * Calibração da escala de faturamento da Alliance One Brasil (~R$ 840 milhões anuais).
   * Modelagem de curvas de sazonalidade realistas: safra/compra (fev-mai), processamento fabril (mar-jul) e embarques de exportação pelo Porto de Rio Grande (mai-nov).
   * Inclusão do primeiro dia do mês na tabela orçamentária (`Data`), garantindo relacionamento 1:N puro com a dimensão calendário.

2. **Motor de Rateio de Custos Indiretos (`src/etl_pipeline.py`):**
   * Absorção contábil de 60% das despesas corporativas de Gestão (`CC3001`) e TI (`CC3002`) pelas quatro linhas produtivas fabris (`CC1001` a `CC1004` - 15% cada).
   * Criação de lançamentos automáticos de rateio identificados com o prefixo `RAT-`.

3. **Garantia de Qualidade e Conformidade de Dados (`src/data_quality.py`):**
   * Testes automatizados de unicidade de chaves primárias.
   * Validação de integridade referencial entre fatos e dimensões (100% de correspondência).
   * Verificação de valores nulos e limites de datas.

4. **Tratamento no Power Query M:**
   * Exportação dos arquivos CSV utilizando separador de ponto decimal no padrão `en-US` (`CultureInfo.InvariantCulture`), prevenindo a interpretação incorreta de casas decimais em ambientes locais do Windows com configuração regional pt-BR.

---

## 4. Catálogo de Medidas DAX

### 4.1. Pasta de Exibição: `01. Realizado & Orcado`

```dax
[Realizado Total] = 
// Calcula o montante total de lancamentos reais realizados no periodo selecionado
SUM(Fatos_Lancamentos_Realizados[Valor_Realizado])
```

```dax
[Orcado Total] = 
// Calcula o montante total orcado para o periodo selecionado
SUM(Fatos_Orcamento_Planejado[Valor_Orcado])
```

```dax
[Realizado YTD] = 
// Calcula o valor acumulado no ano fiscal ate o periodo atual selecionado
TOTALYTD(
    [Realizado Total],
    Dim_Calendario[Data]
)
```

```dax
[Orcado YTD] = 
// Calcula o orcamento acumulado no ano fiscal ate o periodo atual selecionado
TOTALYTD(
    [Orcado Total],
    Dim_Calendario[Data]
)
```

```dax
[Realizado Ano Anterior (SPLY)] = 
// Calcula o valor realizado no mesmo periodo do ano anterior para analise YoY
CALCULATE(
    [Realizado Total],
    SAMEPERIODLASTYEAR(Dim_Calendario[Data])
)
```

---

### 4.2. Pasta de Exibição: `02. Variancia & Desvios`

```dax
[Desvio Orcado R$] = 
// Calcula a diferenca liquida nominal entre Realizado e Orcado
[Realizado Total] - [Orcado Total]
```

```dax
[Desvio Orcado %] = 
// Calcula a variacao percentual entre Realizado e Orcado
DIVIDE(
    [Desvio Orcado R$],
    [Orcado Total],
    0
)
```

```dax
[Desvio YTD R$] = 
// Calcula o desvio acumulado no ano fiscal
[Realizado YTD] - [Orcado YTD]
```

```dax
[Desvio YTD %] = 
// Variacao percentual acumulada no ano
DIVIDE(
    [Desvio YTD R$],
    [Orcado YTD],
    0
)
```

```dax
[Crescimento YoY R$] = 
// Variacao nominal frente ao mesmo periodo do ano anterior
[Realizado Total] - [Realizado Ano Anterior (SPLY)]
```

```dax
[Crescimento YoY %] = 
// Percentual de crescimento ou retracao frente ao ano anterior
DIVIDE(
    [Crescimento YoY R$],
    [Realizado Ano Anterior (SPLY)],
    0
)
```

---

### 4.3. Pasta de Exibição: `03. DRE & Indicadores de Resultado`

```dax
[Receita Bruta Real] = 
// Soma das receitas brutas totais (Exportacao e Mercado Interno)
CALCULATE(
    [Realizado Total],
    Dim_PlanoContas[Nivel1] = "1. Receita Bruta"
)
```

```dax
[Deducoes Real] = 
// Soma dos impostos e abatimentos comerciais
CALCULATE(
    [Realizado Total],
    Dim_PlanoContas[Nivel1] = "2. Deducoes da Receita"
)
```

```dax
[Receita Liquida Real] = 
// Receita Operacional Liquida
[Receita Bruta Real] - [Deducoes Real]
```

```dax
[CPV Industrial Real] = 
// Custo de compra de folha e processamento fabril em Venancio Aires
CALCULATE(
    [Realizado Total],
    Dim_PlanoContas[Nivel1] = "3. Custo Industrial (CPV)"
)
```

```dax
[Margem Bruta Real] = 
// Lucro Bruto Industrial
[Receita Liquida Real] - [CPV Industrial Real]
```

```dax
[Margem Bruta %] = 
// Percentual de Margem Bruta sobre a Receita Liquida
DIVIDE(
    [Margem Bruta Real],
    [Receita Liquida Real],
    0
)
```

```dax
[OPEX & Logistica Real] = 
// Despesas operacionais com fretes, terminal de Rio Grande, campo (STP) e corporativo
CALCULATE(
    [Realizado Total],
    Dim_PlanoContas[Nivel1] = "4. Despesas Operacionais (OPEX)"
)
```

```dax
[EBITDA Gerencial Real] = 
// Lucro Antes de Juros, Impostos, Depreciacao e Amortizacao
VAR _Depreciacao = 
    CALCULATE(
        [Realizado Total],
        Dim_PlanoContas[ID_Conta] = "3.06.001"
    )
RETURN
    ([Margem Bruta Real] - [OPEX & Logistica Real]) + _Depreciacao
```

```dax
[Margem EBITDA %] = 
// Percentual de Margem EBITDA sobre a Receita Liquida
DIVIDE(
    [EBITDA Gerencial Real],
    [Receita Liquida Real],
    0
)
```

```dax
[Resultado Financeiro & Hedge Real] = 
// Efeito liquido de variacao cambial em USD e rendimentos de tesouraria
VAR _ReceitasFin = 
    CALCULATE(
        [Realizado Total],
        Dim_PlanoContas[ID_Conta] IN {"5.01.001", "5.03.001"}
    )
VAR _DespesasFin = 
    CALCULATE(
        [Realizado Total],
        Dim_PlanoContas[ID_Conta] = "5.02.001"
    )
RETURN
    _ReceitasFin - _DespesasFin
```

---

### 4.4. Pasta de Exibição: `04. Auxiliares & Formatacao`

```dax
[Cor Status Desvio DRE] = 
// Formata condicionalmente as cores da matriz DRE considerando Credito e Debito
VAR _Natureza = SELECTEDVALUE(Dim_PlanoContas[Natureza])
VAR _Desvio = [Desvio Orcado R$]
VAR _Nivel1 = SELECTEDVALUE(Dim_PlanoContas[Nivel1])
RETURN
    SWITCH(
        TRUE(),
        _Natureza = "Credito" && _Desvio >= 0, "#009E49",
        _Natureza = "Credito" && _Desvio < 0, "#E74C3C",
        _Natureza = "Debito" && _Desvio <= 0, "#009E49",
        _Natureza = "Debito" && _Desvio > 0, "#E74C3C",
        _Nivel1 = "5. Resultado Financeiro" && _Desvio >= 0, "#009E49",
        _Nivel1 = "5. Resultado Financeiro" && _Desvio < 0, "#E74C3C",
        "#7F8C8D"
    )
```

---

## 5. Regras de Negócio e Particularidades do Tabaco

1. **Estrutura de Faturamento (*Leaf Merchant*):**
   * O faturamento principal advém da exportação de *Strips Virgínia*, *Strips Burley* e subprodutos (*By-Products* - talas/fumos picados).
   * Imunidade tributária constitucional (CF/88 Art. 149 e Art. 155) sobre exportações diretas (alíquota zero de PIS/COFINS e imunidade de ICMS na saída portuária).

2. **Sazonalidade Fabril e Logística:**
   * A compra de matéria-prima ocorre fortemente no primeiro quadrimestre (fevereiro a maio).
   * As linhas de debulha e secadores operam continuamente entre março e julho.
   * Os embarques de caixas C-48 pelo Porto de Rio Grande (RS) atingem o pico entre maio e novembro.

3. **Governança de Rateio:**
   * 60% das despesas corporativas de TI e Gestão da Sede são rateadas equitativamente (15% para cada) entre os 4 centros produtivos da fábrica de Venâncio Aires.

---

Desenvolvido por **Iago Walter**  
Engenheiro de Produção | Especialista em BI, Modelagem Dimensional e Analytics Engineering
