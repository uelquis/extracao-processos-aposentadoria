# Extração de Processos de Aposentadoria

Este projeto possui uma CLI em Python para processar arquivos PDF localizados em uma pasta e gerar um arquivo Excel com os dados extraídos.

## Instalação

```bash
python -m pip install -e '.[test]'
```

## Uso

```bash
python -m src.main processar caminho/para/pdfs caminho/para/resultado.xlsx
```

Ou, após a instalação do script de console:

```bash
extracao-processos-aposentadoria processar caminho/para/pdfs caminho/para/resultado.xlsx
```
