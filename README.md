# AdR_projeto

Projeto de análise de redes usando Flask.

---

## Sumário

- [Como rodar localmente](#como-rodar-localmente)
- [Como rodar com Docker](#como-rodar-com-docker)
- [Dependências](#dependências)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Testes](#testes)
- [CI/CD](#cicd)
- [Build e Deploy com Docker](#build-e-deploy-com-docker)
- [Observações](#observações)

---

## Como rodar localmente

1. **Clone o repositório:**
   ```sh
   git clone https://gitlab.com/Croncl/adr_projeto.git
   cd adr_projeto
   ```

2. **Instale as dependências:**
   ```sh
   pip install -r requirements.txt
   ```

3. **Execute o projeto:**
   ```sh
   python main.py
   ```
   O site estará disponível em [http://localhost:5000](http://localhost:5000).

---

## Como rodar com Docker

1. **Construa a imagem:**
   ```sh
   docker build -t adr_projeto .
   ```

2. **Rode o container:**
   ```sh
   docker run -p 5000:5000 adr_projeto
   ```

---

## Dependências

Principais bibliotecas utilizadas (todas listadas em [`requirements.txt`](requirements.txt)):

- Flask
- Flask-WTF
- WTForms
- Flask-SQLAlchemy
- pandas
- networkx
- matplotlib
- seaborn
- pyvis
- dask
- pyarrow

---

## Estrutura do projeto

```
adr_projeto/
├── main.py
├── views.py
├── forms.py
├── models.py
├── requirements.txt
├── Dockerfile
├── .dockerignore
├── .gitignore
├── .gitlab-ci.yml
├── README.md
├── templates/
│   ├── home.html
│   ├── blog.html
│   ├── visualizations.html
│   └── graph_interactive.html
├── static/
│   ├── fundo.png
│   ├── images/
│   │   ├── degree_boxplot.png
│   │   └── degree_dist.png
│   ├── visualizations/
│   │   └── graph_output.html
│   └── dataset/
│       └── bitcoin.links.csv
├── lib/
│   ├── bindings/
│   │   └── utils.js
│   ├── tom-select/
│   │   ├── tom-select.complete.min.js
│   │   └── tom-select.css
│   └── vis-9.1.2/
│       ├── vis-network.css
│       └── vis-network.min.js
└── tests/
    ├── __init__.py
    ├── test_basic.py
    ├── test_graph_analyzer.py
    ├── test_routes.py
    └── __pycache__/
```

---

## Testes

Para rodar os testes automatizados:

```sh
python -m unittest discover
```

Os testes estão localizados na pasta [`tests/`](tests/).

---

## CI/CD

O projeto possui integração contínua via [`.gitlab-ci.yml`](.gitlab-ci.yml) para rodar testes automáticos e build de imagem Docker no GitLab.

Pipeline padrão:
- **build-job**: prepara o ambiente.
- **test**: executa os testes unitários.
- **package-job**: constrói e publica a imagem Docker no Container Registry do GitLab (executado apenas na branch `main`).

---

## Build e Deploy com Docker

### Imagem Base

Para uma imagem Docker mais leve, utilize no seu [`Dockerfile`](Dockerfile):

```dockerfile
FROM python:3.12-slim
# ...demais comandos...
```
> **Obs:** O projeto atualmente usa `python:3.12` (padrão), mas pode ser ajustado para `python:3.12-slim` para builds menores.

### Comandos úteis

- **Build da imagem:**
  ```sh
  docker build -t adr_projeto .
  ```
- **Listar imagens:**
  ```sh
  docker images
  ```
- **Executar o container:**
  ```sh
  docker run -p 5000:5000 adr_projeto
  ```

### CI/CD com Docker-in-Docker

No [`.gitlab-ci.yml`](.gitlab-ci.yml), utilize o seguinte job para build e push da imagem Docker:

```yaml
package-job:
  image: docker:24.0.5
  services:
    - docker:24.0.5-dind
  stage: package
  before_script: []
  script:
    - docker login $CI_REGISTRY -u $CI_REGISTRY_USER -p $CI_JOB_TOKEN
    - docker build -t $CI_REGISTRY_IMAGE .
    - docker push $CI_REGISTRY_IMAGE
  rules:
    - if: '$CI_COMMIT_BRANCH == "main"'
      when: always
```

- `$CI_REGISTRY_IMAGE` já aponta para o endereço correto do Container Registry do GitLab.

---

## Observações

- Para autenticação no Container Registry do GitLab durante o pipeline, utilize as variáveis de ambiente pré-definidas (`$CI_REGISTRY`, `$CI_REGISTRY_USER`, `$CI_JOB_TOKEN`).
- Consulte a [documentação oficial do GitLab](https://docs.gitlab.com/ee/ci/docker/using_docker_build.html) para detalhes sobre autenticação e deploy no Container Registry.
- Para builds ainda menores, considere também a imagem `python:alpine`, mas pode exigir ajustes nas dependências.
- O projeto utiliza arquivos de dados e imagens em subpastas de `static/` e bibliotecas JS/CSS em `lib/`.

---
