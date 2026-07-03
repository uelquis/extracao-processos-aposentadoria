
from dataclasses import dataclass
from pathlib import Path
import re

import pdfplumber

@dataclass(slots=True)
class ProcessoAposentadoria:
    """Representa um processo extraído de um PDF."""
    numero_processo: str = ""
    interessado: str = ""
    assunto: str = ""
    orgao_origem: str = ""
    decisao: str = ""
    
class ExtratorProcesso:
    
    def extrair(self, pdf_caminho: Path) -> list[ProcessoAposentadoria]:
        with pdfplumber.open(pdf_caminho) as pdf:
            texto_paginas = [page.extract_text() for page in pdf.pages]
            
            filtradas = self.filtrar_paginas(texto_paginas)

        return []
    
    def filtrar_paginas(self, paginas: list[str]) -> list[tuple[int, str]]:
        paginas_com_processo = []
        idx = 0
        for texto in paginas:
            match = re.search(r'ASSUNTO:\s*APOSENTADORIA', texto)
            if match:
                paginas_com_processo.append((idx, texto))
            idx += 1

        return paginas_com_processo