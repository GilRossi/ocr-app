# OCR App - Painel Interativo de Correção de Promoções

Sistema de OCR para leitura de encartes promocionais com **FastAPI**, extração estruturada de promoções e um painel web para revisão manual dos resultados, coleta de feedback e acompanhamento de métricas de acerto.

---

## 🚀 Tecnologias Utilizadas

* **Python 3.12**
* **FastAPI**
* **Uvicorn**
* **Google Cloud Vision API**
* **HTML, CSS e JavaScript**
* **Matplotlib**
* **JSON** para persistência local de resultados e feedbacks

---

## 📂 Estrutura do Projeto

```text
ocr-app/
│
├── main.py                          # API FastAPI e endpoints principais
├── ocr_pipeline.py                  # Pipeline batch para imagens locais
├── requirements.txt                 # Dependências do projeto
│
├── parser/
│   ├── adaptive_parser.py           # OCR repetido + persistência em dataset
│   ├── base_parser.py               # Regras de extração das promoções
│   ├── learn_parser.py              # Fluxo de aprendizado baseado em feedback
│   └── utils.py                     # Utilitários de cópia do último JSON
│
├── pipeline/
│   └── ajustar_parser.py            # Comparação entre dataset e parser atual
│
├── scripts/
│   ├── atualizar_ultimo_json.py     # Copia o JSON mais recente para o painel
│   └── grafico_aprendizado.py       # Gera gráfico de precisão dos feedbacks
│
├── public/
│   ├── painel/index.html            # Interface web de revisão
│   ├── ultimoreconhecimento.json    # Último resultado consumido pelo painel
│   └── resultado.json               # Artefato auxiliar
│
├── dataset/                         # Resultados OCR e amostras para análise
├── feedbacks/                       # Correções feitas no painel
└── grafico_aprendizado.png          # Gráfico gerado a partir dos feedbacks
```

---

## 🛠 Arquitetura e Princípios

### Separação por responsabilidade

* `main.py` expõe a API HTTP e serve o painel web.
* `parser/` concentra a extração das promoções a partir do texto reconhecido.
* `scripts/` e `pipeline/` apoiam análise, sincronização de artefatos e avaliação local.
* `public/` contém a interface de revisão usada para correção humana.

### Fluxo orientado a feedback

* O OCR gera um JSON com o texto bruto e os resultados do parser.
* O painel permite corrigir promoções e marcar itens como `ok` ou `ajustar`.
* Os feedbacks alimentam métricas e o fluxo de aprendizado incremental.

### Persistência simples

* O projeto usa arquivos `.json` locais em vez de banco de dados.
* Isso simplifica prototipação, mas exige cuidado com versionamento e higiene de artefatos.

---

## ✨ Funcionalidades Principais

### 📷 OCR de imagens promocionais

* Upload de imagem via endpoint `/ocr`
* Processamento usando Google Cloud Vision
* Geração de hash e versionamento do resultado por timestamp

### 🧠 Parser de promoções

* Extração de nome do produto, preço original, preço promocional e condição
* Limpeza básica de ruído textual do OCR
* Suporte a múltiplas execuções de OCR para a mesma imagem

### 🖥 Painel de revisão

* Upload de imagem diretamente no navegador
* Edição manual dos campos extraídos
* Marcação visual de itens corretos ou a ajustar

### 💬 Coleta de feedback

* Envio de correções para a pasta `feedbacks/`
* Reaproveitamento das correções para análise posterior
* Exibição de precisão agregada no painel

### 📊 Métricas e gráfico

* Endpoint `/metricas` com total de feedbacks e precisão atual
* Endpoint `/grafico` para visualização da evolução dos feedbacks
* Script dedicado para gerar `grafico_aprendizado.png`

---

## 🌐 Endpoints Disponíveis

* `GET /` redireciona para o painel
* `POST /ocr` processa uma imagem enviada
* `POST /feedback` salva correções enviadas pelo painel
* `POST /atualizar-json` publica o último JSON gerado
* `POST /aprender` executa o fluxo de aprendizado incremental
* `GET /metricas` retorna precisão com base nos feedbacks
* `GET /grafico` retorna a imagem do gráfico gerado

---

## 🚀 Como Executar

### Pré-requisitos

* Python 3.12+
* Conta Google Cloud com Vision API habilitada
* Arquivo de credenciais de service account

### Configuração do ambiente

1. **Clonar o repositório**
```bash
git clone <url-do-repositorio>
cd ocr-app
```

2. **Criar e ativar ambiente virtual**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. **Instalar dependências**
```bash
pip install -r requirements.txt
```

4. **Configurar credenciais do Google Vision**
```bash
export GOOGLE_APPLICATION_CREDENTIALS=/caminho/para/sua-service-account.json
```

As credenciais devem ficar fora do repositório.

5. **Executar a aplicação**
```bash
uvicorn main:app --reload
```

6. **Acessar o sistema**
* Painel web: http://127.0.0.1:8000/painel
* Documentação da API: http://127.0.0.1:8000/docs

---

## 🧪 Scripts Úteis

### Gerar gráfico de aprendizado

```bash
python3 scripts/grafico_aprendizado.py
```

### Rodar pipeline batch local

```bash
python3 ocr_pipeline.py
```

### Publicar o último JSON no painel

```bash
python3 scripts/atualizar_ultimo_json.py
```

### Rodar ajuste comparativo com dataset

```bash
python3 pipeline/ajustar_parser.py
```

### Executar testes automatizados

```bash
python3 -m unittest discover -s tests
```

---

## 📘 Documentação Operacional

* [Checklist Operacional](docs/OPERATIONS_CHECKLIST.md)
* [Notas de Release](docs/RELEASE_NOTES_2026-03-19.md)
* [Descrição de PR](docs/PR_DESCRIPTION.md)

---

## 📋 Fluxos Principais

### Fluxo OCR

```text
Imagem -> Google Vision -> Texto OCR -> Parser -> JSON em dataset -> Painel
```

### Fluxo de Correção

```text
Painel -> Edição manual -> Feedback JSON -> Métricas -> Aprendizado
```

### Fluxo de Avaliação

```text
Dataset salvo -> Comparação com parser atual -> Resumo de similaridade
```

---

## ⚠️ Limitações Atuais

* O parser é heurístico e depende fortemente do formato do encarte.
* A persistência local em arquivos JSON não é adequada para uso concorrente ou produção.
* O fluxo de aprendizado incremental ainda é heurístico e deve evoluir com regras mais específicas.
* A suíte automatizada atual cobre os fluxos críticos básicos, mas ainda não cobre integração real com Google Vision.

---

## 📚 Próximos Passos

* Adicionar testes automatizados para parser e endpoints
* Externalizar configurações e caminhos para variáveis de ambiente
* Remover artefatos gerados e credenciais do versionamento
* Melhorar a estratégia de aprendizado a partir dos feedbacks
* Evoluir o parser para modelos mais resilientes a ruído de OCR

---

## 👨‍💻 Autor

**Gil Rossi Aguiar**  
📧 [gilrossi.aguiar@live.com](mailto:gilrossi.aguiar@live.com)  
💼 [LinkedIn](https://www.linkedin.com/in/gil-rossi-5814659b/)  
🐙 [GitHub](https://github.com/GilRossi)
