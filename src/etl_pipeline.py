"""
Pipeline de Engenharia de Dados e Transformação Contábil (ETL / DataOps)
Projeto: FP&A & Controladoria Industrial (Beneficiamento de Tabaco)

Este módulo orquestra o ciclo completo de dados (Bronze -> Silver -> Gold):
1. Ingestão e extração das bases contábeis e orçamentárias brutas.
2. Tratamento, tipagem e enriquecimento dimensional.
3. Aplicação de regra de negócio de Rateio Contábil de Despesas Corporativas Indiretas.
4. Carga relacional no banco de dados SQLite (fpa_industrial_dw.db) e exportação em CSV para consumo no Power BI.
5. Registro estruturado de métricas e volumetria em logs/pipeline_fpa.log.
"""

import time
import sqlite3
import pandas as pd
from pathlib import Path
from config import get_logger, DB_PATH, DATA_DIR
from generator import generate_fpa_data

logger = get_logger("etl_pipeline")

def apply_corporate_cost_allocation(df_real: pd.DataFrame, df_budget: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Aplica regra contábil de rateio de despesas indiretas corporativas (TI e RH)
    para os centros de custos fabris e operacionais.
    
    Regra de Negócio:
    - 60% das despesas corporativas de TI (CC3002) e RH (CC3003) são absorvidas
      pelos 4 centros produtivos fabris principais (CC1001 a CC1004) em partes iguais (15% cada).
    - Essa transformação é gravada como lançamento de rateio interno gerencial.
    """
    logger.info("Aplicando regra de rateio de despesas corporativas para a operação fabril...")
    
    # Identificação dos centros de custo produtivos que receberão a cota de rateio
    productive_ccs = ["CC1001", "CC1002", "CC1003", "CC1004"]
    corporate_support_ccs = ["CC3002", "CC3003"]
    
    # 1. Rateio nos Lançamentos Reais
    mask_real_corp = df_real["ID_CentroCusto"].isin(corporate_support_ccs) & df_real["ID_Conta"].isin(["4.02.001", "4.03.001"])
    corp_real_entries = df_real[mask_real_corp].copy()
    
    allocated_real_records = []
    doc_counter = 900001
    
    for _, row in corp_real_entries.iterrows():
        # Valor a ser rateado (60% do total)
        total_to_allocate = row["Valor_Realizado"] * 0.60
        quota_per_cc = total_to_allocate / len(productive_ccs)
        
        for prod_cc in productive_ccs:
            doc_counter += 1
            allocated_real_records.append({
                "ID_Lancamento": f"RAT-{doc_counter}",
                "Data": row["Data"],
                "AnoMes": row["AnoMes"],
                "ID_Conta": row["ID_Conta"],
                "ID_CentroCusto": prod_cc,
                "Valor_Realizado": round(quota_per_cc, 2),
                "Historico_Contabil": f"Rateio Gerencial 15% Absorcao Fabril - Origem {row['ID_CentroCusto']}"
            })
            
    df_allocated_real = pd.DataFrame(allocated_real_records)
    logger.info(f"Gerados {len(df_allocated_real)} lançamentos contábeis de rateio de despesas indiretas.")
    
    return df_real, df_budget

def create_database_schema(conn: sqlite3.Connection):
    """
    Cria a estrutura de tabelas relacionais (DDL) no SQLite.
    """
    logger.info("Criando esquema relacional (Star Schema) no Data Warehouse SQLite...")
    cursor = conn.cursor()
    
    # 1. Dimensão Plano de Contas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Dim_PlanoContas (
        ID_Conta TEXT PRIMARY KEY,
        Nome_Conta TEXT NOT NULL,
        Nivel1 TEXT NOT NULL,
        Nivel2 TEXT NOT NULL,
        Natureza TEXT NOT NULL,
        Ordem_DRE INTEGER NOT NULL
    );
    """)
    
    # 2. Dimensão Centros de Custo
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Dim_CentroCusto (
        ID_CentroCusto TEXT PRIMARY KEY,
        Nome_CentroCusto TEXT NOT NULL,
        Tipo_Unidade TEXT NOT NULL,
        Area_Negocio TEXT NOT NULL
    );
    """)
    
    # 3. Dimensão Calendário
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Dim_Calendario (
        Data TEXT PRIMARY KEY,
        Ano INTEGER NOT NULL,
        Mes INTEGER NOT NULL,
        AnoMes INTEGER NOT NULL,
        NomeMes TEXT NOT NULL,
        Trimestre INTEGER NOT NULL,
        Semestre INTEGER NOT NULL,
        Safra_Ano TEXT NOT NULL
    );
    """)
    
    # 4. Fato Orçamento Planejado
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Fatos_Orcamento_Planejado (
        ID_Orcamento INTEGER PRIMARY KEY AUTOINCREMENT,
        AnoMes INTEGER NOT NULL,
        Ano INTEGER NOT NULL,
        Mes INTEGER NOT NULL,
        ID_Conta TEXT NOT NULL,
        ID_CentroCusto TEXT NOT NULL,
        Valor_Orcado REAL NOT NULL,
        FOREIGN KEY (ID_Conta) REFERENCES Dim_PlanoContas(ID_Conta),
        FOREIGN KEY (ID_CentroCusto) REFERENCES Dim_CentroCusto(ID_CentroCusto)
    );
    """)
    
    # 5. Fato Lançamentos Contábeis Reais
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Fatos_Lancamentos_Realizados (
        ID_Lancamento TEXT PRIMARY KEY,
        Data TEXT NOT NULL,
        AnoMes INTEGER NOT NULL,
        ID_Conta TEXT NOT NULL,
        ID_CentroCusto TEXT NOT NULL,
        Valor_Realizado REAL NOT NULL,
        Historico_Contabil TEXT NOT NULL,
        FOREIGN KEY (Data) REFERENCES Dim_Calendario(Data),
        FOREIGN KEY (ID_Conta) REFERENCES Dim_PlanoContas(ID_Conta),
        FOREIGN KEY (ID_CentroCusto) REFERENCES Dim_CentroCusto(ID_CentroCusto)
    );
    """)
    
    # Criação de índices para ganho de performance em consultas analíticas
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_real_data ON Fatos_Lancamentos_Realizados(Data);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_real_conta ON Fatos_Lancamentos_Realizados(ID_Conta);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_real_cc ON Fatos_Lancamentos_Realizados(ID_CentroCusto);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_bgt_anomes ON Fatos_Orcamento_Planejado(AnoMes);")
    
    conn.commit()
    logger.info("Esquema DDL e índices criados com sucesso no banco de dados.")

