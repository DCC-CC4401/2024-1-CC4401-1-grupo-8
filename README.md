# ¿QUIÉN VA GANANDO?

**¿Quién va ganando?** es una aplicación web diseñada para facilitar la organización de competencias con varios eventos, como La Mona o alianzas de colegio.

Mediante esta aplicación, un usuario registrado va a poder crear un torneo, administrar los participantes, eventos y partidos, y adjudicar posiciones y puntajes a los participantes en cada evento. Por otra parte, los usuarios van a poder ingresar a la página del torneo, donde podrán ver tanto información general del torneo (tabla de puntajes totales y próximos partidos) como información detallada para cada evento.

Actualmente, la aplicación posee la siguiente funcionalidad:

* Un usuario puede crear una cuenta, e iniciar y cerrar sesión.
* Un usuario registrado puede crear un torneo, agregando participantes y eventos.
* Cualquier usuario puede entrar a la página de un torneo existente, donde podrá observar una tabla con los puntajes de cada participante en el torneo, y una lista de eventos.

## Cómo inicializar y correr el proyecto

Este proyecto utiliza **Django 3.2.25**, para lo cual se requiere una versión de Python igual o superior a **Python 3.6**.

A lo largo de las instrucciones, se utilizarán los comandos `python` y `pip`; si en la máquina del usuario estos comandos refieren a Python 2, es necesario cambiarlos por `python3` y `pip3`, respectivamente.


### Crear y activar el ambiente virtual

Para mantener las librerías necesarias para el proyecto, es recomendable instalarlas en un ambiente virtual (*venv*). Para crear un ambiente virtual llamado `myenv`, se debe correr el siguiente comando:
```
$ python -m venv myenv
```

Luego, antes de correr el proyecto, se debe activar el ambiente virtual con el siguiente comando, ejecutando desde el directorio que contiene la carpeta `myenv` el siguiente comando si se está trabajando en Linux:
```
$ source myenv/bin/activate
```

Y si se está trabajando en Windows:
```
$ myenv/Scripts/activate
```

Mientras el ambiente virtual esté activado, en el terminal aparecerá `(myenv)` antes del directorio actual.


### Instalar Django e inicializar el proyecto

Primero, se debe clonar este repositorio con `git`, mediante el siguiente comando:
```
$ git clone https://github.com/DCC-CC4401/2024-1-CC4401-1-grupo-8.git
```

Luego, se puede acceder a la carpeta clonada con el comando:
```
$ cd 2024-1-CC4401-1-grupo-8
```

Habiendo previamente activado el ambiente virtual, se pueden instalar las librerías necesarias para correr el proyecto (la versión de Django antes mencionada, junto con algunas librerías auxiliares) utilizando el siguiente comando:
```
$ pip install -r requirements.txt
```


Luego, se deben correr los siguientes comandos para actualizar la base de datos y cargar datos de prueba pre-existentes:
```
$ python manage.py migrate
$ python manage.py loaddata testdata.json
```

### Correr el proyecto

Una vez completados los pasos anteriores, cada vez que se desee correr el proyecto, basta con ejecutar el siguiente comando (estando en el directorio previamente clonado y con el ambiente virtual activado):
```
$ python manage.py runserver
```

Accediendo a `http://127.0.0.1:8000/`, la aplicación redirigirá al usuario a `http://127.0.0.1:8000/torneos`, la página principal donde se tiene la lista de torneos existentes. Una vez aquí, el usuario puede crear una cuenta nueva haciendo *click* en el botón "Iniciar sesión" y siguiendo las instrucciones del formulario; con una cuenta creada, el usuario puede hacer *click* en "Crear torneo" y rellenar la información pedida para armar su propia competición.

Una vez creado el torneo, el usuario puede hacer *click* en él para ingresar a la página asociada al torneo. Observará que ningún usuario tiene puntajes asociados; esta funcionalidad se implementará en una versión futura. Para ver un ejemplo de cómo sería una tabla con información rellenada, el usuario puede cerrar sesión, iniciar sesión con la cuenta "testuser" y la contraseña "thisisatest", y entrar al torneo "The Monkey 2024" (no basado en ningún torneo de la facultad).