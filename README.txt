Grupo 3 - Sistemas Distribuidos

* Integrantes:

- Juan Aguillón
- Benjamín Farías
- Tomás García
- Francisco Guíñez
- Christian Klempau
- Amaranta Salas

Profesor: Javier Bustos

############################################# NOTAS IMPORTANTES ###################################################
* Debe tener instalado python 3.8 (o más reciente) en su computador.
* La tarea fue testeada en su mayoría en Windows, por lo que recomendamos utilizar este SO al momento de correrla.
###################################################################################################################

* Servidor

Para correr el servidor, ejecutar la siguiente línea dentro de la carpeta 'server': "python3 main.py -N"
Donde N corresponde a cualquier número entero positivo (ej: "python3 main.py -2"). 

Esto ejecuta un server de relay que actúa como intermediario entre los clientes y servidores de chat actuales, dado que estos últimos van migrando y cambiando sus IP y puerto.
Este servidor de relay también actúa como controlador de los otros, recibiendo comandos para apagar y prender cualquiera de los 2 servidores de chat disponibles:

- "APAGAR -N": Apaga el servidor de chat número N (el N tiene que ser 1 o 2, y corresponder a un servidor actualmente prendido).
- "PRENDER -N": Prende el servidor de chat número N (el N tiene que ser 1 o 2, y corresponder a un servidor actualmente apagado).

* Cliente

Para correr un cliente, ejecutar la siguiente línea dentro de la carpeta 'client': "python3 main.py"

Los clientes del chat pueden enviar mensajes, y además tienen a su disposición el siguiente comando especial:

- "$private USER MSG": Enviar un mensaje privado "MSG" (que NO pasa por el servidor) al usuario de nombre USER.

La mensajería puede realizarse incluso si el destinatario está desconectado, en cuyo caso recibirá los mensajes al volver a conectarse.

* Arquitectura

La transmisión de mensajes se realiza mediante una arquitectura cliente servidor, con la particularidad de que hay 2 servidores replicados que van migrando cada 30 segundos cada uno (en caso de tener clientes a los que migrar).

Para coordinar las migraciones entre servidores y otorgar un punto de acceso estable al chat para los clientes,
añadimos un servidor `relay` (de relevo), el cual referencia a la dirección actual de cada servidor. Por ello, apenas se conecta
un nuevo cliente, este será redirigido al servidor actual más cercano de forma transparente (es decir, los clientes solo deben conectarse y no deben conocer la IP/Puerto del servidor `real` del chat).

El servidor de relevo guarda una referencia a la IP y puerto de los 2 servidores de chat actual, lo que se actualiza cada 30 segundos (en caso de que estos puedan migrar).
Esto permite realizar migraciones transparentes para el cliente, haciendo que las referencias a los servidores de 
chat anteriores ya no sean necesarias, por lo que simplemente se eliminan tras terminar el proceso de migración.

La distancia a los servidores se determina comparando sus IP a través de máscaras, y en caso de tener la misma IP se desempata con la que tenga el menor puerto.

El sistema es tolerante a fallas del lado del servidor, ya que al apagar uno de los servidores se aprovecha la existencia del otro servidor (replicado) para mantener el servicio funcional.
Además, si ambos servidores se apagan, los clientes seguirán conectados (sin poder hacer nada), y cuando se vuelva a prender cualquier servidor se resumirá la disponibilidad del chat.
Por último, un cliente desconectado podrá ver los mensajes que le llegaron mientras estaba inactivo al volver a conectarse.

* Consideraciones

- Es posible enviar mensajes de cualquier tipo antes de que se unan los primeros N usuarios, pero no se podrán ver hasta que el chat se active.

- Cuando el número de usuarios conectados alcance el valor N, el chat quedará activado permanentemente.
