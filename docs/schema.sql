

CREATE TABLE IF NOT EXISTS modo_transporte (
    id_modo INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE,
    descricao TEXT
);

CREATE TABLE IF NOT EXISTS linha (
    id_linha INTEGER PRIMARY KEY AUTOINCREMENT,
    id_modo INTEGER NOT NULL REFERENCES modo_transporte(id_modo),
    codigo TEXT NOT NULL UNIQUE,
    nome TEXT NOT NULL,
    descricao TEXT
);

CREATE TABLE IF NOT EXISTS indicador(
    id_indicador INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE,
    unidade TEXT NOT NULL,
    descricao TEXT 
);

CREATE TABLE IF NOT EXISTS importacao(
    id_importacao INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_ficheiro TEXT NOT NULL,
    hash_sha256 TEXT NOT NULL UNIQUE,
    fonte TEXT NOT NULL,
    num_registos INTEGER NOT NULL,
    data_importacao TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS valor_indicador(
    id_valor INTEGER PRIMARY KEY AUTOINCREMENT,
    id_importacao INTEGER NOT NULL REFERENCES importacao(id_importacao),
    id_indicador INTEGER NOT NULL REFERENCES indicador (id_indicador),
    id_linha INTEGER REFERENCES linha (id_linha),
    ano INTEGER NOT NULL CHECK (ano BETWEEN 2000 AND 2030),
    valor REAL,
    UNIQUE (id_indicador, id_linha, ano)
);

CREATE UNIQUE INDEX IF NOT EXISTS ux_valor_total
    ON valor_indicador(id_indicador,ano)
    WHERE id_linha IS NULL;