# Checklist Operacional

## 1. Rotação de credencial Google

- revogar a service account key antiga no Google Cloud
- gerar uma nova chave apenas para o ambiente necessário
- armazenar o JSON fora do repositório
- definir a variável `GOOGLE_APPLICATION_CREDENTIALS` apontando para o novo arquivo
- validar no shell com `echo $GOOGLE_APPLICATION_CREDENTIALS`

## 2. Subida local

```bash
cd /home/gil/workspace/claude/ocr-app
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export OCR_PROVIDER=mock
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

Para OCR real:

```bash
export OCR_PROVIDER=google
export GOOGLE_APPLICATION_CREDENTIALS=/caminho/seguro/nova-service-account.json
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

## 3. Teste local mínimo

- abrir `http://127.0.0.1:8000/painel`
- abrir `http://127.0.0.1:8000/docs`
- abrir `http://127.0.0.1:8000/health`
- rodar `python -m unittest discover -s tests`
- enviar uma imagem real no painel
- confirmar geração de JSON em `dataset/`
- confirmar atualização do painel com as promoções extraídas
- enviar feedback e verificar criação de arquivo em `feedbacks/`
- executar `POST /aprender` e verificar geração de `grafico_aprendizado.png`

## 4. Checklist antes de produção

- confirmar Vision API habilitada no projeto GCP correto
- usar credencial dedicada por ambiente
- não compartilhar o arquivo JSON por e-mail, chat ou repositório
- monitorar permissões da service account com privilégio mínimo
- revisar retenção e limpeza de `dataset/` e `feedbacks/`
- definir estratégia de backup e limpeza de artefatos locais
- considerar storage persistente e banco de dados antes de uso multiusuário

## 5. Checklist antes de novo push

- rodar `git status --short`
- garantir ausência de `AGENTS.md`, `SKILL.md`, `.env`, credenciais e artefatos locais
- revisar `.gitignore` se houver novo tooling local
- validar testes afetados pela mudança
- revisar diff final antes do `git push`
