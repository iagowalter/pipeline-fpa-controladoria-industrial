"""
Módulo de Geração de Dados Sintéticos de FP&A e Controladoria Industrial
Setor: Indústria de Beneficiamento e Processamento de Tabaco

Este script gera dados contábeis realistas para o período de 2024 a 2026:
1. Plano de Contas Gerencial (Hierarquia contábil padronizada)
2. Centros de Custo Fabris e Corporativos
3. Fato Orçamento Planejado (Granularidade Mensal por Centro de Custo/Conta)
4. Fato Lançamentos Contábeis Reais (Livro Razão / GL Diário com Sazonalidade de Safra)
"""

import random
import datetime
import calendar
import pandas as pd
import numpy as np
from pathlib import Path
from config import get_logger, DATA_DIR

logger = get_logger("data_generator")

# Fixação da semente para reprodutibilidade matemática dos dados
random.seed(42)
np.random.seed(42)

def generate_chart_of_accounts() -> pd.DataFrame:
    """
    Gera o Plano de Contas Gerencial padronizado para a indústria de tabaco.
    Organizado em hierarquia estruturada para formação da DRE Contábil.
    """
    logger.info("Gerando Dimensão Plano de Contas...")
    accounts = [
        # 1. RECEITA OPERACIONAL BRUTA
        {"ID_Conta": "1.01.001", "Nome_Conta": "Venda Tabaco Processado - Exportacao", "Nivel1": "1. Receita Bruta", "Nivel2": "Receita de Exportacao", "Natureza": "Credito", "Ordem_DRE": 1},
        {"ID_Conta": "1.01.002", "Nome_Conta": "Venda Tabaco Processado - Mercado Interno", "Nivel1": "1. Receita Bruta", "Nivel2": "Receita Mercado Interno", "Natureza": "Credito", "Ordem_DRE": 2},
        {"ID_Conta": "1.02.001", "Nome_Conta": "Venda de Subprodutos (Talas e Fumos Picados)", "Nivel1": "1. Receita Bruta", "Nivel2": "Outras Receitas Operacionais", "Natureza": "Credito", "Ordem_DRE": 3},
        
        # 2. DEDUÇÕES DA RECEITA
        {"ID_Conta": "2.01.001", "Nome_Conta": "Impostos sobre Faturamento (PIS, COFINS, ICMS)", "Nivel1": "2. Deducoes da Receita", "Nivel2": "Impostos Incidentes", "Natureza": "Debito", "Ordem_DRE": 4},
        {"ID_Conta": "2.02.001", "Nome_Conta": "Devolucoes e Abatimentos de Exportacao", "Nivel1": "2. Deducoes da Receita", "Nivel2": "Cancelamentos e Abatimentos", "Natureza": "Debito", "Ordem_DRE": 5},

        # 3. CUSTO DOS PRODUTOS VENDIDOS (CPV INDUSTRIAL)
        {"ID_Conta": "3.01.001", "Nome_Conta": "Compra de Tabaco em Folha (Materia-Prima Safra)", "Nivel1": "3. Custo Industrial (CPV)", "Nivel2": "Materia-Prima Direta", "Natureza": "Debito", "Ordem_DRE": 6},
        {"ID_Conta": "3.02.001", "Nome_Conta": "Mao de Obra Direta Industrial (Debulha e Cura)", "Nivel1": "3. Custo Industrial (CPV)", "Nivel2": "Mao de Obra Fabril", "Natureza": "Debito", "Ordem_DRE": 7},
        {"ID_Conta": "3.03.001", "Nome_Conta": "Energia Eletrica Fabril e Vapor/Caldeiras", "Nivel1": "3. Custo Industrial (CPV)", "Nivel2": "Utilidades Industriais", "Natureza": "Debito", "Ordem_DRE": 8},
        {"ID_Conta": "3.04.001", "Nome_Conta": "Insumos de Embalagem (Caixas C-48 e Cintas)", "Nivel1": "3. Custo Industrial (CPV)", "Nivel2": "Embalagens e Insumos", "Natureza": "Debito", "Ordem_DRE": 9},
        {"ID_Conta": "3.05.001", "Nome_Conta": "Manutencao Industrial Preditiva e Corretiva", "Nivel1": "3. Custo Industrial (CPV)", "Nivel2": "Manutencao Fabril", "Natureza": "Debito", "Ordem_DRE": 10},
        {"ID_Conta": "3.06.001", "Nome_Conta": "Depreciacao de Linhas de Debulha e Secadores", "Nivel1": "3. Custo Industrial (CPV)", "Nivel2": "Depreciacao Industrial", "Natureza": "Debito", "Ordem_DRE": 11},

        # 4. DESPESAS OPERACIONAIS (OPEX)
        {"ID_Conta": "4.01.001", "Nome_Conta": "Fretes Internacionais e Terminal Portuario", "Nivel1": "4. Despesas Operacionais (OPEX)", "Nivel2": "Logistica e Embarque", "Natureza": "Debito", "Ordem_DRE": 12},
        {"ID_Conta": "4.02.001", "Nome_Conta": "Folha de Pagamento Administrativa e Gestao", "Nivel1": "4. Despesas Operacionais (OPEX)", "Nivel2": "Despesas Corporativas", "Natureza": "Debito", "Ordem_DRE": 13},
        {"ID_Conta": "4.03.001", "Nome_Conta": "Licencas de Software, TI e Infraestrutura", "Nivel1": "4. Despesas Operacionais (OPEX)", "Nivel2": "Tecnologia da Informacao", "Natureza": "Debito", "Ordem_DRE": 14},
        {"ID_Conta": "4.04.001", "Nome_Conta": "Laudos Agronomicos e Certificacoes Fitossanitarias", "Nivel1": "4. Despesas Operacionais (OPEX)", "Nivel2": "Qualidade e Agronomia", "Natureza": "Debito", "Ordem_DRE": 15},
        {"ID_Conta": "4.05.001", "Nome_Conta": "Viagens Comerciais e Prospeccao Global", "Nivel1": "4. Despesas Operacionais (OPEX)", "Nivel2": "Comercial e Vendas", "Natureza": "Debito", "Ordem_DRE": 16},
        {"ID_Conta": "4.06.001", "Nome_Conta": "Seguranca Patrimonial e Manutencao Predial", "Nivel1": "4. Despesas Operacionais (OPEX)", "Nivel2": "Facilities e Ocupacao", "Natureza": "Debito", "Ordem_DRE": 17},

        # 5. RESULTADO FINANCEIRO
        {"ID_Conta": "5.01.001", "Nome_Conta": "Variacao Cambial Liquida (Contratos de Exportacao)", "Nivel1": "5. Resultado Financeiro", "Nivel2": "Efeito Cambial", "Natureza": "Credito", "Ordem_DRE": 18},
        {"ID_Conta": "5.02.001", "Nome_Conta": "Despesas Financeiras e Juros de Capital de Giro", "Nivel1": "5. Resultado Financeiro", "Nivel2": "Despesas Bancarias", "Natureza": "Debito", "Ordem_DRE": 19},
        {"ID_Conta": "5.03.001", "Nome_Conta": "Receitas de Aplicacoes Financeiras de Curto Prazo", "Nivel1": "5. Resultado Financeiro", "Nivel2": "Receitas Financeiras", "Natureza": "Credito", "Ordem_DRE": 20},

        # 6. TRIBUTOS SOBRE O LUCRO
        {"ID_Conta": "6.01.001", "Nome_Conta": "Provisao de IRPJ e CSLL", "Nivel1": "6. Provisao Tributaria", "Nivel2": "Impostos Diretos", "Natureza": "Debito", "Ordem_DRE": 21}
    ]
    df = pd.DataFrame(accounts)
    logger.info(f"Dim_PlanoContas gerada com {len(df)} contas.")
    return df

