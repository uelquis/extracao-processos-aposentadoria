from pathlib import Path
from src.ExtratorDiario import ExtratorDiario

import typer

app = typer.Typer(add_completion=False, no_args_is_help=True)

@app.command()
def processar(
    entrada: Path = typer.Argument(..., help="Diretório com os arquivos PDF"),
    saida: Path = typer.Argument(..., help="Caminho do arquivo Excel a ser gerado"),
) -> None:
    """Processa os PDFs do diretório informado e gera um arquivo Excel."""

    diarios_caminhos = sorted(entrada.rglob("*.pdf"))
    diarios = []
    
    for diario_caminho in diarios_caminhos[:5]:
        diario = ExtratorDiario().extrair(diario_caminho)
        diarios.append(diario)

    for diario in diarios[:5]: 
        print(diario)

if __name__ == "__main__":
    app()
