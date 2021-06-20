# Selector-standardizers

Модуль проекта Selector, реализующий основную логику обработки данных протоколов:
- распознавание уровня выборов
- распознавание уровня комиссии
- подбор схемы данных
- распознавание полей протокола
- конвертирование в стандартный формат, соответствующий схеме
- обучение ML-моделей распознавания.

Для работы тестов необходимо задать переменную окружения GOOGLE_APPLICATION_CREDENTIALS, указывающую путь к JSON файлу аутентификации Google Cloud Storage (GCS) проекта codeforrussia-selector.

> PYTHONPATH=src GOOGLE_APPLICATION_CREDENTIALS=<path_to_google_credentials_json> pytest

## Обучение модели распознавания полей протоколов

Обучение (точнее, fine-tuning) ML-модели осуществляется по текущей Avro схеме. Avro схема разрабатывается для выборов определенного уровня и типа. Pre-trained мульти-языковая модель на основе Sentence-BERT уже способна распознавать различные поля протоколов. Для улучшения ее качества используется fine-tuning модели по отношению к triplet loss на синтетических данных, сгенерированных из Avro схемы.

1) Генерируются синтетические данные для обучения из имен и алиасов полей протоколов в схеме.
2) Fine-tuning языковой модели по triplet loss.
3) Экспорт модели в формат, принимаемый Sentence-BERT.

Пример команды тренировки:
> PYTHONPATH=src python -m org.codeforrussia.selector.standardizer.recognizers.similarity.train --election-level REGIONAL --election-type PERSONAL --output-model-dir /tmp/codeforrussia-selector/ml-models/similarity-protocol-recognizer_1_0_0.zip