def generate_cost_centers() -> pd.DataFrame:
    """
    Gera a Dimensão de Centros de Custo (Fabris, Operacionais e Corporativos).
    """
    logger.info("Gerando Dimensão Centros de Custo...")
    cost_centers = [
        {"ID_CentroCusto": "CC1001", "Nome_CentroCusto": "Recepcao e Classificacao de Folhas", "Tipo_Unidade": "Fabrica", "Area_Negocio": "Operacoes Fabris"},
        {"ID_CentroCusto": "CC1002", "Nome_CentroCusto": "Linha de Debulha e Separacao (Threshing)", "Tipo_Unidade": "Fabrica", "Area_Negocio": "Operacoes Fabris"},
        {"ID_CentroCusto": "CC1003", "Nome_CentroCusto": "Secadores Continuos e Redryer", "Tipo_Unidade": "Fabrica", "Area_Negocio": "Operacoes Fabris"},
        {"ID_CentroCusto": "CC1004", "Nome_CentroCusto": "Prensagem, Embalagem e Armazens C-48", "Tipo_Unidade": "Fabrica", "Area_Negocio": "Operacoes Fabris"},
        {"ID_CentroCusto": "CC1005", "Nome_CentroCusto": "Manutencao Industrial e Caldeiras", "Tipo_Unidade": "Fabrica", "Area_Negocio": "Suporte Fabril"},
        {"ID_CentroCusto": "CC2001", "Nome_CentroCusto": "Logistica, Fretes e Embarque Portuario", "Tipo_Unidade": "Operacional", "Area_Negocio": "Logistica"},
        {"ID_CentroCusto": "CC3001", "Nome_CentroCusto": "Diretoria Executiva e Controladoria", "Tipo_Unidade": "Matriz Corporativa", "Area_Negocio": "Corporativo"},
        {"ID_CentroCusto": "CC3002", "Nome_CentroCusto": "Tecnologia da Informacao e Seguranca", "Tipo_Unidade": "Matriz Corporativa", "Area_Negocio": "Suporte Corporativo"},
        {"ID_CentroCusto": "CC3003", "Nome_CentroCusto": "Recursos Humanos e Saude Ocupacional", "Tipo_Unidade": "Matriz Corporativa", "Area_Negocio": "Suporte Corporativo"},
        {"ID_CentroCusto": "CC4001", "Nome_CentroCusto": "Mesa de Trading e Vendas Globais", "Tipo_Unidade": "Comercial", "Area_Negocio": "Comercial"}
    ]
    df = pd.DataFrame(cost_centers)
    logger.info(f"Dim_CentroCusto gerada com {len(df)} centros de custo.")
    return df