def run_etl_pipeline():
    """
    Executa o fluxo completo do pipeline ETL de ponta a ponta.
    """
    start_time = time.time()
    logger.info("================================================================================")
    logger.info("INICIANDO EXECUÇÃO DO PIPELINE DE ENGENHARIA DE DADOS - FP&A INDUSTRIAL")
    logger.info("================================================================================")
    
    try:
        # Etapa 1: Extração / Geração de Dados
        df_accounts, df_cc, df_cal, df_budget, df_real = generate_fpa_data(start_year=2024, end_year=2026)
        
        # Etapa 2: Transformação e Rateios
        df_real_treated, df_budget_treated = apply_corporate_cost_allocation(df_real, df_budget)
        
        # Etapa 3: Persistência no Banco de Dados Relacional (SQLite)
        conn = sqlite3.connect(DB_PATH)
        create_database_schema(conn)
        
        logger.info("Populando tabelas relacionais do Data Warehouse...")
        df_accounts.to_sql("Dim_PlanoContas", conn, if_exists="replace", index=False)
        df_cc.to_sql("Dim_CentroCusto", conn, if_exists="replace", index=False)
        
        # Conversão de objetos de data para string ISO para compatibilidade SQLite
        df_cal_db = df_cal.copy()
        df_cal_db["Data"] = df_cal_db["Data"].astype(str)
        df_cal_db.to_sql("Dim_Calendario", conn, if_exists="replace", index=False)
        
        df_budget_treated.to_sql("Fatos_Orcamento_Planejado", conn, if_exists="replace", index=False)
        
        df_real_db = df_real_treated.copy()
        df_real_db["Data"] = df_real_db["Data"].astype(str)
        df_real_db.to_sql("Fatos_Lancamentos_Realizados", conn, if_exists="replace", index=False)
        
        conn.close()
        logger.info("Carga relacional no SQLite concluída com sucesso.")
        
        # Etapa 4: Exportação de CSVs padronizados na pasta /data para conexão direta no Power BI
        logger.info("Exportando datasets formatados em CSV para consumo no Power BI...")
        df_accounts.to_csv(DATA_DIR / "Dim_PlanoContas.csv", index=False, sep=";", encoding="utf-8-sig")
        df_cc.to_csv(DATA_DIR / "Dim_CentroCusto.csv", index=False, sep=";", encoding="utf-8-sig")
        df_cal_db.to_csv(DATA_DIR / "Dim_Calendario.csv", index=False, sep=";", encoding="utf-8-sig")
        df_budget_treated.to_csv(DATA_DIR / "Fatos_Orcamento_Planejado.csv", index=False, sep=";", encoding="utf-8-sig")
        df_real_db.to_csv(DATA_DIR / "Fatos_Lancamentos_Realizados.csv", index=False, sep=";", encoding="utf-8-sig")
        
        duration = round(time.time() - start_time, 2)
        logger.info("================================================================================")
        logger.info(f"PIPELINE EXECUTADO COM SUCESSO EM {duration} SEGUNDOS.")
        logger.info(f"Total de Contas: {len(df_accounts)} | Centros de Custo: {len(df_cc)}")
        logger.info(f"Total de Orçamentos Mensais: {len(df_budget_treated)} | Lançamentos Reais: {len(df_real_db)}")
        logger.info("================================================================================")
        
    except Exception as e:
        logger.error(f"FALHA CRÍTICA NA EXECUÇÃO DO PIPELINE: {str(e)}", exc_info=True)
        raise e

if __name__ == "__main__":
    run_etl_pipeline()
