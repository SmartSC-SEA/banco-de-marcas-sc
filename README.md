# Banco de Marcas SC

Este repositório contém a aplicação Flask **Cadastro de Marcas**, desenvolvida para...
- listar e consultar marcas
- cadastro de novas marcas com upload de anexos e imagens
- filtros de segurança (CSRF, uploads protegidos, rate-limit)
- divisão simples de rotas: auth, internas, públicas, catálogo, export

## Como rodar

1. Copie `.env.example` para `.env` e preencha as variáveis.
2. `pip install -r requirements.txt`
3. `python app.py`
4. Acesse `http://<host>:5000/consulta_publica` para a rota pública.
5. Faça login em `http://<host>:5000/auth/login` para a área interna.
