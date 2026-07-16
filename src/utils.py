
from pathlib import Path
from ExtratorDiario import Diario, ExtratorDiario, DiarioError
from ExtratorProcesso import ExtratorProcesso, ProcessoAposentadoria, ProcessoDeAposentadoriaError
from concurrent.futures import as_completed

import pdfplumber
import traceback

def extrair_dados(diario_caminho: Path) -> tuple[Diario | None, list[ProcessoAposentadoria] | None]:
    
    diario = None
    processos_extraidos = None

    with pdfplumber.open(diario_caminho) as pdf:
        try:
            arquivo_nome = Path(diario_caminho).name
            diario = ExtratorDiario.extrair(pdf, arquivo_nome)
            processos_extraidos = ExtratorProcesso.extrair(pdf, arquivo_nome)
            
        except DiarioError as err:
            print(f"Erro ao extrair dados do diário {diario_caminho}: {err}")
        except ProcessoDeAposentadoriaError as err:
            print(f"Erro ao extrair processos do diário {diario_caminho}: {err}")
        return (diario, processos_extraidos)

def construir_matriz(futuros) -> tuple[list, list, list]:
    """Constrói a matriz de dados a partir dos PDFs informados."""

    diarios : list[Diario] = []
    processos : list[ProcessoAposentadoria] = []
    processos_offset : list[int] = [0]

    for futuro in as_completed(futuros):
        try:
            diario = futuro.result()[0]
            if diario != None: diarios.append(diario)

            processos_extraidos = futuro.result()[1]
            if processos_extraidos is None or []: raise DiarioError(f"O diário {diario.arquivo_nome} não está associado a nenhum processos de aposentadoria!")
            processos.extend(processos_extraidos)

            processos_offset.append(len(processos))
                
        except DiarioError as err:
            print(f'DiarioError ao construir matriz:'.upper())
            traceback.print_exception(err)
            diarios.pop()
        except Exception as err:
            print(f"Erro ao construir matriz:".upper())
            traceback.print_exception(err)

    return (diarios, processos, processos_offset)

def ler_linha(diarios: list, processos: list, processos_offset: list, linha: int) -> tuple:
    """Lê uma linha da matriz de dados e retorna um dicionário com os dados."""

    diario = diarios[linha]
    processo_inicio = processos_offset[linha]
    processo_fim = processos_offset[linha + 1] if linha + 1 < len(processos_offset) else len(processos)
    processos_linha = processos[processo_inicio:processo_fim]

    return diario, processos_linha