# Diagrama Estrutural do Grafo do Conhecimento do IFG

O presente documento apresenta o diagrama detalhado do Grafo do Conhecimento Acadêmico, construído a partir da estrutura semântica dos dados do Instituto Federal de Goiás (IFG). Esse grafo, armazenado no banco de dados [Neo4j](https://neo4j.com/docs/getting-started/get-started-with-neo4j/graph-database/), representa de forma visual e organizada as entidades e seus relacionamentos do ambiente acadêmico do IFG.

O diagrama abrange a estrutura do grafo, destacando os diferentes tipos de nós e suas propriedades (também podendo ser chamadas de atributos, um par de chave-valor), bem como os relacionamentos entre eles. Essa representação proporciona uma visão clara e abrangente da complexidade das informações acadêmicas, auxiliando na compreensão e análise dos dados.

Ao explorar esse diagrama juntamente com a documentação abaixo, é possível visualizar a interconexão entre cursos, disciplinas, docentes, discentes e demais elementos do ambiente acadêmico, contribuindo para uma melhor compreensão da estrutura melhor acessibilidade à escrita de consultas utilizando a linguagem [Cypher](<https://en.wikipedia.org/wiki/Cypher_(query_language)>).

![diagrama principal](.github/resources/diagram_documentation/main.svg)
[Clique aqui](.github/resources/diagram_documentation/main.svg) para ver o diagrama em uma nova aba.

## Estrutura da documentação

Apresente a estrutura da documentação, destacando os principais capítulos e seções. Isso ajudará o leitor a ter uma visão geral do conteúdo e a encontrar facilmente as informações de seu interesse.

## Recursos de Suporte

Informe sobre os recursos de suporte disponíveis para o leitor, como links para documentação adicional, fóruns de discussão, FAQs ou suporte técnico. Isso ajuda o leitor a encontrar ajuda adicional, caso necessário.

[neo4j data types](https://neo4j.com/docs/cypher-manual/4.4/values-and-types/)

## Documentação das entidades

### Unidade

Representa uma unidade do IFG com um codigo UASG, que identifica unicamente um órgão do Governo Federal.

![diagrama unidade](.github/resources/graph-docs/unidade.svg)

#### Rótulos

1. Unidade

#### Propriedades

| Nome       | Obrigatória | Tipo de Dado | Formato adicional    |
| ---------- | ----------- | ------------ | -------------------- |
| nome       | Sim         | String       |                      |
| sigla      | Sim         | String       |                      |
| logradouro | Não         | String       |                      |
| numero     | Não         | String       |                      |
| bairro     | Não         | String       |                      |
| cep        | Não         | String       | "00000-000"          |
| cidade     | Não         | String       |                      |
| site       | Sim         | String       |                      |
| telefone   | Sim         | String       | "(ddd) 0000-0000"    |
| email      | Sim         | String       | "xxxxx@ifg.edu.br"   |
| cnpj       | Sim         | String       | "00.000.000/0000-00" |
| uasg       | Sim         | String       |                      |

#### Consultas de exemplo

1. Buscando pela unidade com a sigla "JAT"

    ```cypher
    MATCH (u:Unidade) WHERE u.sigla = 'JAT' RETURN n
    ```

### Docente

Representa um docente efetivo, que obrigatóriamente possui uma matrícula SIAPE e neste caso está vinculado a alguma Unidade do IFG.

![diagrama docente](.github/resources/graph-docs/docente.svg)

#### Rótulos

1. Docente
2. Servidor

#### Propriedades

| Nome                  | Obrigatória | Tipo de Dado |
| --------------------- | ----------- | ------------ |
| nome                  | ?           | String       |
| matricula             | ?           | Integer      |
| disciplina_ministrada | ?           | String       |
| data_ingresso         | ?           | Integer      |
| atribuicao            | ?           | String       |
| carga_horaria         | ?           | String       |

#### Relacionamentos

###### Docente - PART_OF -> Unidade

Denota a ligação de um Docente com uma Unidade.


#### Consultas de exemplo

1. Buscando pela unidade com a sigla "JAT"

    ```cypher
    MATCH (u:Unidade) WHERE u.sigla = 'JAT' RETURN n
    ```