def generate_calendar(start_year: int = 2024, end_year: int = 2026) -> pd.DataFrame:
    """
    Gera a Dimensão Calendário cobrindo o período fiscal de análise.
    """
    logger.info(f"Gerando Dimensão Calendário ({start_year} a {end_year})...")
    start_date = datetime.date(start_year, 1, 1)
    end_date = datetime.date(end_year, 12, 31)
    
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    df = pd.DataFrame({"Data": dates})
    df["Data"] = df["Data"].dt.date
    df["Ano"] = pd.to_datetime(df["Data"]).dt.year
    df["Mes"] = pd.to_datetime(df["Data"]).dt.month
    df["AnoMes"] = df["Ano"] * 100 + df["Mes"]
    df["NomeMes"] = pd.to_datetime(df["Data"]).dt.strftime('%b')
    df["Trimestre"] = pd.to_datetime(df["Data"]).dt.quarter
    df["Semestre"] = np.where(df["Mes"] <= 6, 1, 2)
    df["Safra_Ano"] = "Safra " + df["Ano"].astype(str)
    
    logger.info(f"Dim_Calendario gerada com {len(df)} dias.")
    return df

def generate_fpa_data(start_year: int = 2024, end_year: int = 2026):
    """
    Gera as tabelas de fatos:
    1. Fatos_Orcamento_Planejado (Mensal)
    2. Fatos_Lancamentos_Realizados (Diário)
    """
    logger.info("Iniciando geração de Fatos Orçado e Realizado com curvas sazonais de beneficiamento...")
    
    df_accounts = generate_chart_of_accounts()
    df_cc = generate_cost_centers()
    df_cal = generate_calendar(start_year, end_year)
    
    # Mapeamento de contas com seus centros de custo padrão
    account_cc_map = {
        "1.01.001": ["CC4001"],
        "1.01.002": ["CC4001"],
        "1.02.001": ["CC1004"],
        "2.01.001": ["CC3001"],
        "2.02.001": ["CC4001"],
        "3.01.001": ["CC1001"],
        "3.02.001": ["CC1002", "CC1003"],
        "3.03.001": ["CC1002", "CC1003", "CC1005"],
        "3.04.001": ["CC1004"],
        "3.05.001": ["CC1005"],
        "3.06.001": ["CC1002", "CC1003"],
        "4.01.001": ["CC2001"],
        "4.02.001": ["CC3001", "CC3003"],
        "4.03.001": ["CC3002"],
        "4.04.001": ["CC1001", "CC3001"],
        "4.05.001": ["CC4001"],
        "4.06.001": ["CC3001", "CC1005"],
        "5.01.001": ["CC3001"],
        "5.02.001": ["CC3001"],
        "5.03.001": ["CC3001"],
        "6.01.001": ["CC3001"]
    }
    
    # Valores base mensais médios (R$)
    base_values = {
        "1.01.001": 28500000.0, # Receita Exportação
        "1.01.002": 3200000.0,  # Receita Mercado Interno
        "1.02.001": 850000.0,   # Subprodutos
        "2.01.001": 2800000.0,  # Impostos
        "2.02.001": 150000.0,   # Devoluções
        "3.01.001": 14500000.0, # Compra de Tabaco Cru
        "3.02.001": 2200000.0,  # MOD Fabril
        "3.03.001": 950000.0,   # Energia e Caldeiras
        "3.04.001": 650000.0,   # Embalagens C-48
        "3.05.001": 480000.0,   # Manutenção Industrial
        "3.06.001": 720000.0,   # Depreciação
        "4.01.001": 1450000.0,  # Logística / Frete Porto Rio Grande
        "4.02.001": 550000.0,   # Pessoal Administrativo
        "4.03.001": 220000.0,   # TI / Licenças
        "4.04.001": 180000.0,   # Agronomia e Qualidade
        "4.05.001": 190000.0,   # Comercial / Viagens
        "4.06.001": 140000.0,   # Facilities
        "5.01.001": 450000.0,   # Variação Cambial
        "5.02.001": 380000.0,   # Juros Capital de Giro
        "5.03.001": 110000.0,   # Aplicações Financeiras
        "6.01.001": 1250000.0   # IRPJ / CSLL
    }
    
    # Sazonalidade de Safra de Tabaco (Meses 3 a 7: Pico de compra e beneficiamento)
    seasonality_cpv = {1: 0.4, 2: 0.6, 3: 1.5, 4: 1.8, 5: 1.7, 6: 1.6, 7: 1.4, 8: 1.0, 9: 0.8, 10: 0.5, 11: 0.4, 12: 0.3}
    # Sazonalidade de Exportação (Meses 5 a 11: Embarques concentrados no Porto)
    seasonality_rev = {1: 0.5, 2: 0.6, 3: 0.7, 4: 0.9, 5: 1.3, 6: 1.5, 7: 1.6, 8: 1.5, 9: 1.4, 10: 1.2, 11: 1.0, 12: 0.8}
    seasonality_flat = {m: 1.0 for m in range(1, 13)}
    
    budget_records = []
    real_records = []
    doc_id_counter = 100001
    
    months_series = df_cal[["Ano", "Mes", "AnoMes"]].drop_duplicates()
    
    for _, m_row in months_series.iterrows():
        ano = int(m_row["Ano"])
        mes = int(m_row["Mes"])
        anomes = int(m_row["AnoMes"])
        
        # Crescimento anual orçado (inflação/expansão de volume de safra)
        year_multiplier = 1.0 + ((ano - start_year) * 0.05)
        
        for acc_id, cc_list in account_cc_map.items():
            base_val = base_values[acc_id] * year_multiplier
            
            # Aplicação da curva sazonal conforme a natureza da conta
            if acc_id.startswith("1."):
                s_factor = seasonality_rev[mes]
            elif acc_id.startswith("3.") or acc_id == "4.01.001":
                s_factor = seasonality_cpv[mes]
            else:
                s_factor = seasonality_flat[mes]
                
            monthly_budget_total = base_val * s_factor
            
            # Divisão entre os centros de custo associados
            val_per_cc_budget = monthly_budget_total / len(cc_list)
            
            for cc_id in cc_list:
                # 1. Registro do Orçamento Mensal
                budget_records.append({
                    "AnoMes": anomes,
                    "Ano": ano,
                    "Mes": mes,
                    "ID_Conta": acc_id,
                    "ID_CentroCusto": cc_id,
                    "Valor_Orcado": round(val_per_cc_budget, 2)
                })
                
                # 2. Geração dos Lançamentos Reais Diários (Livro Razão / GL)
                # Introdução de variância real controlada (+/- 12% aleatório com choques pontuais)
                variance_factor = np.random.normal(1.02, 0.06) # Média levemente acima do orçado
                
                # Evento pontual realista: Em maio de 2025 houve quebra de secador, elevando manutenção em 35%
                if ano == 2025 and mes == 5 and acc_id == "3.05.001":
                    variance_factor = 1.38
                # Evento pontual realista: Em setembro de 2024 pico de valorização cambial favorável
                if ano == 2024 and mes == 9 and acc_id == "5.01.001":
                    variance_factor = 1.45
                    
                monthly_real_total = val_per_cc_budget * variance_factor
                
                # Número de dias úteis no mês para pulverização dos lançamentos contábeis
                _, num_days = calendar.monthrange(ano, mes)
                num_entries = random.randint(4, 12) if not acc_id.startswith("3.06") else 1 # Depreciação é 1 lançamento
                
                # Distribuição do valor mensal em múltiplos lançamentos diários
                daily_weights = np.random.dirichlet(np.ones(num_entries))
                entry_days = sorted(random.sample(range(1, num_days + 1), num_entries))
                
                for day, weight in zip(entry_days, daily_weights):
                    entry_val = monthly_real_total * weight
                    entry_date = datetime.date(ano, mes, day)
                    doc_id_counter += 1
                    
                    real_records.append({
                        "ID_Lancamento": f"DOC-{doc_id_counter}",
                        "Data": entry_date,
                        "AnoMes": anomes,
                        "ID_Conta": acc_id,
                        "ID_CentroCusto": cc_id,
                        "Valor_Realizado": round(entry_val, 2),
                        "Historico_Contabil": f"Lancamento Contabil - {acc_id} - Ref {mes:02d}/{ano}"
                    })

    df_budget = pd.DataFrame(budget_records)
    df_real = pd.DataFrame(real_records)
    
    logger.info(f"Fatos_Orcamento_Planejado gerada com {len(df_budget)} registros.")
    logger.info(f"Fatos_Lancamentos_Realizados gerada com {len(df_real)} lançamentos diários.")
    
    return df_accounts, df_cc, df_cal, df_budget, df_real

if __name__ == "__main__":
    df_acc, df_cc, df_cal, df_bgt, df_real = generate_fpa_data()
    print("\nAmostra do Orçamento Mensal:")
    print(df_bgt.head())
    print("\nAmostra dos Lançamentos Reais Diários:")
    print(df_real.head())
