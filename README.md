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

3) Открыть [Airflow](http://localhost:8080), установить логин/пароль администратора и сделать активным 	_selector_standardize_electoral_data_ flow.