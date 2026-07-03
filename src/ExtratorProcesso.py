
from dataclasses import dataclass

@dataclass(slots=True)
class ProcessoAposentadoria:
    """Representa um processo extraído de um PDF."""
    numero_processo: str = ""
    interessado: str = ""
    assunto: str = ""
    orgao_origem: str = ""
    decisao: str = ""
    
class ExtratorProcesso:
    pass
        