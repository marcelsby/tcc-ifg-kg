# Grafo de Conhecimento do IFG

Repositório referente ao código-fonte da solução tecnológica proposta pelo meu TCC, intitulado "Construção de um Grafo do Conhecimento Acadêmico a partir da
estrutura semântica dos dados do IFG".

## Requisitos

- Python 3.10+
- Pipenv 2022.12.19+
- Docker 23.0.4+
- Docker Compose 2.17.2+

## Executar localmente

1. Clone o projeto:

```bash
  git clone https://github.com/marcelsby/tcc-ifg-kg.git
```

2. Acesse o diretório do projeto:

```bash
  cd tcc-ifg-kg
```

3. Defina as variáveis de ambiente:

```bash
  cp .env.example .env
```

O arquivo `.env.example` já vem com valores padrão, caso só deseje executar o projeto sem customizações não é necessário alterar o arquivo `.env` apenas usá-lo
da maneira que ele ficará após a execução do comando acima.

⚠️ **Para informações sobre a customização da execução leia a seção "Variáveis de Ambiente".**

4. Inicie o contêiner do Neo4j:

```bash
  docker compose up -d neo4j
```

5. Instale as dependências da aplicação:

```bash
  pipenv install
```

6. Entre no virtualenv criado pelo pipenv:

```bash
  pipenv shell
```

7. Execute a aplicação e aguarde a conclusão do processo:

```bash
  pipenv run pipeline
```

8. Abra o browser do Neo4j no navegador e realize as consultas no Grafo, caso necessite das credenciais, são as mesmas encontradas no arquivo .env, configurado
   anteriormente, na configuração padrão a URL para acessar o browser do Neo4j é a seguinte: [http://localhost:7474](http://localhost:7474)

9. Execute a consulta de teste, que exibe todos os servidores ligados ao IFG Jataí:

```cypher
MATCH (s:Servidor)-[:PART_OF]->(u:Unidade) WHERE u.sigla = 'JAT' RETURN s, u
```

10. Veja o grafo resultante da consulta na sua tela 🎉:

![Resultado da consulta dos servidores que fazem parte do IFG Jataí](./.github/resources/graph.png)

## Variáveis de Ambiente

Caso deseje customizar a execução do projeto abra o arquivo `.env` com o seu editor preferido e preencha as variáveis conforme a tabela abaixo:

|    Variável    | Descrição                                                        | Valor de exemplo |
|:--------------:|------------------------------------------------------------------|------------------|
|   NEO4J_HOST   | IP do banco usado pela aplicação para inserir os dados do grafo. | `localhost`      |
|   NEO4J_PORT   | Porta da porta Bolt do banco.                                    | `7687`           |
|   NEO4J_USER   | Usuário usado pela aplicação para se conectar ao banco.          | `neo4j`          |
| NEO4J_PASSWORD | Senha do usuário do banco.                                       | `ABhkQt`         |