CREATE VIEW livros AS
SELECT livro, autor, genero, ano, editora, quantidade, sinopse
FROM tb_livros AS t1;

CREATE VIEW usuarios AS
SELECT nome, tipo, sala, email, telefone
FROM tb_usuarios AS t1;

CREATE VIEW emprestimos AS
SELECT t2.nome AS nome, t2.tipo AS tipo, t3.livro AS livro, t3.autor AS autor, t3.ano AS ano, t3.editora AS editora, t1.quantidade, t1.data, t1.prazo, t1.status
FROM tb_emprestimos AS t1
JOIN tb_usuarios AS t2 ON t1.id_usa = t2.id_usa
JOIN tb_livros AS t3 ON t1.id_liv = t3.id_liv;