# Selector-standardation-beam

Apache beam пайплайн стандартизации:
- читает данные протоколов (например, хранящиеся на GCS)
- вызывает selector-standardizers в виде масштабируемого пайплайна (исполняемого как локально, так и, например, на Dataflow, Spark и тп.)
- сохраняет результат стандартизации в виде Avro.

> GOOGLE_APPLICATION_CREDENTIALS=/Users/nzhiltsov/airflow-installation/google-configs/carbide-program-314404-b1f3be733966.json