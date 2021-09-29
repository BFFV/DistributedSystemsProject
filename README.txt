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
- p2pnetwork
- requests

Opción A: Instalarlas con el comando: "python3 -m pip install flask flask-socketio p2pnetwork requests"

Opción B: Instalarlas desde el archivo 'requirements.txt' incluido en la entrega, con el comando: "python3 -m pip install -r requirements.txt" 
(debe estar parado en la misma carpeta que el archivo para que funcione)

* Servidor

Para correr el servidor localmente, ejecutar la siguiente línea dentro de la carpeta 'server': "python3 main.py -N"
Donde N corresponde a cualquier número entero positivo (ej: "python3 main.py -2").

* Cliente

Para correr un cliente, ejecutar la siguiente línea dentro de la carpeta 'client': "python3 main.py URI"
Donde URI corresponde a la URI en la que se encuentra el servidor (http://IP:5000). Por ejemplo "python3 main.py http://192.168.1.110:5000".

- La IP del servidor se puede ver en la consola del servidor al momento de ejecutarlo, el puerto es siempre el 5000.
- Si no entregas el argumento URI, se asume que estás intentando conectarte a un servidor local en http://127.0.0.1:5000.

Los clientes del chat pueden enviar mensajes, y además tienen a su disposición los siguientes comandos especiales (también indicados en la interfaz del programa):

- "$exit": Permite al cliente salirse del chat y terminar su programa (equivalente a hacer CTRL+C).
- "$private USER MSG": Enviar un mensaje privado "MSG" (que NO pasa por el servidor) al usuario de nombre USER.
- "$reset -N": Reiniciar el servidor a su estado inicial con un nuevo parámetro N (los clientes que estaban conectados actualmente serán desconectados y se perderán los datos de esta sesión).

* Consideraciones

- Es posible enviar mensajes de cualquier tipo antes de que se unan los primeros N usuarios, pero no se podrán ver hasta que el chat se active.

- Cuando el número de usuarios conectados alcance el valor N, el chat quedará activado permanentemente, a menos que se utilice el comando `$reset -N` desde algún cliente. 
Este último comando permite volver a fijar un valor de N y reiniciar todo.

- Los comandos especiales del cliente ('$exit', '$private', '$reset') son indicados dentro de la interfaz del chat.