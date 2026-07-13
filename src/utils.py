
from pathlib import Path
from ExtratorDiario import Diario, ExtratorDiario, DiarioError
from ExtratorProcesso import ExtratorProcesso, ProcessoAposentadoria, ProcessoDeAposentadoriaError
from concurrent.futures import as_completed

import pyarrow as pa
import traceback

def extrair_dados(diario_caminho: Path) -> tuple[tuple | None, list[ProcessoAposentadoria] | None]:
    
        diario = None
        processos_extraidos = None

        try:
            diario = ExtratorDiario.extrair(diario_caminho)
            processos_extraidos = ExtratorProcesso.extrair(diario_caminho, diario[3])
            
        except DiarioError as err:
            print(f"Erro ao extrair dados do diário {diario_caminho}: {err}")
        except ProcessoDeAposentadoriaError as err:
            print(f"Erro ao extrair processos do diário {diario_caminho}: {err}")

        return (diario, processos_extraidos)

def construir_matriz(futuros):
    """Constrói a matriz de dados a partir dos PDFs informados."""

    tmp_diarios : list[Diario] = []
    tmp_processos : list[ProcessoAposentadoria] = []
    tmp_processos_offset : list[int] = [0]

    for futuro in as_completed(futuros):
        try:
            diario = futuro.result()[0]
            if diario != None: tmp_diarios.append(diario)

            processos_extraidos = futuro.result()[1]
            if processos_extraidos is None or []: raise DiarioError(f"O diário {diario[3]} não está associado a nenhum processos de aposentadoria!")
            tmp_processos.extend(processos_extraidos)

            tmp_processos_offset.append(len(tmp_processos))
                
        except DiarioError as err:
            print(f'DiarioError ao construir matriz:'.upper())
            traceback.print_exception(err)
            tmp_diarios.pop()
        except Exception as err:
            print(f"Erro ao construir matriz:".upper())
            traceback.print_exception(err)

    return (
        pa.array(tmp_diarios),
        pa.array(tmp_processos),
        pa.array(tmp_processos_offset))

def ler_linha(diarios, processos, processos_offset, linha: int) -> tuple:
    """Lê uma linha da matriz de dados e retorna um dicionário com os dados."""

    diario = diarios[linha]
    processo_inicio = processos_offset[linha]
    processo_fim = processos_offset[linha + 1] if linha + 1 < len(processos_offset) else len(processos)
    processos_linha = processos[processo_inicio:processo_fim]

    return diario, processos_linha