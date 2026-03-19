# Release Notes - 2026-03-19

## Resumo

Esta entrega endurece o projeto em quatro frentes:

- segurança de credenciais e higiene de versionamento
- correção do fluxo de aprendizado incremental
- robustez dos endpoints FastAPI e do painel web
- documentação e testes mínimos para operação local

## Principais mudanças

### Segurança

- remoção de credencial Google indevidamente versionada
- uso exclusivo de `GOOGLE_APPLICATION_CREDENTIALS` para carregar credenciais
- endurecimento do `.gitignore` para bloquear credenciais, arquivos de agent e tooling local
- remoção de artefatos locais do índice do Git

### Backend

- correção do endpoint `/aprender` para executar aprendizado de forma nativa
- implementação de regras dinâmicas de parser em `dataset/parser_learning_rules.json`
- centralização de paths de runtime em `app_paths.py`
- centralização de configuração por ambiente em `settings.py`
- nova camada de serviço para OCR em `services/ocr_service.py`
- validação de uploads com tipo, tamanho máximo e conteúdo não vazio
- melhoria no tratamento de exceções e logs
- endpoint `/health` para diagnóstico operacional
- modo `mock` para OCR local sem dependência de credencial externa

### Frontend

- correção da exportação JSON no painel
- redução do risco de XSS com criação segura de elementos DOM
- melhoria de mensagens de erro e carregamento de métricas
- exibição do provider ativo e seleção de quantidade de execuções no painel

### Qualidade

- adição de testes automatizados para parser e API
- adição de testes para camada de serviço de OCR
- atualização do README para refletir o projeto real
- limpeza estrutural do repositório para manter somente arquivos legítimos
- inclusão de `Makefile`, `.env.example` e pipeline CI no GitHub Actions

## Impacto

- o projeto fica mais seguro para colaboração e publicação
- o fluxo de OCR e aprendizado fica previsível e testável
- a operação local passa a depender explicitamente de uma nova credencial válida do Google Cloud Vision

## Risco remanescente

- a credencial antiga deve ser tratada como comprometida e precisa ser revogada no Google Cloud
- o projeto ainda usa persistência em arquivos locais, o que não é adequado para concorrência ou produção real

## Validação executada

- `venv/bin/python -m unittest discover -s tests`
- `venv/bin/python -m parser.learn_parser`
- verificação de higiene Git e confirmação de publicação em `origin/main`
