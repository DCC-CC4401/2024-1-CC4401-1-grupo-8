# ¿QUIÉN VA GANANDO?

**¿Quién va ganando?** es una aplicación web diseñada para facilitar la organización de competencias con varios eventos, como La Mona o alianzas de colegio.

Mediante esta aplicación, un usuario registrado va a poder crear un torneo, administrar los participantes, eventos y partidos, y adjudicar posiciones y puntajes a los participantes en cada evento. Por otra parte, los usuarios van a poder ingresar a la página del torneo, donde podrán ver tanto información general del torneo (tabla de puntajes totales y próximos partidos) como información detallada para cada evento.

Actualmente, la aplicación posee la siguiente funcionalidad:

* Un usuario puede crear una cuenta, e iniciar y cerrar sesión.
* Un usuario registrado puede crear un torneo, agregando participantes y eventos.
* Cualquier usuario puede entrar a la página de un torneo existente, donde podrá observar una tabla con los puntajes de cada participante en el torneo, y una lista de eventos.

## Cómo correr el proyecto

El proyecto utiliza **Django 3.2.25**, el cual se puede instalar en Python con `pip` mediante el siguiente comando:
```
$ pip install Django==3.2.25
```
Es recomendable instalar Django en un ambiente virtual (*venv*) separado.

Una vez instalado Django, se debe clonar este repositorio con `git`, mediante el siguiente comando:
```
$ git clone https://github.com/DCC-CC4401/2024-1-CC4401-1-grupo-8.git
```

Habiendo clonado el repositorio, y estando en el directorio del proyecto clonado, se deben correr los siguientes comandos para actualizar la base de datos y cargar datos de prueba pre-existentes:
```
$ python manage.py migrate
$ python manage.py loaddata testdata.json
```

Ahora se puede correr la aplicación ejecutando el siguiente comando:
```
$ python manage.py runserver
```

Accediendo a `http://127.0.0.1:8000/`, la aplicación redirigirá al usuario a `http://127.0.0.1:8000/torneos`, la página principal donde se tiene la lista de torneos existentes. Una vez aquí, el usuario puede crear una cuenta nueva haciendo *click* en el botón "Iniciar sesión" y siguiendo las instrucciones del formulario; con una cuenta creada, el usuario puede hacer *click* en "Crear torneo" y rellenar la información pedida para armar su propia competición.

Una vez creado el torneo, el usuario puede hacer *click* en él para ingresar a la página asociada al torneo. Observará que ningún usuario tiene puntajes asociados; esta funcionalidad se implementará en una versión futura. Para ver un ejemplo de cómo sería una tabla con información rellenada, el usuario puede volver a la lista de torneos (por ejemplo, haciendo *click* en el título "¿Quién va ganando?") y entrar al torneo "The Monkey 2024" (no basado en ningún torneo de la facultad).