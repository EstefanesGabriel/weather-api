# Weather API

O projeto coleta condições meteorológicas atuais da **OpenWeather Current Weather API**, armazena registros no **PostgreSQL** com **Django ORM** e disponibiliza a consulta/importação via **FastAPI**, com documentação Swagger automática.

## Tecnologias

- Python 3.14
- Django 5.2 LTS (ORM, migrations e administração)
- FastAPI e Pydantic (endpoints e contratos de resposta)
- Requests (consumo da OpenWeather)
- PostgreSQL 17
- Docker / Docker Compose

## Estrutura

```text
weather-api/
├── config/                 # Configurações e ASGI do Django
├── weather/
│   ├── migrations/         # Versionamento do esquema do banco
│   ├── models.py           # Model WeatherRecord
│   ├── routes.py           # Endpoints FastAPI
│   ├── schemas.py          # Schema de resposta Pydantic
│   ├── services.py         # Consulta OpenWeather + persistência
│   └── admin.py            # Administração dos registros
├── main.py                 # Entrada FastAPI + montagem Django
├── manage.py               # Comandos administrativos Django
├── Dockerfile              # Imagem da aplicação Python
├── compose.yaml            # Contêineres API e PostgreSQL
├── requirements.txt        # Dependências Python
├── .env.example            # Modelo das variáveis de ambiente
└── README.md
```

## Pré-requisitos

