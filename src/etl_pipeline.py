"""
Pipeline de Engenharia de Dados e Transformação Contábil (ETL / DataOps)
Empresa Referência: Alliance One Brasil (Polo Venâncio Aires - RS)
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
    Aplica regra contábil de rateio de despesas indiretas corporativas da Sede (TI e Gestão)
    para as linhas produtivas da fábrica de Venâncio Aires.
    """
    productive_ccs = ["CC1001", "CC1002", "CC1003", "CC1004"]
    corporate_support_ccs = ["CC3001", "CC3002"]
    
    mask_real_corp = df_real["ID_CentroCusto"].isin(corporate_support_ccs) & df_real["ID_Conta"].isin(["4.03.001", "4.04.001"])
    corp_real_entries = df_real[mask_real_corp].copy()
    
    allocated_real_records = []
    doc_counter = 900001
    
    for _, row in corp_real_entries.iterrows():
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
    df_real_total = pd.concat([df_real, df_allocated_real], ignore_index=True)
    return df_real_total, df_budget

def create_database_schema(conn: sqlite3.Connection):
    """
    Cria a estrutura de tabelas relacionais no SQLite.
    """
    cursor = conn.cursor()
    
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
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Dim_CentroCusto (
        ID_CentroCusto TEXT PRIMARY KEY,
        Nome_CentroCusto TEXT NOT NULL,
        Tipo_Unidade TEXT NOT NULL,
        Area_Negocio TEXT NOT NULL
    );
    """)
    
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
    
    cursor.execute("DROP TABLE IF EXISTS Fatos_Orcamento_Planejado;")
    cursor.execute("""
    CREATE TABLE Fatos_Orcamento_Planejado (
        ID_Orcamento INTEGER PRIMARY KEY,
        Data TEXT NOT NULL,
        AnoMes INTEGER NOT NULL,
        Ano INTEGER NOT NULL,
        Mes INTEGER NOT NULL,
        ID_Conta TEXT NOT NULL,
        ID_CentroCusto TEXT NOT NULL,
        Valor_Orcado REAL NOT NULL,
        FOREIGN KEY (Data) REFERENCES Dim_Calendario(Data),
        FOREIGN KEY (ID_Conta) REFERENCES Dim_PlanoContas(ID_Conta),
        FOREIGN KEY (ID_CentroCusto) REFERENCES Dim_CentroCusto(ID_CentroCusto)
    );
    """)
    
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
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_real_data ON Fatos_Lancamentos_Realizados(Data);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_bgt_data ON Fatos_Orcamento_Planejado(Data);")
    conn.commit()

def run_etl_pipeline():
    """
    Executa o pipeline ETL e atualiza Data Warehouse e CSVs.
    """
    start_time = time.time()
    logger.info("Executando ETL calibrado Alliance One...")
    
    df_accounts, df_cc, df_cal, df_budget, df_real = generate_fpa_data(start_year=2024, end_year=2026)
    df_real_treated, df_budget_treated = apply_corporate_cost_allocation(df_real, df_budget)
    
    conn = sqlite3.connect(DB_PATH)
    create_database_schema(conn)
    
    df_accounts.to_sql("Dim_PlanoContas", conn, if_exists="replace", index=False)
    df_cc.to_sql("Dim_CentroCusto", conn, if_exists="replace", index=False)
    
    df_cal_db = df_cal.copy()
    df_cal_db["Data"] = df_cal_db["Data"].astype(str)
    df_cal_db.to_sql("Dim_Calendario", conn, if_exists="replace", index=False)
    
    df_bgt_db = df_budget_treated.copy()
    df_bgt_db["Data"] = df_bgt_db["Data"].astype(str)
    df_bgt_db.to_sql("Fatos_Orcamento_Planejado", conn, if_exists="replace", index=False)
    
    df_real_db = df_real_treated.copy()
    df_real_db["Data"] = df_real_db["Data"].astype(str)
    df_real_db.to_sql("Fatos_Lancamentos_Realizados", conn, if_exists="replace", index=False)
    
    conn.close()
    
    # Exportação em CSV
    df_accounts.to_csv(DATA_DIR / "Dim_PlanoContas.csv", index=False, sep=";", encoding="utf-8-sig")
    df_cc.to_csv(DATA_DIR / "Dim_CentroCusto.csv", index=False, sep=";", encoding="utf-8-sig")
    df_cal_db.to_csv(DATA_DIR / "Dim_Calendario.csv", index=False, sep=";", encoding="utf-8-sig")
    df_bgt_db.to_csv(DATA_DIR / "Fatos_Orcamento_Planejado.csv", index=False, sep=";", encoding="utf-8-sig")
    df_real_db.to_csv(DATA_DIR / "Fatos_Lancamentos_Realizados.csv", index=False, sep=";", encoding="utf-8-sig")
    
    logger.info(f"ETL calibrado concluído em {round(time.time() - start_time, 2)}s.")

if __name__ == "__main__":
    run_etl_pipeline()
