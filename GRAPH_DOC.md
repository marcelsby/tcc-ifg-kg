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

1. Buscando pela Unidade com a sigla "JAT":

    ```cypher
    MATCH (u:Unidade) WHERE u.sigla = 'JAT' RETURN u
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
| nome                  | Sim         | String       |
| matricula             | Sim         | Integer      |
| disciplina_ministrada | Sim         | String       |
| data_ingresso         | Não         | Date         |
| atribuicao            | Sim         | String       |
| carga_horaria         | Sim         | String       |

#### Relacionamentos

- **Docente -[:PART_OF]➔ Unidade**

    Docente que faz parte de uma Unidade.


#### Consultas de exemplo

1. Docente com a matrícula "1526346":

    ```cypher
    MATCH (d:Docente) WHERE d.matricula = 1526346 RETURN d
    ```

2. Docentes que possuem ligação com a Unidade de Jataí:

    ```cypher
    MATCH (d:Docente)-[:PART_OF]->(u:Unidade) WHERE u.sigla = 'JAT' RETURN d, u LIMIT 15
    ```

3. Quantidade de Docentes que ingressaram depois de 01/01/2000:

    ```cypher
    MATCH (d:Docente) WHERE d.data_ingresso > date('2000-01-01') RETURN count(d)
    ```

### Técnico Administrativo Educacional (TAE)

Representa um TAE, que obrigatóriamente possui uma matrícula SIAPE e neste caso está vinculado a alguma Unidade do IFG.

![diagrama técnico administrativo educacional](.github/resources/graph-docs/tae.svg)

#### Rótulos

1. TAE
2. Servidor

#### Propriedades

| Nome          | Obrigatória | Tipo de Dado |
| ------------- | ----------- | ------------ |
| nome          | Sim         | String       |
| matricula     | Sim         | Integer      |
| data_ingresso | Sim         | Date         |
| atribuicao    | Sim         | String       |
| carga_horaria | Sim         | String       |

#### Relacionamentos

- **TAE -[:PART_OF]➔ Unidade**

   TAE que faz parte de uma Unidade.


#### Consultas de exemplo

1. TAE com a matrícula "2242502":

    ```cypher
    MATCH (t:TAE) WHERE t.matricula = 2242502 RETURN t
    ```

2. TAEs que possuem ligação com a Unidade de Jataí:

    ```cypher
    MATCH (t:TAE)-[:PART_OF]->(u:Unidade) WHERE u.sigla = 'JAT' RETURN t, u LIMIT 15
    ```

3. Quantidade de TAEs que ingressaram no ano de 2008:

    ```cypher
    MATCH (t:TAE) WHERE t.data_ingresso >= date('2008-01-01') AND t.data_ingresso <= date('2008-12-31') RETURN count(t)
    ```

### Curso

Representa um curso que é ofertado em uma Unidade.

![diagrama curso](.github/resources/graph-docs/curso.svg)

#### Rótulos

1. Curso

#### Propriedades

| Nome                | Obrigatória | Tipo de Dado |
| ------------------- | ----------- | ------------ |
| nome                | Sim         | String       |
| codigo              | Sim         | Integer      |
| modalidade          | Sim         | String       |
| formato             | Sim         | String       |
| turno               | Sim         | String       |
| periodo_de_ingresso | Sim         | String       |
| qtd_vagas_ano       | Sim         | Integer      |
| nivel               | Sim         | String       |
| ch_disciplinas      | Sim         | Integer      |
| ch_complementar     | Não         | Integer      |
| ch_estagio          | Não         | Integer      |
| ch_optativas        | Não         | Integer      |
| ch_projeto_final    | Não         | Integer      |
| ch_total            | Não         | Integer      |
| qtd_semestres       | Sim         | Integer      |


#### Relacionamentos

- **Curso -[:OFFERED_AT]➔ Unidade | Unidade -[:OFFERS]➔ Curso**

    Curso que é oferecido em uma Unidade, e vice versa.

#### Consultas de exemplo

1. Curso com o código "471" e em qual Unidade que é ofertado:

    ```cypher
    MATCH (c:Curso)-[:OFFERED_AT]->(u:Unidade) WHERE c.codigo = 471 RETURN c, u
    ```

2. Cursos ofertados pela Unidade de Jataí:

    ```cypher
    MATCH (u:Unidade)-[:OFFERS]->(c:Curso) WHERE u.sigla = 'JAT' RETURN c, u
    ```

3. Quantidade de Cursos de Ensino Médio ofertados em todas as Unidades:

    ```cypher
    MATCH (c:Curso) WHERE c.nivel = 'Ensino Médio' RETURN count(c)
    ```

### Disciplina

Representa uma Disciplina que é ministrada em um Curso.

![diagrama disciplina](.github/resources/graph-docs/disciplina.svg)

#### Rótulos

1. Disciplina

#### Propriedades

| Nome              | Obrigatória | Tipo de Dado |
| ----------------- | ----------- | ------------ |
| codigo            | Sim         | Integer      |
| periodo           | Sim         | Integer      |
| departamento      | Sim         | String       |
| nome              | Sim         | String       |
| carga_horaria     | Sim         | Integer      |
| sigla             | Sim         | String       |
| frequencia_oferta | Sim         | String       |


#### Relacionamentos

- **Disciplina -[:TAUGHT_AT]➔ Curso**

    Disciplina que é lecionada em um Curso.

- **Unidade -[:OFFERS]➔ Curso**

    Curso que oferta uma Disciplina.

#### Consultas de exemplo

1. O nome das Disciplinas lecionadas no curso de TADS da Unidade Jataí, ordenadas de maneira ascendente pelo período que são ofertadas:

    ```cypher
    MATCH (d:Disciplina)-[:TAUGHT_AT]->(c:Curso) WHERE c.codigo = 471 RETURN d.nome ORDER BY d.periodo
    ```

2. Quantas Disciplinas foram ofertadas nos Cursos da Unidade de Jataí:

    ```cypher
    MATCH (d:Disciplina)-[:TAUGHT_AT]->(c:Curso)-[:OFFERED_AT]->(u:Unidade) WHERE u.sigla = 'JAT' RETURN count(d)
    ```

3. Quantidades de Disciplinas de todas Unidades agrupadas por frequência de oferta:

    ```cypher
    MATCH (d:Disciplina) RETURN d.frequencia_oferta, COUNT(d)
    ```