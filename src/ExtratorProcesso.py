
from dataclasses import dataclass
from pathlib import Path
from itertools import chain
from pdfplumber.page import Page
import re, pdfplumber
from enum import Enum

@dataclass(slots=True)
class ProcessoAposentadoria:
    """Representa um processo extraído de um PDF."""
    numero: str = ""
    interessado: str = ""
    assunto: str = ""
    orgao_origem: str = ""
    decisao: str = ""
    acordao: str = ""
    
    def __str__(self) -> str:
        return f"Processo: {self.numero} \nInteressado: {self.interessado} \nAssunto: {self.assunto} \nÓrgão de Origem: {self.orgao_origem} \nDecisão: {self.decisao} \nAcórdão: {self.acordao}"

class ProcessoDeAposentadoriaError(Exception):
     pass

class Padroes(Enum):
    ASSUNTO = r'ASSUNTO:[\s\xA0]*(APOSENTADORIA[\s\S]+?)(?=(?:\.\s+|\n[ \t]*)[A-ZÁÉÍÓÚÂÊÔÃÕÇ \(\)]+:|$)'
    DECISAO = r'(DECISÃO\b(?!\s*MONOCR[ÁA]TICA\b)[\s\S]+?)(?=(?:\.\s+|\n[ \t]*)[A-ZÁÉÍÓÚÂÊÔÃÕÇ \(\)]+:|\n\s*[A-ZÁÉÍÓÚÂÊÔÃÕÇ]?[a-záéíóúâêôãõç]|$)'
    INTERESSADO = r'INTERESSS?[AD]{0,2}[OA](?:[\s\xA0]*\(A\))?[\s\xA0]*([\s\S]+?)(?=(?:\.\s+|\n[ \t]*)[A-ZÁÉÍÓÚÂÊÔÃÕÇ \(\)]+:|$)'
    PROCESSO = r'\bPROCESSO:?\s*TC[:\s/]*[Nn]?\.?[º°]?\s*(\d{3}\.?\d{3}\/\d{4})\b'
    ACORDAO = r'(AC[ÓO]RD[ÃA]O[\s\xA0][A-ZÁÉÍÓÚÂÊÔÃÕÇ0-9nº°№ \t\-\–\—\/\\.,\(\)]+)(?:\n[ \t]*(?![A-ZÁÉÍÓÚÂÊÔÃÕÇ \(\)]+:)[A-ZÁÉÍÓÚÂÊÔÃÕÇ0-9nº°№ \t\-\–\—\/\\.,\(\)]+)*'
    ORGAO_ORIGEM = r'(?:[ÓO]RG[ÃA]O DE ORIGEM|PROCED[ÊE]NCIA|UNIDADE GESTORA):?[\s\xA0]*([\s\S]+?)(?=(?:\.\s+|\n[ \t]*)[A-ZÁÉÍÓÚÂÊÔÃÕÇ \(\)]+:|$)'

