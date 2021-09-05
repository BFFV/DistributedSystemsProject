Recomiendo usar virtualenv con Python 3.7.11

Primera versión basada en https://codeburst.io/building-your-first-chat-application-using-flask-in-7-minutes-f98de4adfa5d

Instalar paquetes necesarios con `pip install -r requirements.txt`.

Correr para que flask reconozca app: `export FLASK_APP=chat_app`.

Cambiar entre dev y production: `export FLASK_ENV=development/production`.

Activar o desactivar el debug mode: `export FLASK_DEBUG=True/False`.

Para crear un repositorio de migraciones usar `flask db init`

Para generar una migración usar `flask db migrate`

Para aplicar migraciones usar `flask db upgrade`

Cada vez que se cambia el modelo de la base de datos correr comandos 
`migrate` y `upgrade`.

Para sincronizar bd en otro sistema, refrescar carpeta de migraciones
desde la fuente y correr el comando `upgrade`

Para ver todos los comandos correr `flask db --help`. Para ayuda también puede 
revisar [aquí](https://flask-migrate.readthedocs.io/en/latest/)

Finalmente correr aplicación con `flask run`.

# Distributed Systems P1
La Tarea 1 es bastante simple: debe crear un servidor y clientes de chat.

Los clientes se conectan al servidor mediante una URL (definida por ustedes), todo lo que escriban debe ser visto por el resto de los clientes conectados a ese servidor.

1. El servidor maneja el ingreso de los clientes y el reenvío de los mensajes al resto de los clientes. Los mensajes deben mantener el orden y la integridad (completitud) en que se produjeron, y mantener el orden en que el servidor los recibe.

2. El servidor puede ser inicializado con un parámetro -n que indica que nadie ve ningún mensaje hasta que se conecten n usuarios, al conectarse el enésimo entonces todos reciben todos los mensajes en el orden que corresponda.

3. Un usuario puede enviar un mensaje privado a otro usuario sin pasar por el servidor y mantienen el orden.

Por simplicidad, no considere pérdida de mensajes.

La tarea es GRUPAL y deben inscribir el nombre del grupo.

Evaluación técnica:

1.0 Si su código no compila o no cumple con el mínimo (el punto 1)
4.0 Si logran el punto 1
5.5 Si logran el punto 1 y el punto 2 o el 1 y el 3.
7.0 Si logran los puntos 1, 2 y 3

Evaluación grupal:

Al entregar se les enviará una encuesta donde se pedirá el nombre de su grupo y su evaluación de los integrantes respondiendo la siguiente pregunta: ¿Qué % del total de la evaluación merece su compañera/o? y deberán anotar los nombres de todas/os con su porcentaje respectivo. **Si el nombre no aparece se asumirá un 0%**.

