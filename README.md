# Никита проект генерации сайта.

python 3.13

Время на беке UTS

Для установки необходимых зависимостей из файла `requirements.txt`, выполните следующую команду в вашем терминале:

```bash
pip install -r requirements.txt
```


## Develop
Для обновления списка пакетов в requirements.txt используем pipreqs ./project_path  
``` pipreqs ./ --force```


uvicorn backend:app --reload

Запуск миграций  
```  alembic upgrade head ```  
Создание новой миграции    
``` alembic revision --autogenerate -m 'Name for migratiob' ```   
Запуск миграции в контейнере
``` docker-compose -p ai_bot_mysql up``` не доработанно  