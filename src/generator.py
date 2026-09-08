"""
Módulo de Geração de Dados Sintéticos de FP&A e Controladoria Industrial
Empresa Referência: Alliance One Brasil (Polo Venâncio Aires - RS)
Modelo de Negócio: Leaf Merchant (Processamento, Beneficiamento e Exportação de Tabaco em Folha)

Gera dados contábeis e operacionais realistas para o período de 2024 a 2026:
- Faturamento anual realista na faixa de R$ 650M a R$ 850M (Alliance One Brasil)
- Fatos_Orcamento_Planejado contendo a coluna 'Data' (dia 01 do mês) para relacionamento 1:N perfeito com Dim_Calendario
"""

import random
import datetime
import calendar
import pandas as pd
import numpy as np
from pathlib import Path
from config import get_logger, DATA_DIR

logger = get_logger("generator_alliance_one")

# Fixação da semente para reprodutibilidade matemática
random.seed(42)
np.random.seed(42)

def generate_chart_of_accounts() -> pd.DataFrame:
    """
    Gera o Plano de Contas Gerencial estruturado para a operação de processamento
    e exportação de tabaco em folha (Alliance One - Polo Venâncio Aires).
    """
    accounts = [
        # 1. RECEITA OPERACIONAL BRUTA (95%+ EXPORTAÇÃO)
        {"ID_Conta": "1.01.001", "Nome_Conta": "Exportacao Tabaco Processado - Strips Virginia", "Nome_Produto_Curto": "Strips Virgínia", "Nivel1": "1. Receita Bruta", "Nivel2": "Receita de Exportacao", "Natureza": "Credito", "Ordem_DRE": 1},
        {"ID_Conta": "1.01.002", "Nome_Conta": "Exportacao Tabaco Processado - Strips Burley", "Nome_Produto_Curto": "Strips Burley", "Nivel1": "1. Receita Bruta", "Nivel2": "Receita de Exportacao", "Natureza": "Credito", "Ordem_DRE": 2},
        {"ID_Conta": "1.01.003", "Nome_Conta": "Exportacao de By-Products (Stems/Talas e Fumos Picados)", "Nome_Produto_Curto": "By-Products & Talas", "Nivel1": "1. Receita Bruta", "Nivel2": "Receita de Exportacao", "Natureza": "Credito", "Ordem_DRE": 3},
        {"ID_Conta": "1.02.001", "Nome_Conta": "Vendas no Mercado Interno e Amostras Comerciais", "Nome_Produto_Curto": "Mercado Interno", "Nivel1": "1. Receita Bruta", "Nivel2": "Receita Mercado Interno", "Natureza": "Credito", "Ordem_DRE": 4},
        
        # 2. DEDUÇÕES DA RECEITA
        {"ID_Conta": "2.01.001", "Nome_Conta": "Tributos sobre Faturamento Interno (PIS/COFINS/ICMS)", "Nome_Produto_Curto": "Tributos sobre Vendas", "Nivel1": "2. Deducoes da Receita", "Nivel2": "Impostos Incidentes", "Natureza": "Debito", "Ordem_DRE": 5},
        {"ID_Conta": "2.02.001", "Nome_Conta": "Descontos Comerciais e Reclamacoes de Umidade/Qualidade", "Nome_Produto_Curto": "Descontos Comerciais", "Nivel1": "2. Deducoes da Receita", "Nivel2": "Cancelamentos e Abatimentos", "Natureza": "Debito", "Ordem_DRE": 6},

        # 3. CUSTO DOS PRODUTOS VENDIDOS (CPV / PROCESSAMENTO INDUSTRIAL VENÂNCIO AIRES)
        {"ID_Conta": "3.01.001", "Nome_Conta": "Aquisicao de Tabaco Cru (Produtores Integrados Sul)", "Nome_Produto_Curto": "Matéria-Prima Safra", "Nivel1": "3. Custo Industrial (CPV)", "Nivel2": "Materia-Prima Direta", "Natureza": "Debito", "Ordem_DRE": 7},
        {"ID_Conta": "3.02.001", "Nome_Conta": "Mao de Obra Direta Fabril (Linhas Threshing e Prensas)", "Nome_Produto_Curto": "Mão de Obra Fabril", "Nivel1": "3. Custo Industrial (CPV)", "Nivel2": "Mao de Obra Fabril", "Natureza": "Debito", "Ordem_DRE": 8},
        {"ID_Conta": "3.03.001", "Nome_Conta": "Utilidades Industriais (Caldeiras a Biomassa, Vapor e Energia)", "Nome_Produto_Curto": "Caldeiras & Energia", "Nivel1": "3. Custo Industrial (CPV)", "Nivel2": "Utilidades Fabris", "Natureza": "Debito", "Ordem_DRE": 9},
        {"ID_Conta": "3.04.001", "Nome_Conta": "Embalagens de Exportacao (Caixas C-48, Liners e Cintas)", "Nome_Produto_Curto": "Caixas C-48 & Insumos", "Nivel1": "3. Custo Industrial (CPV)", "Nivel2": "Embalagens e Insumos", "Natureza": "Debito", "Ordem_DRE": 10},
        {"ID_Conta": "3.05.001", "Nome_Conta": "Manutencao Industrial Preditiva das Linhas de Debulha", "Nome_Produto_Curto": "Manutenção Threshing", "Nivel1": "3. Custo Industrial (CPV)", "Nivel2": "Manutencao Fabril", "Natureza": "Debito", "Ordem_DRE": 11},
        {"ID_Conta": "3.06.001", "Nome_Conta": "Depreciacao Fabril (Linhas Threshing, Redryers e Silos)", "Nome_Produto_Curto": "Depreciação Fabril", "Nivel1": "3. Custo Industrial (CPV)", "Nivel2": "Depreciacao Fabril", "Natureza": "Debito", "Ordem_DRE": 12},

        # 4. DESPESAS OPERACIONAIS (OPEX & LOGÍSTICA DE EXPORTAÇÃO)
        {"ID_Conta": "4.01.001", "Nome_Conta": "Fretes Rodoviarios (Venancio Aires -> Porto de Rio Grande)", "Nome_Produto_Curto": "Fretes Porto Rio Grande", "Nivel1": "4. Despesas Operacionais (OPEX)", "Nivel2": "Logistica e Exportacao", "Natureza": "Debito", "Ordem_DRE": 13},
        {"ID_Conta": "4.01.002", "Nome_Conta": "Custos Portuarios, Estufagem e Terminal Alfandegado", "Nome_Produto_Curto": "Terminal Portuário", "Nivel1": "4. Despesas Operacionais (OPEX)", "Nivel2": "Logistica e Exportacao", "Natureza": "Debito", "Ordem_DRE": 14},
        {"ID_Conta": "4.02.001", "Nome_Conta": "Assistente Tecnico de Campo e Programa STP (Agronomia/ESG)", "Nome_Produto_Curto": "Agronomia / STP", "Nivel1": "4. Despesas Operacionais (OPEX)", "Nivel2": "Agronomia e Sustentabilidade", "Natureza": "Debito", "Ordem_DRE": 15},
        {"ID_Conta": "4.03.001", "Nome_Conta": "Folha de Pagamento Administrativa e Gestao Corporativa", "Nome_Produto_Curto": "Administrativo & Gestão", "Nivel1": "4. Despesas Operacionais (OPEX)", "Nivel2": "Despesas Corporativas", "Natureza": "Debito", "Ordem_DRE": 16},
        {"ID_Conta": "4.04.001", "Nome_Conta": "Tecnologia da Informacao, ERP e Automacao Fabril", "Nome_Produto_Curto": "TI & Automação", "Nivel1": "4. Despesas Operacionais (OPEX)", "Nivel2": "Tecnologia da Informacao", "Natureza": "Debito", "Ordem_DRE": 17},
        {"ID_Conta": "4.05.001", "Nome_Conta": "Laudos Fitossanitarios, Laboratorio de Fumo e Qualidade", "Nome_Produto_Curto": "Laboratório & Qualidade", "Nivel1": "4. Despesas Operacionais (OPEX)", "Nivel2": "Qualidade e Laboratorio", "Natureza": "Debito", "Ordem_DRE": 18},
        {"ID_Conta": "4.06.001", "Nome_Conta": "Mesa Comercial Internacional e Negociacao de Safras", "Nome_Produto_Curto": "Comercial & Vendas", "Nivel1": "4. Despesas Operacionais (OPEX)", "Nivel2": "Comercial e Vendas", "Natureza": "Debito", "Ordem_DRE": 19},

        # 5. RESULTADO FINANCEIRO (ACC / HEDGE CAMBIAL)
        {"ID_Conta": "5.01.001", "Nome_Conta": "Variacao Cambial Liquida (Contratos de Exportacao USD)", "Nome_Produto_Curto": "Variação Cambial", "Nivel1": "5. Resultado Financeiro", "Nivel2": "Efeito Cambial", "Natureza": "Credito", "Ordem_DRE": 20},
        {"ID_Conta": "5.02.001", "Nome_Conta": "Juros e Despesas com Antecipacao Cambial (ACC / ACE)", "Nome_Produto_Curto": "Despesas Bancárias / ACC", "Nivel1": "5. Resultado Financeiro", "Nivel2": "Despesas Bancarias", "Natureza": "Debito", "Ordem_DRE": 21},
        {"ID_Conta": "5.03.001", "Nome_Conta": "Rendimento de Aplicacoes Financeiras de Tesouraria", "Nome_Produto_Curto": "Rendimentos Tesouraria", "Nivel1": "5. Resultado Financeiro", "Nivel2": "Receitas Financeiras", "Natureza": "Credito", "Ordem_DRE": 22},

        # 6. TRIBUTOS SOBRE O LUCRO
        {"ID_Conta": "6.01.001", "Nome_Conta": "Provisao de IRPJ e CSLL", "Nome_Produto_Curto": "Provisão IRPJ/CSLL", "Nivel1": "6. Provisao Tributaria", "Nivel2": "Impostos Diretos", "Natureza": "Debito", "Ordem_DRE": 23}
    ]
    return pd.DataFrame(accounts)

