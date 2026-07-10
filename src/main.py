from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
from utils import extrair_dados, construir_matriz, ler_linha

import typer, os

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
        
        futuros = {executor.submit(extrair_dados, caminho) for caminho in diarios_caminhos}

        # Construir a matriz de dados
        diarios, processos, processos_offset = construir_matriz(futuros)
    
    # Exportar dados em uma tabela excel
    from ConstrutorExcel import ConstrutorExcel

    try:
        excel = ConstrutorExcel("PROCESSOS_APOSENTADORIAS")

        for idx, _ in enumerate(diarios):
            excel.adicionar_linha(*ler_linha(diarios, processos, processos_offset, idx))
            
        excel.salvar(saida)
    except Exception as err:
        print(f"Erro ao exportar dados para excel: {err}")

if __name__ == "__main__":
    app()
