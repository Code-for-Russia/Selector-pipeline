# Selector-pipeline
ETL пайпланы для проекта Selector ([Идея](https://github.com/Code-for-Russia/How-to-start/issues/11), [RFC](https://docs.google.com/document/d/1nxI_VNQ_HgMeIJJqJpP24aUpEpfnVbbehyNbq3eh_3Q/edit?usp=sharing))

## Дизайн-схема
![Design](Selector-Flow.png)

## Установка

1) Развернуть Airflow

 - Скачать Docker Image для Airflow:
 > docker pull nzhiltsov/selector-airflow:0.1

 - Скопировать docker-compose.yaml в $AIRFLOW_HOME_DIR
 - Скопировать selector-standardization-flow в $AIRFLOW_HOME_DIR/dags:
 > rsync -rv --exclude=.git --exclude=build --exclude=selector_standardization_flow.egg-info --exclude=dist --exclude=__pycache__ selector-standardization-flow $AIRFLOW_HOME_DIR/dags

 - Сгенерировать файл для соединения с Google Cloud Storage (GCS) и скопировать его в $AIRFLOW_HOME_DIR/google-configs/gcs-credentials.json
 - Стартовать Airflow
 > docker compose up

2) Открыть Airflow [локально](http://localhost:8080), установить логин/пароль администратора и сделать активным	_selector_standardize_electoral_data_ flow.

## Сервис

Референсный пример сервиса развернут в тестовом режиме и пишет стандартизированные данные каждый день в папку gs://codeforrussia-selector/standardized-election-data, группируя по датам.

## Чтение стандартизированных файлов

Результирующие файлы в формате Avro можно прочитать с помощью соответствующего reader и схемы. Например, в Python:

```python
import json
from fastavro import parse_schema, reader

avro_folder = "selector/selector-pipeline/selector-standardizers/src/org/codeforrussia/selector/standardizer/schemas"

named_schemas = {}
# Общая схема для всех схем полей протоколов
with open(f"{avro_folder}/common/election_1_0.avsc", "rb") as election_schema_file:
    election_schema = parse_schema(json.load(election_schema_file), named_schemas)

# Схема для выборов депутатов представительных органов местного самоуправления на уровне городского поселения
with open(f"{avro_folder}/municipal/deputy_city_1_0.avsc", "rb") as municipal_deputy_file:
    municipal_deputy_schema = parse_schema(json.load(municipal_deputy_file), named_schemas)

# Чтение файла
with open('codeforrussia-selector/standardized-election-data/2021-07-06/org_codeforrussia_selector_schemas_municipal_DeputyCityProtocolFields-00000-of-00001.avro', 'rb') as fin:
    avro_reader = reader(fin, municipal_deputy_schema)
    standardized_data = [item for item in avro_reader]
    print(standardized_data[0])
```

Пример прочитанных данных одного протокола (описание полей - в соответствующей Avro схеме - в данном случае, [deputy_city_1_0.avsc](https://github.com/Code-for-Russia/Selector-pipeline/blob/main/selector-standardizers/src/org/codeforrussia/selector/standardizer/schemas/municipal/deputy_city_1_0.avsc)):
```javascript
{
    'election': {
          'name': 'Выборы депутатов Совета муниципального образования городского округа "Сыктывкар" шестого созыва',
          'date': '21.09.2020',
          'location': ['Сыктывкарская, округ №1'],
          'commission_level': 'TERRITORY'
     },
     'voters': 12135,
     'received_by_commission': 8600,
     'issued_ahead': 1713,
     'issued_to_commission': 1473,
     'issued_to_mobile': 96,
     'canceled': 82,
     'in_mobile': 1724,
     'in_stationary': 1556,
     'invalid': 252,
     'valid': 3028,
     'lost': 0,
     'unaccounted': 0,
     'issued_ahead_to_territorial': -1,
     'issued_ahead_to_district': -1,
     'received_absentee_certificates': 90,
     'issued_absentee_certificates': 8,
     'votes_by_absentee_certificates': 43,
     'issued_absentee_certificates_to_territorial': 0,
     'lost_absentee_certificates': 0
 }
```
-1 обозначает отсутствие значений полей этого типа.