- Docker Engine com suporte a contêineres Linux e Docker Compose instalados. No Windows e macOS, o Docker Desktop é uma opção para fornecer esse ambiente.
- Conta e chave de API ativa na [OpenWeather](https://home.openweathermap.org/api_keys).
- Para execução sem Docker da API: Python 3.14 e dependências em `requirements.txt`.

## Configuração

1. Copie `.env.example` para um arquivo `.env` na raiz do projeto.
   - No Windows PowerShell: `Copy-Item .env.example .env`
   - No Linux/macOS: `cp .env.example .env`
2. Edite `.env` e defina:
   - `OPENWEATHER_API_KEY`: chave ativa da OpenWeather.
   - `POSTGRES_PASSWORD`: senha do usuário do banco.
   - `DJANGO_SECRET_KEY`: chave longa e aleatória usada pelo Django.
   - `DJANGO_DEBUG`: `True` para desenvolvimento local; se omitida, assume `False`.
   - `POSTGRES_DB` e `POSTGRES_USER`: nome e usuário do banco.
3. **Não publique `.env`**. Ele está ignorado pelo Git e pelo Docker build.

Para gerar uma chave, execute `python -c "import secrets; print(secrets.token_urlsafe(50))"` e copie o resultado para `DJANGO_SECRET_KEY` no `.env`. A aplicação exige uma chave não vazia para iniciar.

`DB_HOST=localhost` e `DB_PORT=5432` são utilizados quando o Django roda no seu computador. **Dentro do contêiner da API, o Compose define automaticamente `DB_HOST=db` e `DB_PORT=5432`.**

> As configurações de exemplo (`DJANGO_DEBUG=True`, porta exposta e endpoints sem autenticação) destinam-se a desenvolvimento e avaliação local. Não publique este sistema diretamente na internet sem autenticação, HTTPS e revisão de segurança.

## Executar com Docker (recomendado)

Na raiz do projeto, depois de preparar o `.env`:

```bash
docker compose up --build -d
docker compose exec api python manage.py migrate
docker compose ps
```

Serviços disponíveis:

| Serviço                                | Acesso                             |
| -------------------------------------- | ---------------------------------- |
| API FastAPI e Swagger                  | http://localhost:8000/docs         |
| API OpenAPI em JSON                    | http://localhost:8000/openapi.json |
| PostgreSQL a partir do computador      | `localhost:5432`                   |
| PostgreSQL a partir do contêiner `api` | `db:5432`                          |

A API é publicada na porta `8000` do computador. Em uma rede local autorizada, ela poderá ser acessada por `http://IP_DO_COMPUTADOR:8000/docs` **se a rede e o firewall permitirem**. Isso não constitui uma publicação segura na internet.

Para acompanhar os logs:

```bash
docker compose logs -f api
```

Para desligar os serviços sem remover os dados:

```bash
docker compose down
```

Os registros são preservados no volume `postgres_data`. **Não execute `docker compose down -v` se quiser conservar os dados**, pois esse comando remove os volumes do projeto.

## Endpoints REST

### POST `/weather/import`

Recebe coordenadas, faz uma **requisição GET autenticada à OpenWeather**, extrai os campos selecionados e salva um registro no PostgreSQL. Retorna `201 Created` e o registro inserido.

Parâmetros de consulta:

| Parâmetro | Tipo    | Descrição                  |
| --------- | ------- | -------------------------- |
| `lat`     | `float` | Latitude (`-90` a `90`)    |
| `lon`     | `float` | Longitude (`-180` a `180`) |

Exemplo (Curitiba):

```http
POST http://localhost:8000/weather/import?lat=-25.43&lon=-49.27
```

A chamada externa feita pelo serviço tem este formato (a chave é enviada automaticamente pelo backend):

```http
GET https://api.openweathermap.org/data/2.5/weather?lat=-25.43&lon=-49.27&units=metric&lang=pt_br&appid=SUA_API_KEY
```

### GET `/weather`

Lista os registros armazenados, ordenando os mais recentes primeiro.

```http
GET http://localhost:8000/weather
```

O parâmetro opcional `city` permite filtrar pelo nome da cidade (sem diferenciar maiúsculas e minúsculas):

```http
GET http://localhost:8000/weather?city=Curitiba
```

### Exemplo de resposta

Valores meramente ilustrativos:

```json
{
  "id": 1,
  "name": "Curitiba",
  "country": "BR",
  "temp": 23.99,
  "temp_min": 23.8,
  "temp_max": 24.23,
  "feels_like": 24.06,
  "main": "Clouds",
  "description": "nuvens dispersas",
  "rain_1h": null,
  "wind_speed": 4.63,
  "collected_at": "2026-11-16T17:50:25.620131Z"
}
```

## Estrutura do banco

Uma tabela `weather_records`, definida em `weather/models.py`, com os seguintes campos:

| Campo          | Origem/descrição                                    |
| -------------- | --------------------------------------------------- |
| `id`           | Chave primária gerada pelo Django                   |
| `name`         | Nome da cidade (`name`)                             |
| `country`      | Código do país (`sys.country`)                      |
| `temp`         | Temperatura em °C (`main.temp`)                     |
| `temp_min`     | Temperatura mínima da observação (`main.temp_min`)  |
| `temp_max`     | Temperatura máxima da observação (`main.temp_max`)  |
| `feels_like`   | Sensação térmica em °C (`main.feels_like`)          |
| `main`         | Condição climática geral (`weather[0].main`)        |
| `description`  | Descrição em português (`weather[0].description`)   |
| `rain_1h`      | Chuva na última hora, em mm (`rain.1h`), opcional   |
| `wind_speed`   | Velocidade do vento em m/s (`wind.speed`), opcional |
| `collected_at` | Data/hora de gravação, gerada pelo Django (UTC)     |

Os valores `temp_min` e `temp_max` são referentes à observação disponibilizada pela API de clima atual, **não necessariamente à mínima e à máxima do dia**. A ausência do campo de chuva é armazenada como `NULL`, não como zero.

**Cada importação cria um novo registro**, inclusive se a API retornar uma observação repetida. Nesta versão, não há processo automático de agendamento nem deduplicação.

## Executar a API diretamente no Windows (opcional)

Deixe apenas o banco rodando no Docker para evitar conflito da porta `8000`:

```powershell
docker compose up -d db
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
uvicorn main:app --reload
```

Se o PowerShell bloquear `Activate.ps1`, verifique a política de execução ou execute `.venv\Scripts\python.exe` diretamente sem ativar o ambiente virtual.

## Django Admin (opcional)

O model está registrado no Django Admin. Para utilizar a interface:

```bash
docker compose exec api python manage.py createsuperuser
```

Depois acesse `http://localhost:8000/admin/` e entre com o usuário criado. Para aplicações expostas publicamente, proteja o acesso administrativo e configure corretamente as opções de segurança.

## Observações técnicas

- Django ORM e `requests` são utilizados de maneira **síncrona**. Por isso, as funções de rota FastAPI são declaradas com `def`.
- `main.py` inicializa o Django antes de importar os módulos que utilizam seus models.
- A OpenWeather exige chave ativa; falhas de integração retornam erro HTTP adequado (por exemplo, `502` para falha na API externa).
- A documentação Swagger é gerada automaticamente pelo FastAPI em `/docs`.
- O projeto foi mantido intencionalmente enxuto para atender à avaliação: uma tabela e dois endpoints, sem diretório de testes.

## Documentação oficial

- [OpenWeather Current Weather API](https://openweathermap.org/current)
- [Django](https://docs.djangoproject.com/en/5.2/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Docker Compose](https://docs.docker.com/compose/)