def generate_cost_centers() -> pd.DataFrame:
    """
    Gera a Dimensão de Centros de Custo da Alliance One (Polo Venâncio Aires).
    """
    cost_centers = [
        {"ID_CentroCusto": "CC1001", "Nome_CentroCusto": "Recepcao, Pesagem e Classificacao de Fumo Cru", "Tipo_Unidade": "Fabrica Venancio Aires", "Area_Negocio": "Operacoes Fabris"},
        {"ID_CentroCusto": "CC1002", "Nome_CentroCusto": "Linha de Debulha Mecanica (Threshing Lines)", "Tipo_Unidade": "Fabrica Venancio Aires", "Area_Negocio": "Operacoes Fabris"},
        {"ID_CentroCusto": "CC1003", "Nome_CentroCusto": "Secadores Continuos e Redryers (Controle Umidade)", "Tipo_Unidade": "Fabrica Venancio Aires", "Area_Negocio": "Operacoes Fabris"},
        {"ID_CentroCusto": "CC1004", "Nome_CentroCusto": "Prensagem, Embalagem Caixas C-48 e Silos", "Tipo_Unidade": "Fabrica Venancio Aires", "Area_Negocio": "Operacoes Fabris"},
        {"ID_CentroCusto": "CC1005", "Nome_CentroCusto": "Manutencao Industrial, Vapor e Caldeiras Biomassa", "Tipo_Unidade": "Fabrica Venancio Aires", "Area_Negocio": "Suporte Fabril"},
        {"ID_CentroCusto": "CC2001", "Nome_CentroCusto": "Logistica de Conteineres e Terminal Porto Rio Grande", "Tipo_Unidade": "Operacional", "Area_Negocio": "Logistica Exportacao"},
        {"ID_CentroCusto": "CC2002", "Nome_CentroCusto": "Orientacao Tecnica Agronomica e Programa STP (Campo)", "Tipo_Unidade": "Operacional", "Area_Negocio": "Agronomia e Campo"},
        {"ID_CentroCusto": "CC3001", "Nome_CentroCusto": "Sede Venancio Aires - Diretoria, FP&A e Controladoria", "Tipo_Unidade": "Sede Administrativa", "Area_Negocio": "Corporativo"},
        {"ID_CentroCusto": "CC3002", "Nome_CentroCusto": "TI Corporativa, Automacao Fabril e Seguranca", "Tipo_Unidade": "Sede Administrativa", "Area_Negocio": "Suporte Corporativo"},
        {"ID_CentroCusto": "CC4001", "Nome_CentroCusto": "Mesa de Trading Global e Atendimento a Clientes", "Tipo_Unidade": "Comercial", "Area_Negocio": "Comercial Internacional"}
    ]
    return pd.DataFrame(cost_centers)

