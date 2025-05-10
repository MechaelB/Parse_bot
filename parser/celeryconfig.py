broker_url = 'redis://redis:6379/0'  # Брокер сообщений
result_backend = 'redis://redis:6379/0'  # Хранилище для результатов
accept_content = ['json']
task_serializer = 'json'
result_serializer = 'json'
