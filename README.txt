Grupo 3 - Sistemas Distribuidos

* Integrantes:

- Juan Aguillón ([@vikingjuan](https://github.com/vikingjuan))
- Benjamín Farías ([@BFFV](https://github.com/BFFV))
- Tomás García ([@tgarcia5](https://github.com/tgarcia5))
- Francisco Guíñez ([@fguinez](https://github.com/fguinez))
- Christian Klempau ([@Christian-Klempau](https://github.com/Christian-Klempau))
- Amaranta Salas ([@amyaranta](https://github.com/amyaranta))

Profesor: Javier Bustos

* Setup

1) Debe tener instalado python 3.7 (o más reciente) en su computador.
2) Instalar las siguientes librerías de python (abajo se dan 2 formas de realizar esto):

- flask
- flask_socketio
- python_socketio
- p2pnetwork
- requests

Opción A: Instalarlas con el comando: "python3 -m pip install flask flask-socketio python-socketio p2pnetwork requests"

Opción B: Instalarlas desde el archivo 'requirements.txt' incluido en la entrega, con el comando: "python3 -m pip install -r requirements.txt" 
(debe estar parado en la misma carpeta que el archivo para que funcione)

* Servidor

Para correr el servidor localmente, ejecutar la siguiente línea dentro de la carpeta 'server': "python3 main.py -N"
Donde N corresponde a cualquier número entero positivo (ej: "python3 main.py -2").

- Esto ejecuta un server que actúa como intermediario entre los clientes y el servidor actual, dado que este último va migrando y cambiando su IP y puerto.

* Cliente

Para correr un cliente, ejecutar la siguiente línea dentro de la carpeta 'client': "python3 main.py URI"
Donde URI corresponde a la URI en la que se encuentra el servidor intermediario, la que aparece al ejecutar lo indicado en la sección anterior (http://IP:5000).
Por ejemplo "python3 main.py http://192.168.1.110:5000".

- La IP del servidor se puede ver en la consola del servidor al momento de ejecutarlo, el puerto es siempre el 5000.
- Si no entregas el argumento URI, se asume que estás intentando conectarte a un servidor local en http://127.0.0.1:5000.

Los clientes del chat pueden enviar mensajes, y además tienen a su disposición el siguiente comando especial:

- "$private USER MSG": Enviar un mensaje privado "MSG" (que NO pasa por el servidor) al usuario de nombre USER.

* Arquitectura

La transmisión de mensajes se realiza mediante una arquitectura cliente servidor, con la particularidad de que el
servidor que transmite los mensajes a los demás clientes migra entre los equipos de los clientes cada 30 segundos.

Para coordinar las migraciones del servidor y otorgar un punto de acceso estable al chat para los clientes,
añadimos un servidor `relay` (de relevo), el cual referencia a la dirección del servidor actual. Por ello, apenas se conecta
un nuevo cliente, este será redirigido al servidor actual de forma transparente (es decir, los clientes solo deben conectarse
al servidor ejecutado según lo explicado en la sección de 'Servidor' más arriba, y no deben conocer la IP/Puerto del servidor `real` del chat).

El servidor de relevo guarda una referencia a la IP y puerto del servidor de chat actual, lo que se actualiza cada 30 segundos.
Esto permite realizar migraciones transparentes para el cliente, a la vez que asegura que las referencias a los servidores de chat
anteriores ya no son necesarias, por lo que simplemente se eliminan tras terminar el proceso de migración.

* Testing

En la documentación "Docs.md" se pueden encontrar algunas formas de testear la tarea.

* Consideraciones

- Es posible enviar mensajes de cualquier tipo antes de que se unan los primeros N usuarios, pero no se podrán ver hasta que el chat se active.

- Cuando el número de usuarios conectados alcance el valor N, el chat quedará activado permanentemente.