def generate_calendar(start_year: int = 2024, end_year: int = 2026) -> pd.DataFrame:
    """
    Gera a Dimensão Calendário.
    """
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
    return df

def generate_fpa_data(start_year: int = 2024, end_year: int = 2026):
    """
    Gera as tabelas de fatos com faturamento e custos realistas para a Alliance One Brasil.
    """
    logger.info("Gerando bases calibradas para Alliance One Brasil (Venâncio Aires)...")
    
    df_accounts = generate_chart_of_accounts()
    df_cc = generate_cost_centers()
    df_cal = generate_calendar(start_year, end_year)
    
    account_cc_map = {
        "1.01.001": ["CC4001"],
        "1.01.002": ["CC4001"],
        "1.01.003": ["CC4001"],
        "1.02.001": ["CC4001"],
        "2.01.001": ["CC3001"],
        "2.02.001": ["CC4001"],
        "3.01.001": ["CC1001"],
        "3.02.001": ["CC1002", "CC1003"],
        "3.03.001": ["CC1002", "CC1003", "CC1005"],
        "3.04.001": ["CC1004"],
        "3.05.001": ["CC1005"],
        "3.06.001": ["CC1002", "CC1003"],
        "4.01.001": ["CC2001"],
        "4.01.002": ["CC2001"],
        "4.02.001": ["CC2002"],
        "4.03.001": ["CC3001"],
        "4.04.001": ["CC3002"],
        "4.05.001": ["CC1001", "CC3001"],
        "4.06.001": ["CC4001"],
        "5.01.001": ["CC3001"],
        "5.02.001": ["CC3001"],
        "5.03.001": ["CC3001"],
        "6.01.001": ["CC3001"]
    }
    
    # Valores base mensais médios (R$) ajustados para R$ 750M/ano de Receita Operacional
    base_values = {
        "1.01.001": 42000000.0, # Exportação Strips Virgínia
        "1.01.002": 14500000.0, # Exportação Strips Burley
        "1.01.003": 3800000.0,  # Exportação Talas/By-Products
        "1.02.001": 1200000.0,  # Mercado Interno/Amostras
        "2.01.001": 550000.0,   # Tributos Faturamento Interno
        "2.02.001": 320000.0,   # Abatimentos/Ajustes de Umidade
        "3.01.001": 31000000.0, # Compra de Fumo Cru dos Produtores
        "3.02.001": 4800000.0,  # MOD Linhas de Debulha/Prensagem
        "3.03.001": 1950000.0,  # Caldeiras Biomassa, Vapor e Energia
        "3.04.001": 1450000.0,  # Caixas C-48 e Embalagens
        "3.05.001": 980000.0,   # Manutenção Linhas Threshing
        "3.06.001": 1250000.0,  # Depreciação Maquinário
        "4.01.001": 2450000.0,  # Fretes Rodoviários Venâncio -> Porto Rio Grande
        "4.01.002": 950000.0,   # Custos Portuários e Terminal Alfandegado
        "4.02.001": 650000.0,   # Agronomia de Campo / Programa STP
        "4.03.001": 1150000.0,  # Folha Administrativa Sede
        "4.04.001": 450000.0,   # TI e Automação
        "4.05.001": 280000.0,   # Laboratório de Fumo e Qualidade
        "4.06.001": 380000.0,   # Comercial Internacional
        "5.01.001": 850000.0,   # Variação Cambial Exportação USD
        "5.02.001": 680000.0,   # Despesas Financeiras ACC/ACE
        "5.03.001": 190000.0,   # Aplicações Tesouraria
        "6.01.001": 2100000.0   # IRPJ / CSLL
    }
    
    seasonality_cpv = {1: 0.35, 2: 0.55, 3: 1.55, 4: 1.85, 5: 1.75, 6: 1.65, 7: 1.40, 8: 0.95, 9: 0.75, 10: 0.50, 11: 0.40, 12: 0.30}
    seasonality_export = {1: 0.45, 2: 0.55, 3: 0.70, 4: 0.90, 5: 1.30, 6: 1.55, 7: 1.65, 8: 1.60, 9: 1.45, 10: 1.25, 11: 0.95, 12: 0.65}
    seasonality_flat = {m: 1.0 for m in range(1, 13)}
    
    budget_records = []
    real_records = []
    doc_id_counter = 100001
    
    months_series = df_cal[["Ano", "Mes", "AnoMes"]].drop_duplicates()
    
    for _, m_row in months_series.iterrows():
        ano = int(m_row["Ano"])
        mes = int(m_row["Mes"])
        anomes = int(m_row["AnoMes"])
        month_first_day = datetime.date(ano, mes, 1)
        
        year_multiplier = 1.0 + ((ano - start_year) * 0.04)
        
        for acc_id, cc_list in account_cc_map.items():
            base_val = base_values[acc_id] * year_multiplier
            
            if acc_id.startswith("1."):
                s_factor = seasonality_export[mes]
            elif acc_id.startswith("3.") or acc_id.startswith("4.01"):
                s_factor = seasonality_cpv[mes]
            else:
                s_factor = seasonality_flat[mes]
                
            monthly_budget_total = base_val * s_factor
            val_per_cc_budget = monthly_budget_total / len(cc_list)
            
            for cc_id in cc_list:
                # Orçamento agora contém a coluna 'Data' (dia 01 do mês) para relacionamento com Dim_Calendario
                budget_records.append({
                    "ID_Orcamento": len(budget_records) + 1,
                    "Data": month_first_day,
                    "AnoMes": anomes,
                    "Ano": ano,
                    "Mes": mes,
                    "ID_Conta": acc_id,
                    "ID_CentroCusto": cc_id,
                    "Valor_Orcado": round(val_per_cc_budget, 2)
                })
                
                # Variância real diária controlada
                variance_factor = np.random.normal(1.015, 0.04)
                
                if ano == 2025 and mes == 6 and acc_id in ["3.03.001", "4.01.001"]:
                    variance_factor = 1.18
                if ano == 2024 and mes == 10 and acc_id.startswith("1.01"):
                    variance_factor = 1.12
                if ano == 2025 and mes == 4 and acc_id == "3.05.001":
                    variance_factor = 1.22
                    
                monthly_real_total = val_per_cc_budget * variance_factor
                
                _, num_days = calendar.monthrange(ano, mes)
                num_entries = random.randint(4, 10) if not acc_id.startswith("3.06") else 1
                
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
                        "Historico_Contabil": f"Lancamento Razao - {acc_id} - Ref {mes:02d}/{ano} - Planta Venancio Aires"
                    })

    df_budget = pd.DataFrame(budget_records)
    df_real = pd.DataFrame(real_records)
    
    return df_accounts, df_cc, df_cal, df_budget, df_real

if __name__ == "__main__":
    df_acc, df_cc, df_cal, df_bgt, df_real = generate_fpa_data()
    print("Dados calibrados gerados com sucesso.")
