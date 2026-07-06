
from dataclasses import dataclass
from pathlib import Path
from itertools import chain
from pdfplumber.page import Page
import re, pdfplumber

@dataclass(slots=True)
class ProcessoAposentadoria:
    """Representa um processo extraído de um PDF."""
    numero: str = ""
    interessado: str = ""
    assunto: str = ""
    orgao_origem: str = ""
    decisao: str = ""
    
    def __str__(self) -> str:
        return f"Processo: {self.numero} \nInteressado: {self.interessado} \nAssunto: {self.assunto} \nÓrgão de Origem: {self.orgao_origem} \nDecisão: {self.decisao}"

class ExtratorProcesso:
    
    def extrair(self, pdf_caminho: Path) -> list[ProcessoAposentadoria]:
        with pdfplumber.open(pdf_caminho) as pdf:
            
            filtradas = self._filtrar_paginas(self._extrair_texto_das_paginas(pdf.pages))

            processos = [self._extrair_processo(texto) for texto in filtradas]
            
        return list(chain.from_iterable(processos))
    
    def _filtrar_paginas(self, paginas: list[str]) -> list[str]:
        """
        Filtra as páginas que contêm processos de aposentadoria.
        Retorna uma lista que contém os textos das páginas que contêm processos de aposentadoria.
        """
        paginas_com_processo = []
        idx = 0
        for texto in paginas:
            match = re.search(r'ASSUNTO:\s*APOSENTADORIA', texto)
            if match:
                paginas_com_processo.append(texto)
            idx += 1

        return paginas_com_processo
    
    def _extrair_processo(self, texto: str) -> list[ProcessoAposentadoria]:
        """
        Extrai os processos de aposentadoria do texto da página.
        Retorna uma lista de objetos ProcessoAposentadoria.
        """
        processos = []

        processos_numeros = self._extrair_numeros_dos_processos(texto)
        processos_assuntos = self._extrair_assuntos_dos_processos(texto)
        interessados = self._extrair_interessados_dos_processos(texto)
        
        [processos.append(ProcessoAposentadoria(
            numero=numero, 
            assunto=processos_assuntos[processos_numeros.index(numero)].replace('\n', ' '),
            # interessado=interessados[processos_numeros.index(numero)]
            # orgao_de_origem
            # decisao

        )) for numero in processos_numeros]

        return processos
    
    def _extrair_texto_das_paginas(self, paginas : list[Page]) -> list[str]:
        """
        Extrair o texto das páginas em duas listas que represetam as colunas no PDF.
        Retorna uma lista que contém os textos de ambas as colunas das páginas do PDF.
        """
        textos_coluna_esquerda = []
        textos_coluna_direita = []

        for pagina in paginas:
            largura, altura = pagina.width, pagina.height
            meio = largura / 2

            # Definir as caixas de corte para cada coluna
            caixa_esquerda = (0, 0, meio, altura)
            caixa_direita = (meio, 0, largura, altura)

            # Extrair o texto de cada coluna
            texto_esquerda = pagina.within_bbox(caixa_esquerda).extract_text()
            texto_direita = pagina.within_bbox(caixa_direita).extract_text()

            textos_coluna_esquerda.append(texto_esquerda)
            textos_coluna_direita.append(texto_direita)

        return textos_coluna_esquerda + textos_coluna_direita

    def _extrair_numeros_dos_processos(self, texto: str) -> list[str]:
        return re.findall(r'\bPROCESSO:?\s*TC[:\s/]*N?[º°]?\s*(\d{6}\/\d{4})\b', texto)
    
    def _extrair_assuntos_dos_processos(self, texto: str) -> list[str]:
        return re.findall(r'ASSUNTO:[\s\xA0]*(.+?)(?=\n[A-Z]+:|$)', texto, re.DOTALL)


    def _extrair_interessados_dos_processos(self, texto: str) -> list[str]:
        return re.findall(r'INTERESSAD[OA](?:[\s\xA0]*\(A\))?[\s\xA0]*:[\s\xA0]*(.+?)(?=\n[A-Z]+:|$)', texto, re.DOTALL)


        
