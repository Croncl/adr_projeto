# AdR_projeto

Projeto de análise de redes usando Flask.

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
   docker build -t adr-projeto .
   ```

2. **Rode o container:**
   ```sh
   docker run -p 5000:5000 adr-projeto
   ```

---

## Dependências

- Flask
- Flask-WTF
- WTForms
- Flask-SQLAlchemy

Todas listadas em `requirements.txt`.

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
│   └── blog.html
│   └── visualizations.html
└── static/
    └── fundo.png
```

---

## Testes

Para rodar os testes:
```sh
python -m unittest discover
```

---

## CI/CD

O projeto já possui integração contínua configurada via `.gitlab-ci.yml` para rodar testes automáticos no GitLab.

---

Instrucoes para construir imagem docker:

Gerar imagem docker, mas escolher uma distribuicao menor
qual imagem base usar para ficar mais leve?
 - alpine
 - slim(essa)

docker build -t adr_projeto .

listat com docker image:
docker images



usa FROM python:3.12-slim

altera no Dockerfile e no .gitlab-ci.yml


executar o container:
docker run -p 5000:5000 adr_projeto

precisa super um ouro container com docker-in-docker e fazer o docher cli apontar para ele. Esse container temporario,chamamos de servico.

adiciona services: ....
package-job:
  image: docker:stable #mudar para ficar mais robusta
  services:
    - docker:dind 
  stage: package
  script:
    - docker build -t adr_projeto .

ver deploy -> conainer regirtry para ver isntrucoes de como gerar.

docker login registry.gitlab.com
#coo passar credenciap para logar? senao falha: ver documentacao no gitlab

#predefined variables gitlab ci

autendticar no pipeline

depois:
docker build -t registry.gitlab.com/croncl/adr_projeto .

depois:
docker push registry.gitlab.com/croncl/adr_projeto


package-job:
  image: docker:stable
  services:
    - docker:dind
  stage: package
  script:
    - docker login $CI_REGISTRY -u $CI_REGISTRY_USER -p $CI_JOB_TOKEN
    #registry.gitlab.com, aqui para autenticar
    #Gerar token
    - docker build -t $CI_REGISTRY_IMAGE #registry.gitlab.com/croncl/adr_projeto .
    - docker push CI_REGISTRY_IMAGE #registry.gitlab.com/croncl/adr_projeto

    #- docker build -t adr_projeto .