-- Executado só na primeira subida do container (volume vazio).
-- Banco separado para os testes de integração: eles apagam e recriam as tabelas.
CREATE DATABASE crm_test OWNER crm;
