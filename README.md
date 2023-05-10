# backend_community_homework

[![CI](https://github.com/yandex-praktikum/hw03_forms/actions/workflows/python-app.yml/badge.svg?branch=master)](https://github.com/yandex-praktikum/hw03_forms/actions/workflows/python-app.yml)

##### Учебный проект
#### Доработка приложения yatube.
Новое в проекте:
##### - Приложение core:
-- размещён и зарегистрирован фильтр `addclass`, позволяющий добавлять CSS-класс к тегу шаблона;
-- создан и зарегистрирован контекст-процессор, добавляющий текущий год на все страницы в переменную ```{{ year }}```. 
##### - приложение `about`:
--созданы статические страницы `/about/author/` и `/about/tech/`.
##### - приложение `users`:
--кастомные шаблоны для url-адресов `auth/login/`, `auth/logout/` и `auth/signup/`;
--страница пользователя `/profile/<username>/`.
##### - приложение `posts`:
-- cтраница просмотра поста `/posts/<post_id>/`.
- подключена паджинация;
- создана страница с функционалом публикации поста `posts/create/` и страница с функционалом редактирования поста ```posts/edit/```.

#### Запуск проекта в dev-режиме 
- Установите и активируйте виртуальное окружение: ```python -m venv venv```
- Установите зависимости из файла requirements.txt: ``` pip install -r requirements.txt ``` 
- Создайте миграции и мигрируйте их в БД: ```python manage.py makemigrations```, ```python manage.py migrate```
-  Запустите сервер, выполнив в папке с файлом manage.py команду: ``` python manage.py runserver ``` 

##### Финальная версия проекта yatube: https://github.com/creamsandwch/hw05_final.
