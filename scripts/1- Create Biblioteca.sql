CREATE DATABASE biblioteca;
USE biblioteca;

CREATE TABLE tb_livros (
	id_liv INT PRIMARY KEY AUTO_INCREMENT,
	livro VARCHAR(255) NOT NULL,
	autor VARCHAR(255) NOT NULL,
	genero VARCHAR(255) NOT NULL,
	ano INT NOT NULL,
	editora VARCHAR(255) NOT NULL,
	quantidade INT NOT NULL,
	sinopse TEXT
);

CREATE TABLE tb_usuarios (
	id_usa INT PRIMARY KEY AUTO_INCREMENT,
	nome VARCHAR(255) NOT NULL,
	tipo VARCHAR(9) NOT NULL,
	sala VARCHAR(3),
	email VARCHAR(255) NOT NULL,
	telefone VARCHAR(20)
);

CREATE TABLE tb_emprestimos (
	id_emp INT PRIMARY KEY AUTO_INCREMENT,
	id_usa INT NOT NULL,
	id_liv INT NOT NULL,
	quantidade INT NOT NULL,
	data DATE NOT NULL,
	prazo DATE NOT NULL,
	status VARCHAR(9),
	FOREIGN KEY (id_usa) REFERENCES tb_usuarios(id_usa),
	FOREIGN KEY (id_liv) REFERENCES tb_livros(id_liv)
)
	