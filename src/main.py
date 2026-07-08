from pathlib import Path
from typing import Dict
from src.ExtratorDiario import Diario, ExtratorDiario
from src.ExtratorProcesso import ExtratorProcesso, ProcessoAposentadoria
from concurrent.futures import ProcessPoolExecutor, as_completed


import typer, os
import numpy as np

app = typer.Typer(add_completion=False, no_args_is_help=True)

@app.command()
def processar(
    entrada: Path = typer.Argument(..., help="Diretório com os arquivos PDF"),
    saida: Path = typer.Argument(..., help="Caminho do arquivo Excel a ser gerado"),
) -> None:
    """Processa os PDFs do diretório informado e gera um arquivo Excel."""

    diarios_caminhos = sorted(entrada.rglob("*.pdf"))


    MAX_PROCESSOS = os.cpu_count()
    with ProcessPoolExecutor(max_workers=MAX_PROCESSOS) as executor:
        
        futuros = {executor.submit(extrair_dados, caminho) for caminho in diarios_caminhos[:1]}

        # Construir a matriz de dados
        diarios, processos, processos_offset = construir_matriz(futuros)
    
    from src.ConstrutorExcel import ConstrutorExcel

    try:
        # Exportar dados em uma tabela excel
        excel = ConstrutorExcel("PROCESSOS_APOSENTADORIAS")

        for idx, _ in enumerate(diarios):
            excel.adicionar_linha(*ler_linha(diarios, processos, processos_offset, idx))
            
        excel.salvar(saida)
    except Exception as err:
        print(f"Erro ao exportar dados para excel: {err}")

def extrair_dados(diario_caminho: Path) -> tuple[Diario | None, list[ProcessoAposentadoria] | None]:
    
    diario = None
    try:
        diario = ExtratorDiario.extrair(diario_caminho)
    except Exception as e:
        print(f"Erro ao processar o diário {diario_caminho}: {e}")

    processos_extraidos = None
    try:
        processos_extraidos = ExtratorProcesso.extrair(diario_caminho)
    except Exception as e:
        print(f"Erro ao processar os processos do diário {diario_caminho}: {e}")

    return (diario, processos_extraidos)
        

def construir_matriz(futuros) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Constrói a matriz de dados a partir dos PDFs informados."""

    tmp_diarios : list[Diario] = []
    tmp_processos : list[ProcessoAposentadoria] = []
    tmp_processos_offset : list[int] = [0]

    for futuro in as_completed(futuros):
        try:
            diario = futuro.result()[0]
            if diario != None: tmp_diarios.append(diario)

            processos_extraidos = futuro.result()[1]
            tmp_processos.extend(processos_extraidos)

            tmp_processos_offset.append(len(tmp_processos))
                
        except Exception as err:
            print(f'Erro ao adquirir resultado das extrações de dados: {err}')

    return (
        np.array(tmp_diarios, dtype=object),
        np.array(tmp_processos, dtype=object),
        np.array(tmp_processos_offset, dtype=np.int32))

def ler_linha(diarios: np.ndarray, processos: np.ndarray, processos_offset: np.ndarray, linha: int) -> tuple:
    """Lê uma linha da matriz de dados e retorna um dicionário com os dados."""

    diario = diarios[linha]
    processo_inicio = processos_offset[linha]
    processo_fim = processos_offset[linha + 1] if linha + 1 < len(processos_offset) else len(processos)
    processos_linha = processos[processo_inicio:processo_fim]

    return diario, processos_linha

if __name__ == "__main__":
    app()
