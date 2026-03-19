# PR Description

## Contexto

Este PR corrige problemas críticos de segurança, estabilidade e versionamento no OCR App, além de preparar o projeto para operação local com documentação e validação mínima.

## Mudanças principais

- remove credencial sensível e endurece o versionamento
- corrige o fluxo de aprendizado incremental
- melhora validações e tratamento de erro na API FastAPI
- adiciona modo mock para OCR local e endpoint `/health`
- reduz risco de XSS no painel web
- adiciona testes automatizados, CI, `.env.example`, `Makefile` e README atualizado
- adiciona documentação operacional e de release

## Impacto

- sem mudança de contrato público relevante nos endpoints já expostos
- endpoint `/ocr` passa a validar melhor uploads inválidos
- endpoint `/aprender` deixa de depender de subprocess frágil
- operação local exige credencial nova via variável de ambiente

## Riscos

- a chave antiga já exposta precisa ser revogada fora do repositório
- persistência em JSON local continua limitada para ambientes concorrentes

## Validação

- testes automatizados com `unittest`
- execução do aprendizado incremental
- revisão de `git status`, `.gitignore` e arquivos rastreados
- confirmação do commit publicado em `origin/main`
