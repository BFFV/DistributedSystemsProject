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

## Instrucciones de uso
### Instalación

- Recomendamos usar virtualenv con Python 3.7+. De no estar instalado en su enterno de trabajo, debe instalar virtualenv (`pip3 install virtualenv`).

- En la carpeta raíz del repositorio, ejecutar la siguiente línea para crear el ambiente virtual:
```
virtualenv venv
```

- Luego, deberás ejecutar esta línea cada vez que quieras usar el ambiente virtual:
  ```
  source venv/bin/activate
  ```
  En tu terminal debería aparecer un indicativo `(venv)`, el cual te informa que ya estás dentro del ambiente virtual.

- Instalar paquetes necesarios con `pip install -r requirements.txt` (este paso solo es necesario la primera vez).


### Servidor (en local)
**Para correr el servidor**, ejecutar la siguiente línea dentro de la carpeta `chat_app`:

```
python __init__.py -N
```

Donde N corresponde a cualquier número entero positivo.


También es equivalente a ejecutar en la misma carpeta:

```
python main.py -N
```

### Servidor (en Heroku)

### Cliente
**Para correr un cliente**, ejecutar la siguiente línea dentro de la carpeta `cliente`:

```
python client.py URI
```

Donde URI corresponde a la URI en la que se encuentra el servidor (en producción: https://pychat-io.herokuapp.com/), si no se coloca nada entonces se 
asume un servidor local en http://127.0.0.1:5000.

También es equivalente a ejecutar en la misma carpeta:

```
python main.py URI
```

## Suposiciones

- Cuando el número de usuarios conectados pasa de ser mayor a N a ser menor a N, nadie ve ningún mensaje hasta que vuelvan a conectarse N usuarios.
## Instalación (old 🚨)

❗️❗️❗️ _Esta sección de instalación es antigual, debe ser borrada antes de la entrega final ❗️❗️❗️_

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
