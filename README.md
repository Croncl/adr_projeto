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
