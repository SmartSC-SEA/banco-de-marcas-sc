# Makefile para banco-de-marcas-sc

# Subir os containers
up:
	docker compose up -d

# Derrubar os containers
down:
	docker compose down

# Build das imagens
build:
	docker compose build

# Acessar o container web
shell:
	docker exec -it banco-marcas-web bash

# Ver logs em tempo real
logs:
	docker compose logs -f

# Rodar testes (se configurado)
test:
	pytest

# Formatar código com black
fmt:
	black .

# Verificar código com flake8
lint:
	flake8 .
