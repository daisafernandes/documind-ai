# DocuMind AI

API em Python e FastAPI para receber e preparar documentos PDF para uma aplicação de RAG (*Retrieval-Augmented Generation*), técnica que usa conteúdo recuperado de documentos como contexto para gerar respostas.

O projeto está em desenvolvimento. Atualmente, oferece upload e validação de PDFs, serviços de extração de texto e duas estratégias de divisão de conteúdo em trechos (*chunks*).

## Funcionalidades

- Upload de PDFs de até 10 MiB (10 × 1024 × 1024 bytes).
- Validação de integridade, presença de páginas e proteção por senha.
- Armazenamento local com identificador UUID.
- Extração de texto por página com PyMuPDF.
- Divisão por quantidade de caracteres, com sobreposição configurável.
- Divisão por parágrafos, com corte de parágrafos maiores que o limite.
- Preservação do identificador do documento e das páginas de origem em cada trecho.
- Endpoint de saúde e documentação interativa da API.

O upload salva e valida o arquivo, retornando o status `pending`. Ainda não existe um processamento automático posterior, consulta de status, busca vetorial ou geração de respostas. A extração e o chunking são serviços internos, sem endpoints próprios. A extração utiliza o texto disponível no PDF; não há OCR para documentos digitalizados.

## Tecnologias

- Python, FastAPI e Uvicorn.
- Pydantic para os modelos de dados.
- PyMuPDF para leitura e validação de PDFs.
- pytest e HTTPX para testes.

## Instalação

Execute os comandos na raiz do repositório. O ambiente de desenvolvimento presente no projeto utiliza Python 3.14; outras versões não foram verificadas.

Crie um ambiente virtual:

```powershell
python -m venv .venv
```

Ative no Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

No Linux ou macOS:

```bash
source .venv/bin/activate
```

Instale as dependências da API e dos testes com pip 25.1 ou superior:

```bash
python -m pip install --upgrade pip
python -m pip install --group app --group dev
```

Os grupos estão declarados no `pyproject.toml`. Execute o comando na raiz do repositório para que o pip encontre esse arquivo.

| Grupo | Uso |
| --- | --- |
| `app` | Execução da API e processamento de PDFs. |
| `dev` | Execução dos testes. |
| `experiments` | Experimentos com embeddings usando Sentence Transformers. |

Para executar apenas a API, instale com `python -m pip install --group app`. Para instalar também as dependências dos experimentos com embeddings:

```bash
python -m pip install --group experiments
```

Para adicionar ou atualizar uma dependência, edite a versão no grupo correspondente do `pyproject.toml` e execute novamente a instalação desse grupo. O pip não atualiza esse arquivo automaticamente ao instalar um pacote.

As dependências diretas têm versões fixadas. Sem um arquivo de lock, as versões das dependências transitivas podem variar entre instalações.

## Execução

```bash
python -m uvicorn app.main:app --reload
```

- API: <http://127.0.0.1:8000>
- Swagger UI: <http://127.0.0.1:8000/docs>
- ReDoc: <http://127.0.0.1:8000/redoc>
- Esquema OpenAPI: <http://127.0.0.1:8000/openapi.json>

Não há variáveis de ambiente obrigatórias na implementação atual. Os uploads são gravados em `storage/uploads/`, relativo ao diretório de execução. A pasta é criada automaticamente e está ignorada pelo Git.

## Endpoints

### `GET /health`

Retorna HTTP `200`:

```json
{
  "status": "ok",
  "server": "documind-ai"
}
```

### `POST /documents`

Recebe um formulário `multipart/form-data` com o campo `file`. O arquivo deve ser enviado com o tipo `application/pdf`.

Exemplo com curl (no PowerShell, use `curl.exe`):

```bash
curl -X POST http://127.0.0.1:8000/documents -F "file=@documento.pdf;type=application/pdf"
```

Resposta HTTP `202`:

```json
{
  "document_id": "f7385f1a-bf45-4acd-9198-21b16e118e38",
  "filename": "documento.pdf",
  "status": "pending"
}
```

O arquivo fica salvo em `storage/uploads/<document_id>.pdf`. Arquivos inválidos ou que excedem o limite são removidos durante o tratamento do erro.

| Código | Situação |
| --- | --- |
| `202` | PDF validado e armazenado. |
| `413` | Arquivo maior que 10 MiB. |
| `415` | Tipo de conteúdo diferente de `application/pdf`. |
| `422` | PDF inválido, corrompido, protegido por senha ou sem páginas; também ocorre se o campo obrigatório estiver ausente. |

## Serviços de processamento

`PDFService.extract_text(content, document_id)` recebe os bytes do PDF e retorna um `ExtractedDocument` com o total de páginas e o texto de cada página, numerada a partir de 1.

`ChunkingService` utiliza, por padrão, trechos de até 500 caracteres com sobreposição de 100 caracteres. `ParagraphChunkingService` agrupa parágrafos até 500 caracteres e divide os maiores sem sobreposição. Os limites são medidos em caracteres, não em tokens.

Ambas as estratégias retornam objetos `DocumentChunk` com `document_id`, `chunk_index` (a partir de zero), `page_start`, `page_end` e `text`. Um trecho pode abranger mais de uma página.

## Testes

```bash
python -m pytest -q
```

A suíte cobre o endpoint de saúde, upload, rejeição de arquivos inválidos ou grandes demais, extração de texto e estratégias de chunking. Os testes de upload válido gravam PDFs em `storage/uploads/`.

Para verificar conflitos entre as dependências instaladas:

```bash
python -m pip check
```

## Experimento de embeddings

Depois de instalar o grupo `experiments`, execute:

```bash
python experiments/embedding_similarity.py
```

O script compara a similaridade entre frases usando o modelo `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`. Na primeira execução, é necessário acesso à internet para baixar o modelo. Esse experimento é independente da API.

## Estrutura

```text
app/
├── main.py                         # Aplicação FastAPI e endpoint de saúde
├── api/documents.py                # Upload e validação de documentos
├── models/document.py              # Modelos de documento e página
└── services/
    ├── pdf_service.py              # Validação e extração de texto
    ├── chunking_service.py         # Divisão por caracteres com sobreposição
    └── paragraph_chunking_service.py # Divisão por parágrafos
tests/                              # Testes da API e dos serviços
experiments/                        # Experimento de similaridade com embeddings
storage/uploads/                    # PDFs recebidos (ignorado pelo Git)
pyproject.toml                      # Dependências diretas por grupo
```
