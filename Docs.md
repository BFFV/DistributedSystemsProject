# Grupo 3 - Sistemas Distribuidos

***Integrantes:***
- *Juan Aguillón* ([@vikingjuan](https://github.com/vikingjuan))
- *Benjamín Farías* ([@BFFV](https://github.com/BFFV))
- *Tomás García* ([@tgarcia5](https://github.com/tgarcia5))
- *Francisco Guíñez* ([@fguinez](https://github.com/fguinez))
- *Christian Klempau* ([@Christian-Klempau](https://github.com/Christian-Klempau))
- *Amaranta Salas* ([@amyaranta](https://github.com/amyaranta))

***Profesor:** Javier Bustos*

# Chat App

En el siguiente documento detallaremos el proceso de desarrollo de la aplicación Chat App, correspondiente a los requerimientos, arquitectura, componentes, *testing* y manuales de uso (*end user*).

| Versión (Entrega)   | 1                                                            |
| ------------------- | ------------------------------------------------------------ |
| Épica               | Chat distribuido simple y mensajes privados                  |
| Estado de Documento | Borrador                                                     |

| Versión (Entrega)   | 2    |
| ------------------- | ---- |
| Épica               | -    |
| Estado de Documento | -    |

| Versión (Entrega)   | 3    |
| ------------------- | ---- |
| Épica               | -    |
| Estado de Documento | -    |

| Versión (Entrega)   | 4    |
| ------------------- | ---- |
| Épica               | -    |
| Estado de Documento | -    |

## Requerimientos

Se presentan los requerimientos del sistema solicitado mediante *user stories*:

| #                    | Título                        | Descripción                                                  | Prioridad | Notas                                                        |
| -------------------- | ----------------------------- | ------------------------------------------------------------ | --------- | ------------------------------------------------------------ |
| <a name="req1">1</a> | Ingreso al servidor           | Un usuario puede ingresar al servidor de chat                | Alta      |                                                              |
| <a name="req2">2</a> | Envío de mensajes al servidor | Un usuario puede enviar un mensaje al servidor               | Alta      |                                                              |
| <a name="req3">3</a> | Ver los mensajes              | Un usuario puede ver los mensajes enviados al servidor       | Alta      |                                                              |
| <a name="req4">4</a> | Usuarios mínimos conectados   | Un usuario no verá los mensajes pasados hasta que se hayan conectado N clientes | Media     | - El parámetro N puede cambiar mediante comando <br />- Por defecto N es evaluado como 2 |
| <a name="req5">5</a> | Envío de mensajes privados    | Un usuario puede enviar un mensaje privado a otro usuario    | Media     |                                                              |
| <a name="req6">6</a> | Ver los mensajes privados     | Un usuario puede ver los mensajes privados enviados por otro usuario | Media     |                                                              |
| <a name="req7">7</a> | Salir del servidor            | Un usuario puede salir del servidor mediante comando         | Baja      | - Para poder salir sin cerrar de manera indirecta (cerrar consola, ctrl + c) |


## Arquitectura

Como equipo decidimos utilizar la arquitectura **cliente-servidor** con estructura **monolítica**. 

**(Tarea 1)** Un servidor de producción se encuentra montado sobre un contenedor Dynos de Heroku disponible en: https://pychat-io.herokuapp.com/.

### *Environment*

El servidor y la comunicación con este se realizó utilizando el lenguaje [**Python 3**](https://docs.python.org/3.7/), sobre la librería [**Flask**](https://flask.palletsprojects.com/en/2.0.x/). Mientras que para la comunicación privada entre clientes utilizamos la librería [**p2pnetwork**](https://github.com/macsnoeren/python-p2p-network).

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

### *Deployment*

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
## Componentes

<img src="https://github.com/BFFV/DistributedSystemsP1/blob/docs/figs/filemap.drawio.png?raw=true" style="zoom:20%; align:left;" />

### chat_app

Dentro del directorio **chat_app** se encuentran los archivos dedicados a montar el servidor del servicio, principalmente en el archivo **\_\_init\_\_.py**, mientras que el archivo **main.py** trabaja como *wrapper* de ejecución.

Dentro de **_\_init\_\_.py** se encuentran las siguientes funciones principales:

- 
  ```python
  def command_handler(msg):
      message = msg.strip().split()
      if message[0] == '$COMMAND':
          # do command logic
          # signal emition
          socketio.emit('command')
         	return True
      return False
  ```

  Esta función se dedica a manejar los comandos requeridos para la aplicación, hasta el momento, tiene programado los comandos: `$private` y `$reset`.

- ```python
  def create_app():
      # Crea y configura la app
      # Escuchar las seniales del socket
      @socketio.on('signal')
      def wrapper(params):
          # Logica de respuesta
          socketio.emit('response') # solo si corresponde
  ```

  Esta función cumple con configurar la aplicación en **Flask** y responder a las señales recibidas con la lógica de **SocketIo**.

Los archivos **models.py** y **wsgi.py** son para futuro desarrollo en la aplicación, conexión a una base de datos y temas de deployment (en el caso de **wsgi.py**).

### client

Dentro del directorio **client** se encuentran los archivos dedicados al usuario, principalmente los archivos **client.py** y **p2p.py**, mientras que el archivo **main.py** trabaja como *wrapper* de ejecución.

Dentro de **client.py** se encuentra la lógica de comunicación al servidor, y llamada a lógica de comunicación entre clientes. Podemos encontrar la siguiente lógica para la escucha y emisión de señales:

```python
# Escuchar las seniales del socket
@sio.on('signal')
def wrapper(params):
    # Logica de respuesta
   	sio.emit('response') # solo si corresponde
```



## Estrategia de testeo 

Para la mantención de la aplicación se recomienda realizar una serie de pruebas sobre el funcionamiento del programa mediante **White-box *testing***.

#### Local

Se dispone del código base del servidor, el cual se puede montar mediante un servidor local corriendo el siguiente comando desde `root`.

```
python chat_app/__init__.py -N
```

Posterior a esto, se recomienda realizar una prueba con **N-1** clientes conectados a este servidor, mediante el siguiente comando desde `root`

```
python client/client.py
```

Posterior, comience a enviar mensajes por estos N-1 clientes, y posterior conecte el cliente número **N**. 

Una vez hecho, debe revisar que puede observar en consola los siguientes datos:

- Instrucciones de uso.
- Comandos especiales.
- Usuarios conectados.
- Mensajes enviados.
- Mensajes recibidos.

Esto permitirá el mantenimiento de los requerimientos: [#1](#req1), [#2](#req2), [#3](#req3) y [#4](#req4).

Luego, pruebe la desconexión del servidor mediante el comando `$exit` con uno de los clientes, y una salida indirecta con otro cliente (cerrar consola o *Keyboard Interrupt*) para comprobar que el servidor sepa responder a dicha desconexión. Mantiene el requerimiento [#7](#req7).

Mediante el uso de 3 o más clientes conectados, se recomienda probar el comando `$private USER MSG` enviando un mensaje a uno de los usuarios conectados, de lo cual se espera el siguiente comportamiento.

- El usuario que envía el mensaje es confirmado del envío.
- El usuario emisor y receptor tendrá un mensaje iniciado con `(PRIVATE)`.
- Todo otro usuario no debe ver dicho mensaje.

Así se mantienen los requerimientos: [#5](#req5) y [#6](#req6)

Finalmente, probar el comando `$reset -N` y repetir el proceso con una nueva cantidad de usuarios conectados, ya que los anteriores se desconectarán apenas se aprete alguna tecla de input.

#### Producción

Para iniciar una prueba en un servidor externo, debe ejecutar el siguiente comando:

```
python client/client.py URI
```

Donde `URI` corresponde a la URI en la que se encuentra el servidor, en nuestro caso: https://pychat-io.herokuapp.com/

## Dev Notes

- El P2P no es posible aún entre redes de distintos lugares, debido a que se requiere la implementación de alguna estrategia tipo NAT Hole Punching o Port Forwarding para pasar a través de los routers privados.

## Manual de uso

El manual de uso de la aplicación se encuentra en el archivo [**README.md**](https://github.com/BFFV/DistributedSystemsP1/blob/main/README.md) disponible en el repositorio de la app.
