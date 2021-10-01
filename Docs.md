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

| Versión (Entrega)   | 2                                             |
| ------------------- | --------------------------------------------- |
| Épica               | Migración del servidor de manera transparente |
| Estado de Documento | Borrador                                      |

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
| <a name="req4">4</a> | Usuarios mínimos conectados   | Un usuario no verá los mensajes pasados hasta que se hayan conectado N clientes | Media     | - El parámetro N puede cambiar al ejecutar el server <br />- Por defecto N es evaluado como 2 |
| <a name="req5">5</a> | Envío de mensajes privados    | Un usuario puede enviar un mensaje privado a otro usuario    | Media     |                                                              |
| <a name="req6">6</a> | Ver los mensajes privados     | Un usuario puede ver los mensajes privados enviados por otro usuario | Media     |                                                              |

**(Tarea 2)** Los requisitos no cambian, ya que el proceso de migración debe ser transparente para el usuario.

## Arquitectura

Como equipo decidimos utilizar la arquitectura **cliente-servidor** con estructura **monolítica**. 

**(Tarea 1)** Un servidor de producción se encuentra montado sobre un contenedor Dynos de Heroku disponible en: https://pychat-io.herokuapp.com/.

### *Environment*

El servidor y la comunicación con este se realizó utilizando el lenguaje [**Python 3**](https://docs.python.org/3.7/), sobre la librería [**Flask**](https://flask.palletsprojects.com/en/2.0.x/). Mientras que para la comunicación privada entre clientes utilizamos la librería [**p2pnetwork**](https://github.com/macsnoeren/python-p2p-network).

- Recomendamos usar **virtualenv** con Python 3.7+.
- Las librerías requeridas se encuentran dentro del archivo ``requirements.txt``.

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

### Server

Dentro del directorio **server** se encuentra el archivo que monta el servidor **(main.py)**.

Dentro de **main.py** se encuentran las siguientes funciones principales:

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

  Esta función cumple con configurar la aplicación en **Flask** y responder a las señales recibidas con la lógica de **SocketIO**.

### Client

Dentro del directorio **client** se encuentran los archivos dedicados al usuario, que son **main.py** y **p2p.py**.

Dentro de **main.py** se encuentra la lógica de comunicación al servidor, y llamada a lógica de comunicación entre clientes. Podemos encontrar la siguiente lógica para la escucha y emisión de señales:

```python
# Escuchar las seniales del socket
@sio.on('signal')
def wrapper(params):
    # Logica de respuesta
   	sio.emit('response') # solo si corresponde
```

## Estrategia de testeo 

Para la mantención de la aplicación se recomienda realizar una serie de pruebas sobre el funcionamiento del programa mediante **White-box *testing***.

En el directorio **client** dentro del archivo **main.py**, línea 293 tiene disponible una variable para activar el modo debug, con el cual podrá observar el funcionamiento del programa. 

```python
# Run client
if __name__ == '__main__':
    # NOTE: Change this value when debugging
    debug = True
```

#### Local

Se dispone del código base del servidor, el cual se puede montar mediante un servidor local corriendo el siguiente comando desde `root`.

```
python3 server/main.py -N
```

Posterior a esto, se recomienda realizar una prueba con **N-1** clientes conectados a este servidor, mediante el siguiente comando desde `root`

```
python3 client/main.py
```

Posterior, comience a enviar mensajes por estos N-1 clientes, y posterior conecte el cliente número **N**. 

Una vez hecho, debe revisar que pueda observar en consola los siguientes datos:

- Instrucciones de uso.
- Comandos especiales.
- Usuarios conectados.
- Mensajes enviados.
- Mensajes recibidos.

Esto permitirá el mantenimiento de los requerimientos: [#1](#req1), [#2](#req2), [#3](#req3) y [#4](#req4).

Mediante el uso de 3 o más clientes conectados, se recomienda probar el comando `$private USER MSG` enviando un mensaje a uno de los usuarios conectados, de lo cual se espera el siguiente comportamiento.

- El usuario que envía el mensaje es confirmado del envío.
- El usuario emisor y receptor tendrá un mensaje iniciado con `(PRIVATE)`.
- Todo otro usuario no debe ver dicho mensaje.

Así se mantienen los requerimientos: [#5](#req5) y [#6](#req6)

#### Producción **(Tarea 1)**

Para iniciar una prueba en un servidor externo, debe ejecutar el siguiente comando:

```
python3 client/main.py URI
```

Donde `URI` corresponde a la URI en la que se encuentra el servidor, en nuestro caso: https://pychat-io.herokuapp.com/

## Protocolo de Migración

![Diagrama del protocolo de migración](https://i.imgur.com/9faygIn.png)

Puede observar el comportamiento de los procesos utilizando la herramienta disponible en su sistema operativo (Administrador de Tareas).

## Dev Notes

- El programa no funciona entre redes de distintos lugares (redes no LAN), debido a que se requiere la implementación de alguna estrategia tipo NAT Hole Punching o Port Forwarding para pasar a través de los routers privados.

## Manual de uso

El manual de uso de la aplicación se encuentra en el archivo [**README.txt**](README.txt) disponible en el repositorio de la app.
