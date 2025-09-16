# Agente RAG com Google ADK, Postgres/pgvector e Neo4j

Este projeto implementa um agente de conversação utilizando o **Google Agent Development Kit (ADK)**. O agente utiliza uma arquitetura de **Retrieval-Augmented Generation (RAG)** para responder a perguntas, buscando informações em um banco de dados vetorial (**PostgreSQL com pgvector**) e em um banco de dados de grafos (**Neo4j**).

Todo o ambiente é orquestrado com Docker e Docker Compose.

## Arquitetura

- **Agente (ADK)**: O serviço principal que recebe as perguntas do usuário, orquestra as buscas e gera as respostas. Ele é construído com Google ADK e exposto através de uma API FastAPI.
- **PostgreSQL + pgvector**: Utilizado como banco de dados vetorial para armazenar embeddings de documentos e realizar buscas por similaridade.
- **Neo4j**: Utilizado como banco de dados de grafos para armazenar e consultar entidades e seus relacionamentos.

## Pré-requisitos

- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Gerenciamento de Documentos

Além do chat, a API expõe endpoints para gerenciar os documentos na base de conhecimento.

### Upload de Documento

- **Endpoint**: `POST /documents/`
- **Descrição**: Faz o upload de um arquivo (`.pdf`, `.docx`, `.txt`, `.md`), extrai seu conteúdo e o insere nos bancos de dados. Requer um campo `subject` para associar o documento a um tópico.
- **Como usar**: Utilize a interface do Swagger em `http://localhost:3232/docs`. No endpoint `POST /documents/`, preencha o campo `subject` e anexe o arquivo desejado.

### Exclusão de Documento

- **Endpoint**: `DELETE /documents/{doc_id}`
- **Descrição**: Remove um documento dos bancos de dados com base no seu ID.
- **Como usar**: Execute a exclusão através da interface do Swagger ou peça ao agente em uma conversa (ex: "esqueça o documento doc1" ou "remova o documento com id 'doc1'").

## Como Executar

### 1. Iniciar os Serviços

Navegue até o diretório raiz do projeto e execute o seguinte comando para construir e iniciar todos os contêineres em segundo plano:

```bash
docker-compose up --build -d
```

Este comando irá:
- Construir a imagem do agente Python.
- Iniciar os contêineres para o agente, PostgreSQL e Neo4j.
- Criar a extensão `vector` no banco de dados PostgreSQL.

### 2. Ingerir os Dados

Após os contêineres estarem em execução, execute o script de ingestão de dados. Este script irá popular o PostgreSQL com documentos e embeddings, e o Neo4j com nós e relacionamentos de exemplo.

```bash
docker-compose exec agent python ingest.py
```

Você pode executar este comando em um terminal separado. Ele se conectará aos bancos de dados em execução dentro dos contêineres.

### 3. Interagir com o Agente

O agente estará disponível na porta `3232`. A maneira mais fácil de interagir com ele é através da documentação da API gerada automaticamente pelo FastAPI (Swagger UI).

Abra seu navegador e acesse:

[http://localhost:3232/docs](http://localhost:3232/docs)

Você verá o endpoint `/chat`. Você pode expandi-lo, clicar em "Try it out" e enviar suas perguntas no campo de texto.

**Exemplos de Perguntas:**
- "O que é inteligência artificial?"
- "Fale sobre processamento de linguagem natural."
- "Como as redes neurais se relacionam com a IA?"
- "Qual o conceito de IA no assunto 'IA_Conceitos'?"
- "Remova o documento 'doc1'"

### 4. Parar os Serviços

Para parar todos os contêineres, execute:

```bash
docker-compose down
```

Este comando irá parar e remover os contêineres. Se você quiser remover também os volumes de dados (e perder todos os dados do Postgres e Neo4j), use:

```bash
docker-compose down -v
```

## Estrutura do Projeto

```
/
├── agent/            # Código-fonte do agente ADK
│   ├── tools/        # Ferramentas de busca (vetorial e grafo)
│   ├── agent.py      # Definição do agente
│   ├── main.py       # Ponto de entrada da API FastAPI
│   ├── Dockerfile    # Dockerfile do agente
│   └── requirements.txt
├── data/
│   └── sample_data.json # Dados de exemplo
├── postgres/
│   └── init.sql      # Script de inicialização do Postgres
├── docker-compose.yml  # Orquestração dos serviços
├── ingest.py         # Script para ingestão de dados
└── README.md         # Este arquivo
```