class ExtratorProcesso:

    @staticmethod
    def extrair(pdf_caminho: Path, diario_nome: str) -> list[ProcessoAposentadoria]:
        with pdfplumber.open(pdf_caminho) as pdf:
            
            filtradas = ExtratorProcesso._filtrar_paginas(ExtratorProcesso._extrair_texto_das_paginas(pdf.pages))

            processos = [ExtratorProcesso._extrair_processo(texto, diario_nome) for texto in filtradas]
            
        return list(chain.from_iterable(processos))
    
    @staticmethod
    def _filtrar_paginas( paginas: list[str]) -> list[str]:
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
    
    @staticmethod
    def _extrair_processo( texto: str, diario_nome: str) -> list[ProcessoAposentadoria]:
        """
        Extrai os processos de aposentadoria do texto da página.
        Retorna uma lista de objetos ProcessoAposentadoria.
        """
        processos = []

        processos_numeros = ExtratorProcesso._extrair_numeros_dos_processos(texto)
        processos_assuntos = ExtratorProcesso._extrair_assuntos_dos_processos(texto)
        interessados = ExtratorProcesso._extrair_interessados_dos_processos(texto)
        decisoes = ExtratorProcesso._extrair_numeros_das_decisoes(texto)
        orgaos_origem = ExtratorProcesso._extrair_orgaos_de_origem(texto)
        acordaos = ExtratorProcesso._extrair_acordaos(texto)

        for idx, numero in enumerate(processos_numeros):
            try:
                processos.append(ProcessoAposentadoria(
                    numero=numero, 
                    assunto=processos_assuntos[idx],
                    interessado=interessados[idx],
                    orgao_origem=orgaos_origem[idx],
                    decisao=decisoes[idx],
                    acordao=acordaos[idx]
                ))
            except Exception as err:
                print(f"Erro ao extrair processo: {numero} do diario: {diario_nome}! : {err}")


        return processos
    
    @staticmethod
    def _extrair_texto_das_paginas(paginas : list[Page]) -> list[str]:
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
        
        # ordernar os textos das colunas
        textos = []
        for i in range(len(textos_coluna_esquerda)):
            if textos_coluna_esquerda[i] is None:
                raise ValueError(f"Erro ao extrair o texto da coluna esquerda da página {i}. O texto extraído é vazio.")
            if textos_coluna_direita[i] is None:
                raise ValueError(f"Erro ao extrair o texto da coluna direita da página {i}. O texto extraído é vazio.")
            
            textos.append(textos_coluna_esquerda[i] + textos_coluna_direita[i])

        return textos

    @staticmethod
    def _extrair_numeros_dos_processos(texto: str) -> list[str]:
        processos = []

        DISTANCIA = 500

        for match in re.finditer(Padroes.ASSUNTO.value, texto, re.DOTALL):
            start_idx = max(0, match.start() - DISTANCIA)
            end_idx = min(len(texto), match.end() + DISTANCIA)
            chunk = texto[start_idx:end_idx]
            
            processo_pattern = Padroes.PROCESSO.value
            processo_match = re.search(processo_pattern, chunk)
            
            if processo_match is None: continue

            processos.append(processo_match.group(1)) # type: ignore
                
        return processos
    
    @staticmethod
    def _extrair_assuntos_dos_processos(texto: str) -> list[str]:
        return re.findall(Padroes.ASSUNTO.value, texto, re.DOTALL)

    @staticmethod
    def _extrair_interessados_dos_processos(texto: str) -> list[str]:
        matches = re.findall(Padroes.INTERESSADO.value, texto, re.DOTALL)
        
        return [m.strip(':') for m in matches]

    @staticmethod
    def _extrair_numeros_das_decisoes(texto: str) -> list[str]:
        decisoes = []
    
        DISTANCIA = 500

        for match in re.finditer(Padroes.ASSUNTO.value, texto):

            start_idx = max(0, match.start() - DISTANCIA)
            end_idx = min(len(texto), match.end() + DISTANCIA)
            chunk = texto[start_idx:end_idx]
            
            decisao_pattern = Padroes.DECISAO.value
            decisao_match = re.search(decisao_pattern, chunk)
            
            if decisao_match:
                decisoes.append(decisao_match.group(1).strip())
            else:
                decisoes.append("")
                
        return decisoes

    @staticmethod
    def _extrair_orgaos_de_origem(texto: str) -> list[str]:
        orgaos_de_origem = []
    
        DISTANCIA = 500

        for match in re.finditer(Padroes.ASSUNTO.value, texto, re.DOTALL):
            start_idx = max(0, match.start() - DISTANCIA)
            end_idx = min(len(texto), match.end() + DISTANCIA)
            chunk = texto[start_idx:end_idx]
            
            orgao_match = re.search(Padroes.ORGAO_ORIGEM.value, chunk)
            
            if orgao_match:
                orgaos_de_origem.append(orgao_match.group(1).strip())
            else:
                orgaos_de_origem.append("")

        return orgaos_de_origem
    
    @staticmethod
    def _extrair_acordaos(texto: str) -> list[str]:
        acordaos = []
    
        DISTANCIA = 500

        for match in re.finditer(Padroes.ASSUNTO.value, texto, re.DOTALL):
            start_idx = max(0, match.start() - DISTANCIA)
            end_idx = min(len(texto), match.end() + DISTANCIA)
            chunk = texto[start_idx:end_idx]
            
            orgao_match = re.search(Padroes.ACORDAO.value, chunk)
            
            if orgao_match:
                acordaos.append(orgao_match.group(1).strip())
            else:
                acordaos.append("")

        return acordaos
    

        
    