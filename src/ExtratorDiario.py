from enum import Enum
from pathlib import Path
from dataclasses import dataclass

import re, pdfplumber

@dataclass(slots=True)
class Diario:
    """Representa um diário."""
    numero: str = ""
    data_disponibilizacao: str = ""
    data_publicacao: str = ""
    arquivo_nome: str = ""

    def __str__(self) -> str:
        return f"Diário {self.numero} - Disponibilização: {self.data_disponibilizacao}, Publicação: {self.data_publicacao}, Arquivo: {self.arquivo_nome}"

class DiarioError(Exception):
    pass

class ExtratorDiario:

    class DataTipo(Enum):
        DISPONIBILIZACAO = "disponibilizacao"
        PUBLICACAO = "publicacao"

    @staticmethod
    def extrair(pdf_caminho: Path) -> Diario:
        with pdfplumber.open(pdf_caminho) as pdf:
            texto = pdf.pages[0].extract_text()

            diario = Diario(
                numero=ExtratorDiario._extrair_numero(texto),
                data_disponibilizacao=ExtratorDiario._extrair_data(texto, ExtratorDiario.DataTipo.DISPONIBILIZACAO),
                data_publicacao=ExtratorDiario._extrair_data(texto, ExtratorDiario.DataTipo.PUBLICACAO),
                arquivo_nome=Path(pdf_caminho).name
            )

        return diario
    
    @staticmethod
    def _extrair_numero(texto: str) -> str:
        match = re.search(r"Edição nº (\d{3}/\d{4})", texto)
        return match.group(1) if match else ""

    @staticmethod
    def _extrair_data(texto: str, tipo: DataTipo) -> str:
        meses = ["janeiro","fevereiro","março","abril","maio","junho","julho","agosto","setembro","outubro","novembro","dezembro"]
        
        if tipo == ExtratorDiario.DataTipo.PUBLICACAO:
            match = re.search(r"Publicação:\s*([^)]*), ([^)]*)", texto, re.IGNORECASE)

            if match is None:
                raise ValueError("Não foi possível extrair a data de publicação do diário.")

            data_crua = match.group(0) # type: ignore
        else:
            match = re.search(r"Disponibilização:\s*([^)]*), ([^)]*)", texto, re.IGNORECASE)

            if match is None:
                raise ValueError("Não foi possível extrair a data de disponibilização do diário.")
            
            data_crua = match.group(0) # type: ignore

        dia = re.search(r"\d{1,2}", data_crua).group(0) # type: ignore
        ano = re.search(r"\d{4}", data_crua).group(0) # type: ignore
        mes = ""
        for i, mes in enumerate(meses):
            if mes in data_crua.lower():
                mes = str(i + 1)
                break
        
        return f"{dia.zfill(2)}-{mes.zfill(2)}-{ano}" 