from openpyxl import Workbook
from ExtratorDiario import Diario
from ExtratorProcesso import ProcessoAposentadoria
from pathlib import Path

class ConstrutorExcel:
    def __init__(self, nome_arquivo):
        self._nome_arquivo = nome_arquivo
        self._wb = Workbook(write_only=True)
        self._wb.create_sheet("Processos Aposentadoria")
        self._ws = self._wb.active

        if self._ws is None : raise ValueError("Não há uma worksheet ativa!")

        # Cabeçalhos
        self._ws.append(['Processo número', 'Assunto', 'Interessado', 'Órgão de Origem', 'Decisão', 'Acórdão', 'Diário número', 'Disponibilização', 'Publicação', 'Arquivo nome'])

    def adicionar_linha(self, diario, processos):
        if self._ws is None : raise ValueError("Não há uma worksheet ativa!")

        for processo in processos:
            self._ws.append([
                processo[0], 
                processo[1], 
                processo[2], 
                processo[3], 
                processo[4],
                processo[5],
                diario[0],
                diario[1],
                diario[2],
                diario[3]
            ])

    def salvar(self, caminho: Path):
        self._wb.save(caminho.joinpath(self._nome_arquivo + ".xlsx"))