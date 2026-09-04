# Documentação Técnica e de Negócio: FP&A & Controladoria Industrial

**Empresa Referência:** Alliance One Brasil Exportadora de Tabacos Ltda. (Polo Industrial Venâncio Aires - RS)  
**Modelo de Negócio:** *Leaf Merchant* (Processamento, Beneficiamento e Exportação Global de Tabaco em Folha)

---

## 1. Dicionário de Dados

### 1.1. Dimensão Plano de Contas (`Dim_PlanoContas`)

Tabela dimensional que define a hierarquia e ordenação do Demonstrativo de Resultados do Exercício (DRE Gerencial).

| Campo | Tipo de Dado | Restrição | Descrição |
| :--- | :--- | :--- | :--- |
| `ID_Conta` | VARCHAR(20) | PK | Código estruturado da conta contábil (Ex: `1.01.001`, `3.01.001`). |
| `Nome_Conta` | VARCHAR(150) | NOT NULL | Descrição da conta (Ex: `Exportacao Tabaco Processado - Strips Virginia`). |
| `Nivel1` | VARCHAR(100) | NOT NULL | Agrupamento macro da DRE (Receita Bruta, CPV, OPEX, etc.). |
| `Nivel2` | VARCHAR(100) | NOT NULL | Subgrupo de detalhamento operacional, fabril ou logístico. |
| `Natureza` | VARCHAR(20) | NOT NULL | Natureza contábil (`Debito` ou `Credito`). |
| `Ordem_DRE` | INTEGER | NOT NULL | Sequência numérica ordinal para renderização da matriz DRE. |

---

### 1.2. Dimensão Centros de Custo (`Dim_CentroCusto`)

Mapeia as linhas operacionais da fábrica de Venâncio Aires, áreas de campo e sede administrativa.

| Código | Nome do Centro de Custo | Tipo de Unidade | Área de Negócio |
| :--- | :--- | :--- | :--- |
| `CC1001` | Recepção, Pesagem e Classificação de Fumo Cru | Fábrica Venâncio Aires | Operações Fabris |
| `CC1002` | Linha de Debulha Mecânica (Threshing Lines) | Fábrica Venâncio Aires | Operações Fabris |
| `CC1003` | Secadores Contínuos e Redryers (Controle Umidade) | Fábrica Venâncio Aires | Operações Fabris |
| `CC1004` | Prensagem, Embalagem Caixas C-48 e Silos | Fábrica Venâncio Aires | Operações Fabris |
| `CC1005` | Manutenção Industrial, Vapor e Caldeiras Biomassa | Fábrica Venâncio Aires | Suporte Fabril |
| `CC2001` | Logística de Contêineres e Terminal Porto Rio Grande | Operacional | Logística Exportação |
| `CC2002` | Orientação Técnica Agronômica e Programa STP (Campo) | Operacional | Agronomia e Campo |
| `CC3001` | Sede Venâncio Aires - Diretoria, FP&A e Controladoria | Sede Administrativa | Corporativo |
| `CC3002` | TI Corporativa, Automação Fabril e Segurança | Sede Administrativa | Suporte Corporativo |
| `CC4001` | Mesa de Trading Global e Atendimento a Clientes | Comercial | Comercial Internacional |

---

### 1.3. Dimensão Calendário Fiscal (`Dim_Calendario`)

| Campo | Tipo de Dado | Restrição | Descrição |
| :--- | :--- | :--- | :--- |
| `Data` | DATE | PK | Data civil no formato ISO (`YYYY-MM-DD`). |
| `Ano` | INTEGER | NOT NULL | Ano civil (2024, 2025, 2026). |
| `Mes` | INTEGER | NOT NULL | Mês civil (1 a 12). |
| `AnoMes` | INTEGER | NOT NULL | Chave inteira de competência (`YYYYMM`). |
| `NomeMes` | VARCHAR(20) | NOT NULL | Abreviação do mês em português (`Jan`, `Fev`, etc.). |
| `Trimestre` | INTEGER | NOT NULL | Trimestre do exercício (1 a 4). |
| `Semestre` | INTEGER | NOT NULL | Semestre civil (1 ou 2). |
| `Safra_Ano` | VARCHAR(50) | NOT NULL | Identificador da Safra (`Safra 2024`, `Safra 2025`, `Safra 2026`). |

