# Grupo 3 - Sistemas Distribuidos
Tarea 1 - IIC2523

***Integrantes:***
- *Juan Aguillón* ([@vikingjuan](https://github.com/vikingjuan))
- *Benjamín Farías* ([@BFFV](https://github.com/BFFV))
- *Tomás García* ([@tgarcia5](https://github.com/tgarcia5))
- *Francisco Guíñez* ([@fguinez](https://github.com/fguinez))
- *Christian Klempau* ([@Christian-Klempau](https://github.com/Christian-Klempau))
- *Amaranta Salas* ([@amyaranta](https://github.com/amyaranta))

***Profesor:** Javier Bustos*

**URI Producción:** https://pychat-io.herokuapp.com/

## Índice

- [Instrucciones de uso](https://github.com/BFFV/DistributedSystemsP1/blob/main/README.md#instrucciones-de-uso)
  - [Instalación](https://github.com/BFFV/DistributedSystemsP1/blob/main/README.md#instalaci%C3%B3n)
  - [Servidor (versión local)](https://github.com/BFFV/DistributedSystemsP1/blob/main/README.md#servidor-versi%C3%B3n-local)
  - [Servidor (versión producción)](https://github.com/BFFV/DistributedSystemsP1/blob/main/README.md#servidor-versi%C3%B3n-producci%C3%B3n)
  - [Cliente](https://github.com/BFFV/DistributedSystemsP1/blob/main/README.md#cliente)
- [Consideraciones](https://github.com/BFFV/DistributedSystemsP1/blob/main/README.md#cliente)

**Nota:** Para una visión más detallada de la documentación del proyecto puedes visitar [Docs.md](https://github.com/BFFV/DistributedSystemsP1/blob/main/Docs.md).

## Instrucciones de uso
### Instalación

- Recomendamos usar **virtualenv** con Python 3.7+. De no estar instalado en su entorno de trabajo, debe instalar virtualenv (`pip3 install virtualenv`).

- En la carpeta raíz del repositorio, ejecutar la siguiente línea para crear el entorno virtual:

```
virtualenv venv
```

- Luego, deberás ejecutar la siguiente línea cada vez que quieras entrar al entorno virtual:

  ```
  source venv/bin/activate
  ```
  * NOTA: Si estás en Windows, este comando cambia a: ``source venv/Scripts/activate`` (ejecutando desde bash, sino se debe correr el ``activate.bat`` que se encuentra en dicho path desde Powershell o CMD)
- En tu terminal debería aparecer un indicativo `(venv)`, el cual te informa que ya estás dentro del entorno virtual.

- Finalmente, instalar los paquetes necesarios con `pip install -r requirements.txt` (este paso solo es necesario la primera vez).

### Servidor (versión local)

**Para correr el servidor localmente**, ejecutar la siguiente línea dentro de la carpeta `chat_app`:

```
python __init__.py -N
```

Donde N corresponde a cualquier número entero positivo.

También es equivalente a ejecutar en la misma carpeta:

```
python main.py -N
```


### Servidor (versión producción)

Ya hay una versión de producción del servidor en https://pychat-io.herokuapp.com/.

El proceso para realizar el deploy consta de los siguientes pasos:

1. Ingresar a [heroku.com](https://www.heroku.com/) e iniciar sesión.
    - En caso de no tener cuenta, primero debes crearla.
2. Una vez que se despliegue el _dashboard_, presionar la opción 'Create new app' que se despliega al presionar 'New' en la esquina superior derecha:

![Botón New](https://imgur.com/j7LuSUY.png)

3. Elegir un nombre de la app y presionar 'Create app'.

![Botón New](https://imgur.com/Jrn5cW5.png)

4. Iniciar sesión en heroku desde la consola con el comando:

```
heroku login
```
   - Si el comando `heroku` no está instalado, seguir [estas](https://devcenter.heroku.com/articles/heroku-cli) instrucciones.
 
5. Dentro de la carpeta del repositorio, ejecutar:
```
heroku git:remote -a [nombre-de-la-app]
```

6. Finalmente, estando en la rama ``main`` de tu repositorio, ejecutar:
```
git push heroku main
```

Y listo! El servidor ya está corriendo en heroku (por defecto el parámetro N será igual a 2)

Revisa la siguiente sección para saber cómo conectarse desde los clientes.

### Cliente

**Para correr un cliente**, ejecutar la siguiente línea dentro de la carpeta `cliente`:

```
python client.py URI
```

Donde URI corresponde a la URI en la que se encuentra el servidor.
- Si seguiste los pasos de la sección anterior, deberás rellenar este campo con `https://[nombre-de-la-app].herokuapp.com/`
- Alternativamente, ya disponemos de una versión de producción alojada en Heroku en: https://pychat-io.herokuapp.com/
- Si dejas este campo vacío, se asume que estás intentando conectarte a un servidor local en http://127.0.0.1:5000

También es equivalente a ejecutar en la misma carpeta:

```
python main.py URI
```

## Consideraciones

- Es posible enviar mensajes de cualquier tipo antes de que se unan los primeros N usuarios,
 pero no se podrán ver hasta que el chat se active.

- Cuando el número de usuarios conectados alcance el valor N, el chat quedará activado permanentemente,
a menos que se utilice el comando `$reset -N` desde algún cliente. Este último comando permite volver a fijar un valor de N y reiniciar todo.

- Los comandos especiales del cliente (`$exit`, `$private`, `$reset`) son indicados dentro de la interfaz del chat.

<!--  ## Instalación (old 🚨)

❗️❗️❗️ _Esta sección de instalación es antigua, debe ser borrada antes de la entrega final ❗️❗️❗️_

Recomendamos usar virtualenv con Python 3.7+

- Instalar paquetes necesarios con `pip install -r requirements.txt`.

- Correr para que flask reconozca app: `export FLASK_APP=chat_app`.

- Cambiar entre dev y production: `export FLASK_ENV=development/production`.

- Activar o desactivar el debug mode: `export FLASK_DEBUG=True/False`.

- Para crear un repositorio de migraciones usar `flask db init`

- Para generar una migración usar `flask db migrate`

- Para aplicar migraciones usar `flask db upgrade`

- Cada vez que se cambia el modelo de la base de datos correr comandos 
`migrate` y `upgrade`.

- Para sincronizar bd en otro sistema, refrescar carpeta de migraciones
desde la fuente y correr el comando `upgrade`

- Para ver todos los comandos correr `flask db --help`. Para ayuda también puede 
revisar [aquí](https://flask-migrate.readthedocs.io/en/latest/)

-->
