## Projeto Final UFCD -5425 

Este projeto está ser desenvolvido no âmbito da UFCD 5425 -Projeto de tecnologias e programação de sistemas de informação que se insere no curso de Programação em Python dinamizado pelo Centro de Emprego e formação profissional de Faro.

O projeto a desenvolver consiste num website que terá como objetivo informar o público sobre urbanismo e a importância do transporte público para o mesmo, usando a Metro do Porto como caso de estudo.

A ideia para este projeto surge da constatação da enorme lacuna de recursos informativos, acessíveis ao público em geral e ao  português em particular, relativos ao transporte público e a sua importância para o bom funcionamento de uma cidade e o impacto que tem na qualidade de vida dos seus habitantes.



## Como executar (Até agora)

```bat
python -m venv .venv
.venv\Scripts\activate
python -m pip install -e ".[dev]"

:: Cria a estrutura para base de dados a partir de sql\schema.sql (não apaga dados)

python scripts/init_db.py          # prepara a base de dados (não apaga dados)
python scripts/importar_csv.py     # importa data/metro_porto_2016_2024.csv

python -m uvicorn metro_em_numeros.main:criar_app --factory --reload


## Estrutura

| Pasta/ficheiro | Responsabilidade |
|---|---|
| `domain/` | Conceitos e regras (`Linha`, `Indicador`, `ValorIndicador`, erros) |
| `repositories/` | Todo o SQL |
| `services/` | Leitura, validação e coordenação da importação; preparação dos dados da página |
| `web/` | Rotas FastAPI |
| `templates/` | Páginas Jinja2 |
| `sql/schema.sql` | Script de criação da base de dados |
| `scripts/` | Comandos de inicialização e importação |
| `data/` | CSV de origem |
| `tests/` | Testes (pytest) |
| `docs/` | Modelo E-R (`modelo_er.dbml`) e registo de alterações face à Entrega Inicial |

## Passo seguintes (15/11/2026)

- Criar a funcionalidade de importar dos dados através do csv.