---

### 1.4. Fato Orçamento Planejado (`Fatos_Orcamento_Planejado`)

| Campo | Tipo de Dado | Restrição | Descrição |
| :--- | :--- | :--- | :--- |
| `ID_Orcamento` | INTEGER | PK (Auto) | Identificador sequencial do orçamento. |
| `AnoMes` | INTEGER | NOT NULL | Competência mensal do planejamento orçamentário. |
| `Ano` | INTEGER | NOT NULL | Ano fiscal. |
| `Mes` | INTEGER | NOT NULL | Mês fiscal. |
| `ID_Conta` | VARCHAR(20) | FK | Chave estrangeira referenciando `Dim_PlanoContas`. |
| `ID_CentroCusto` | VARCHAR(20) | FK | Chave estrangeira referenciando `Dim_CentroCusto`. |
| `Valor_Orcado` | DECIMAL(18, 2) | NOT NULL | Montante orçado planejado em Reais (R$). |

---

### 1.5. Fato Lançamentos Contábeis Reais (`Fatos_Lancamentos_Realizados`)

| Campo | Tipo de Dado | Restrição | Descrição |
| :--- | :--- | :--- | :--- |
| `ID_Lancamento` | VARCHAR(50) | PK | Código do documento contábil (Ex: `DOC-100245` ou `RAT-900012`). |
| `Data` | DATE | FK | Data da realização do lançamento. |
| `AnoMes` | INTEGER | NOT NULL | Mês e ano da competência contábil. |
| `ID_Conta` | VARCHAR(20) | FK | Chave estrangeira referenciando `Dim_PlanoContas`. |
| `ID_CentroCusto` | VARCHAR(20) | FK | Chave estrangeira referenciando `Dim_CentroCusto`. |
| `Valor_Realizado` | DECIMAL(18, 2) | NOT NULL | Montante efetivamente realizado em Reais (R$). |
| `Historico_Contabil`| VARCHAR(255) | NOT NULL | Descritivo e rastreabilidade da transação contábil. |

---

## 2. Regras Contábeis e Metodologia de Rateio

### 2.1. Estrutura da DRE Gerencial da Alliance One
1. **Receita Bruta**: 95%+ proveniente da exportação de *Strips Virgínia*, *Strips Burley* e *By-Products* (Talas/Stems), além de receitas residuais de mercado interno e amostras.
2. **Deduções**: Tributos sobre vendas locais e reclamações/ajustes de teor de umidade (*moisture*).
3. **CPV (Processamento Fabril Venâncio Aires)**: Aquisição de folha crua dos produtores integrados do Sul, mão de obra das linhas de *Threshing*, caldeiras a biomassa/vapor, embalagens C-48 e manutenção industrial.
4. **Margem Bruta**: `Receita Líquida - CPV Industrial`.
5. **OPEX & Logística**: Fretes rodoviários (Venâncio Aires até o Porto de Rio Grande), taxas portuárias de terminal alfandegado, equipe de campo/agronomia (Programa STP - *Sustainable Tobacco Programme*), TI e administração corporativa.
6. **EBITDA Gerencial**: `Margem Bruta - OPEX + Depreciação`.
7. **Resultado Financeiro**: Variação cambial de exportação em Dólar (USD), juros de adiantamento cambial (ACC/ACE) e rendimentos de tesouraria.
8. **Lucro Líquido**: `EBITDA - Depreciação + Resultado Financeiro - IRPJ/CSLL`.

---

### 2.2. Regra de Rateio de Custos Corporativos Indiretos
- **60% dos custos** de Gestão Administrativa (`CC3001` / Conta `4.03.001`) e TI Corporativa (`CC3002` / Conta `4.04.001`) são absorvidos pelas quatro etapas produtivas da fábrica (`CC1001` a `CC1004`) em cotas iguais de 15% cada.
- Os lançamentos de rateio recebem o prefixo `RAT-` no campo `ID_Lancamento` para auditoria contábil.

---

Desenvolvido por **Iago Walter**  
Engenheiro de Produção | Especialista em BI, Modelagem Dimensional e Analytics Engineering
