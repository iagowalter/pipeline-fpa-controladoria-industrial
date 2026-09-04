"""
Módulo de Configuração e Sistema de Logs (DataOps)
Projeto: Pipeline de FP&A & Controladoria Industrial (Beneficiamento de Tabaco)

Este módulo centraliza os parâmetros de ambiente, caminhos de diretórios e
estabelece o pipeline de rastreabilidade (logging) para registrar cada etapa de execução.
"""

import os
import sys
import logging
from pathlib import Path

# Definição dinâmica de diretórios para evitar caminhos absolutos fixos
BASE_DIR = Path(__file__).resolve().parent.parent
LOGS_DIR = BASE_DIR / "logs"
DATA_DIR = BASE_DIR / "data"
SQL_DIR = BASE_DIR / "sql"

# Garantia de existência dos diretórios fundamentais
LOGS_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Definição do caminho padrão do banco de dados relacional (Data Warehouse)
DB_PATH = DATA_DIR / "fpa_industrial_dw.db"
LOG_FILE_PATH = LOGS_DIR / "pipeline_fpa.log"

def get_logger(name: str = "fpa_pipeline") -> logging.Logger:
    """
    Inicializa e configura um registrador de eventos (logger) padronizado.
    
    Grava mensagens simultaneamente no arquivo logs/pipeline_fpa.log e no console (stdout),
    assegurando rastreabilidade total de auditoria para o processo de engenharia de dados.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Evita adicionar múltiplos handlers caso o logger já esteja instanciado
    if not logger.handlers:
        # Formatação das mensagens de log com timestamp, nível e módulo
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] (%(module)s) %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # Handler 1: Gravação em arquivo físico para auditoria
        file_handler = logging.FileHandler(LOG_FILE_PATH, encoding="utf-8")
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Handler 2: Exibição no console para acompanhamento em tempo real
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger

if __name__ == "__main__":
    test_logger = get_logger("config_test")
    test_logger.info("Sistema de configurações e logging inicializado com sucesso.")
