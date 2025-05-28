-- ==========================================
-- Tabelas principais da aplicação CadastroMarcas
-- ==========================================

CREATE TABLE IF NOT EXISTS usuarios (
  id INT AUTO_INCREMENT PRIMARY KEY,
  usuario VARCHAR(200) NOT NULL,
  senha VARCHAR(200) NOT NULL,
  perfil ENUM('admin','normal') NOT NULL DEFAULT 'normal',
  cpf VARCHAR(11) NOT NULL UNIQUE
) ENGINE=InnoDB CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS orgaos (
  id INT AUTO_INCREMENT PRIMARY KEY,
  sgl_orgao VARCHAR(20) NOT NULL,
  nome_orgao VARCHAR(255) NOT NULL
) ENGINE=InnoDB CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS marcas (
  id INT AUTO_INCREMENT PRIMARY KEY,
  codigo_item VARCHAR(50) NOT NULL,
  marca VARCHAR(255) NOT NULL,
  descricao_produto TEXT NOT NULL,
  data_cadastro DATE NOT NULL,
  data_validade DATE NULL,
  fornecedor_amostra VARCHAR(255) NULL,
  processo_sgpe VARCHAR(100) NULL,
  observacao TEXT NULL,
  status VARCHAR(10) NOT NULL DEFAULT 'ativo',
  fabricante VARCHAR(255) NULL,
  modelo VARCHAR(255) NULL,
  pais_origem VARCHAR(255) NULL,
  imagem_produto VARCHAR(255) NULL,
  arquivo_registro VARCHAR(255) NULL,
  arquivo_ficha_parecer VARCHAR(255) NULL,
  edital_pre_qualificacao VARCHAR(255) NULL,
  id_orgao INT NULL,
  status_aprovacao VARCHAR(20) NOT NULL DEFAULT 'pendente',
  FOREIGN KEY (id_orgao) REFERENCES orgaos(id)
) ENGINE=InnoDB CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS imagens_produto (
  id INT AUTO_INCREMENT PRIMARY KEY,
  id_marca INT NOT NULL,
  nome_arquivo VARCHAR(255) NOT NULL,
  FOREIGN KEY (id_marca) REFERENCES marcas(id)
) ENGINE=InnoDB CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS log_alteracoes (
  id INT AUTO_INCREMENT PRIMARY KEY,
  id_marca INT NOT NULL,
  usuario VARCHAR(100) NOT NULL,
  data_hora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  motivo TEXT NOT NULL,
  FOREIGN KEY (id_marca) REFERENCES marcas(id)
) ENGINE=InnoDB CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==========================================
-- Tabelas de Catálogo (local)
-- ==========================================

CREATE TABLE IF NOT EXISTS catalogo_itens (
  item_codigo   VARCHAR(50) NOT NULL,
  item_descricao VARCHAR(255) NOT NULL,
  PRIMARY KEY (item_codigo)
) ENGINE=InnoDB CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS catalogo_controle (
  id INT AUTO_INCREMENT PRIMARY KEY,
  data_ultima DATETIME NOT NULL,
  total_registros INT NOT NULL DEFAULT 0
) ENGINE=InnoDB CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
