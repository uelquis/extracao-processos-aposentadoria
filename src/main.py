from pathlib import Path
from typing import Dict
from src.ExtratorDiario import Diario, ExtratorDiario
from src.ExtratorProcesso import ExtratorProcesso, ProcessoAposentadoria

import typer
import numpy as np

app = typer.Typer(add_completion=False, no_args_is_help=True)

@app.command()
def processar(
    entrada: Path = typer.Argument(..., help="Diretório com os arquivos PDF"),
    saida: Path = typer.Argument(..., help="Caminho do arquivo Excel a ser gerado"),
) -> None:
    """Processa os PDFs do diretório informado e gera um arquivo Excel."""

    diarios_caminhos = sorted(entrada.rglob("*.pdf"))

    diarios, processos, processos_offset = construir_matriz(diarios_caminhos)

    # linha = ler_linha(diarios, processos, processos_offset, 0)

    # print("*"*25)
    # print(f"Diário: {linha['diario']}")
    # print(f"Total de processos: {len(linha['processos'])}") # type: ignore
    # for processo in linha['processos']: # type: ignore
    #     print("\n")
    #     print(processo)
    # print("*"*25)

def construir_matriz(caminhos: list[Path]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Constrói a matriz de dados a partir dos PDFs informados."""

    # Construir a matriz de dados
    diarios : list[Diario] = []
    processos : list[ProcessoAposentadoria] = []
    processos_offset : list[int] = []
    
    for diario_caminho in caminhos:
        try:
            diario = ExtratorDiario().extrair(diario_caminho)
            diarios.append(diario)
        except Exception as e:
            print(f"Erro ao processar o diário {diario_caminho}: {e}")
            continue

        try:
            processos_extraidos = ExtratorProcesso().extrair(diario_caminho)

            processos_offset.append(0) if len(processos) == 0 else processos_offset.append(len(processos))

            processos.extend(processos_extraidos)
        except Exception as e:
            print(f"Erro ao processar os processos do diário {diario_caminho}: {e}")
            continue

    # Contruir a matriz de leitura
    diarios_leitura = np.array(diarios, dtype=object)
    processos_leitura = np.array(processos, dtype=object)
    processos_offset_leitura = np.array(processos_offset, dtype=np.int32)

    return diarios_leitura, processos_leitura, processos_offset_leitura

def ler_linha(diarios: np.ndarray, processos: np.ndarray, processos_offset: np.ndarray, linha: int) -> Dict[str, object]:
    """Lê uma linha da matriz de dados e retorna um dicionário com os dados."""

    diario = diarios[linha]
    processo_inicio = processos_offset[linha]
    processo_fim = processos_offset[linha + 1] if linha + 1 < len(processos_offset) else len(processos)
    processos_linha = processos[processo_inicio:processo_fim]

    return {
        "diario": diario,
        "processos": processos_linha
    }

if __name__ == "__main__":
    app()
