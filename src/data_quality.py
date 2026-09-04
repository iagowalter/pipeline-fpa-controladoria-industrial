"""
Módulo de Auditoria e Testes de Qualidade de Dados (Data Quality / DataOps)
Projeto: FP&A & Controladoria Industrial (Beneficiamento de Tabaco)

Este módulo implementa uma suíte de testes automatizados para validar a integridade
estrutural, contábil e dimensional antes da liberação dos dados para a camada analítica.
"""

import sqlite3
import pandas as pd
from pathlib import Path
from config import get_logger, DB_PATH

logger = get_logger("data_quality")

class DataQualityAuditor:
    """
    Motor de testes e validação de qualidade de dados do Data Warehouse.
    """
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.test_results = []

    def log_result(self, test_name: str, passed: bool, details: str):
        status = "APROVADO [PASS]" if passed else "REPROVADO [FAIL]"
        self.test_results.append({
            "Teste": test_name,
            "Status": status,
            "Detalhes": details
        })
        if passed:
            logger.info(f"TESTE '{test_name}': {status} - {details}")
        else:
            logger.error(f"TESTE '{test_name}': {status} - {details}")

    def test_null_keys(self):
        """Teste 1: Valida ausência de nulos em chaves primárias e estrangeiras."""
        queries = [
            ("Fatos_Lancamentos_Realizados - Nulos em Chaves", 
             "SELECT COUNT(*) FROM Fatos_Lancamentos_Realizados WHERE ID_Lancamento IS NULL OR Data IS NULL OR ID_Conta IS NULL OR ID_CentroCusto IS NULL;"),
            ("Fatos_Orcamento_Planejado - Nulos em Chaves", 
             "SELECT COUNT(*) FROM Fatos_Orcamento_Planejado WHERE AnoMes IS NULL OR ID_Conta IS NULL OR ID_CentroCusto IS NULL;")
        ]
        for name, q in queries:
            cursor = self.conn.cursor()
            count = cursor.execute(q).fetchone()[0]
            passed = (count == 0)
            self.log_result(name, passed, f"Registros com chave nula encontrados: {count}")

    def test_referential_integrity(self):
        """Teste 2: Garante que não existem chaves órfãs entre Fatos e Dimensões."""
        queries = [
            ("Integridade Referencial - Contas Contábeis (Realizado)",
             "SELECT COUNT(*) FROM Fatos_Lancamentos_Realizados f LEFT JOIN Dim_PlanoContas d ON f.ID_Conta = d.ID_Conta WHERE d.ID_Conta IS NULL;"),
            ("Integridade Referencial - Centros de Custo (Realizado)",
             "SELECT COUNT(*) FROM Fatos_Lancamentos_Realizados f LEFT JOIN Dim_CentroCusto d ON f.ID_CentroCusto = d.ID_CentroCusto WHERE d.ID_CentroCusto IS NULL;"),
            ("Integridade Referencial - Contas Contábeis (Orçamento)",
             "SELECT COUNT(*) FROM Fatos_Orcamento_Planejado f LEFT JOIN Dim_PlanoContas d ON f.ID_Conta = d.ID_Conta WHERE d.ID_Conta IS NULL;"),
            ("Integridade Referencial - Centros de Custo (Orçamento)",
             "SELECT COUNT(*) FROM Fatos_Orcamento_Planejado f LEFT JOIN Dim_CentroCusto d ON f.ID_CentroCusto = d.ID_CentroCusto WHERE d.ID_CentroCusto IS NULL;")
        ]
        for name, q in queries:
            cursor = self.conn.cursor()
            count = cursor.execute(q).fetchone()[0]
            passed = (count == 0)
            self.log_result(name, passed, f"Chaves órfãs identificadas: {count}")

    def test_values_validity(self):
        """Teste 3: Validação de valores numéricos e consistência de sinal contábil."""
        q = "SELECT COUNT(*) FROM Fatos_Lancamentos_Realizados WHERE Valor_Realizado <= 0;"
        cursor = self.conn.cursor()
        count = cursor.execute(q).fetchone()[0]
        passed = (count == 0)
        self.log_result("Consistência de Valores Positivos (Realizado)", passed, f"Lançamentos com valor zero ou negativo: {count}")

    def test_date_range(self):
        """Teste 4: Validação dos limites de data do calendário fiscal."""
        q = "SELECT MIN(Data), MAX(Data) FROM Fatos_Lancamentos_Realizados;"
        cursor = self.conn.cursor()
        min_date, max_date = cursor.execute(q).fetchone()
        passed = (min_date >= "2024-01-01" and max_date <= "2026-12-31")
        self.log_result("Limites Temporais do Calendário", passed, f"Intervalo observado: {min_date} a {max_date}")

    def run_all_tests(self) -> bool:
        """Executa toda a suíte de qualidade de dados."""
        logger.info("================================================================================")
        logger.info("INICIANDO SUÍTE DE TESTES DE DATA QUALITY & AUDITORIA CONTÁBIL")
        logger.info("================================================================================")
        
        self.test_null_keys()
        self.test_referential_integrity()
        self.test_values_validity()
        self.test_date_range()
        
        self.conn.close()
        
        all_passed = all(r["Status"] == "APROVADO [PASS]" for r in self.test_results)
        logger.info("================================================================================")
        logger.info(f"AUDITORIA CONCLUÍDA. RESULTADO GERAL: {'100% APROVADO' if all_passed else 'FALHAS DETECTADAS'}")
        logger.info("================================================================================")
        return all_passed

if __name__ == "__main__":
    auditor = DataQualityAuditor()
    auditor.run_all_tests()
