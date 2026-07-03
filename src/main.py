from pathlib import Path
from typing import Dict
from src.ExtratorDiario import Diario, ExtratorDiario
from src.ExtratorProcesso import ExtratorProcesso, ProcessoAposentadoria

import typer

app = typer.Typer(add_completion=False, no_args_is_help=True)

@app.command()
def processar(
    entrada: Path = typer.Argument(..., help="Diretório com os arquivos PDF"),
    saida: Path = typer.Argument(..., help="Caminho do arquivo Excel a ser gerado"),
) -> None:
    """Processa os PDFs do diretório informado e gera um arquivo Excel."""

    diarios_caminhos = sorted(entrada.rglob("*.pdf"))
    processos : Dict[Diario, list[ProcessoAposentadoria]] = {}
    
    for diario_caminho in diarios_caminhos[:5]:
        diario = ExtratorDiario().extrair(diario_caminho)

        processos[diario].extend(ExtratorProcesso().extrair(diario_caminho))

    for diario in list(processos.keys())[:5]: 
        print(diario)

    for diario in processos.keys():
        for processo in processos[diario]:
            print(processo)

if __name__ == "__main__":
    app()
