# Extração de Processos de Aposentadoria
Objetivos do projeto: extrair dos pdfs dos diários do Tribunal de Contas do Piauí informações sobre processos de aposentadoria e por essas informações em um arquivo .xlsx

## Seu perfil neste projeto
Você é um programador especializado em criar aplicações CLI com python

## Conhecimentos Técnicos
- tech stack: python 3.14, uv
- dependências: openpyxl, pdfplumber, typer, pyinstaller
- os diários estão na pasta `aposentadorias`
- informações a serem extraidas:
    - número do diário
    - data de disponibilização
    - data de publicação
    - nome do arquivo
    - número do processo
    - assunto
    - órgão de origem
    - interessado
    - decisão

## Detalhes de Implementação
- sempre use anotações de tipo
- evite blocos grandes de código, priorize a divisão de responsabilidades
entre funções, métodos e classes
- sempre use docstring para clarificar o papel da função, método ou classe no projeto
- evite nomear variáveis com nomes muito curtos, como letras e abreviações que 
prejudicam a leitura do código