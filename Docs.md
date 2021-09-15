# Chat App

En el siguiente documento detallaremos el proceso de desarrollo de la aplicación Chat App, correspondiente a los requerimientos, arquitectura, componentes, *testing* y manuales de uso (*end user*).

| Versión (Entrega)   | 1                                                            |
| ------------------- | ------------------------------------------------------------ |
| Épica               | Envío de mensajes privados                                   |
| Estado de Documento | Borrador                                                     |
| Equipo              | *Juan Aguillón* ([@vikingjuan](https://github.com/vikingjuan)) <br />*Benjamín Farías* ([@BFFV](https://github.com/BFFV)) <br />*Tomás García* ([@tgarcia5](https://github.com/tgarcia5)) <br />*Francisco Guíñez* ([@fguinez](https://github.com/fguinez))<br />*Christian Klempau* ([@Christian-Klempau](https://github.com/Christian-Klempau))<br />*Amaranta Salas* ([@amyaranta](https://github.com/amyaranta)) |

| Versión (Entrega)   | 2    |
| ------------------- | ---- |
| Épica               | -    |
| Estado de Documento | -    |
| Equipo              | -    |

| Versión (Entrega)   | 3    |
| ------------------- | ---- |
| Épica               | -    |
| Estado de Documento | -    |
| Equipo              | -    |



## Requerimientos

Se presentan los requerimientos del sistema solicitado mediante *user stories*:



| #                    | Título                        | Descripción                                                  | Prioridad | Notas                                                        |
| -------------------- | ----------------------------- | ------------------------------------------------------------ | --------- | ------------------------------------------------------------ |
| <a name="req1">1</a> | Ingreso al servidor           | Un usuario puede ingresar al servidor de chat                | Alta      |                                                              |
| <a name="req2">2</a> | Envío de mensajes al servidor | Un usuario puede enviar un mensaje al servidor               | Alta      |                                                              |
| <a name="req3">3</a> | Ver los mensajes              | Un usuario puede ver los mensajes enviados al servidor       | Alta      |                                                              |
| <a name="req4">4</a> | Usuarios mínimos conectados   | Un usuario no verá los mensajes pasados hasta que se hayan conectado N clientes | Media     | - El parámetro N puede cambiar mediante comando <br />- Por defecto N es evaluado como 2. |
| <a name="req5">5</a> | Envío de mensajes privados    | Un usuario puede enviar un mensaje privado a otro usuario    | Media     |                                                              |
| <a name="req6">6</a> | Ver los mensajes privados     | Un usuario puede ver los mensajes privados enviados por otro usuario | Media     |                                                              |
| <a name="req7">7</a> | Salir del servidor            | Un usuario puede salir del servidor mediante comando         | Baja      | - Para poder salir sin cerrar de manera indirecta (cerrar consola, ctrl + c) |

## Arquitectura

Como equipo decidimos utilizar la arquitectura **cliente-servidor** con estructura **monolítica**. 

El servidor se encuentra montado sobre un contenedor Dynos de Heroku disponible en: https://pychat-io.herokuapp.com/.

### *Deployment*

(Agregar instrucciones de *deployment*)

## Componentes

<img src="https://github.com/BFFV/DistributedSystemsP1/blob/docs/figs/filemap.drawio.png?raw=true" style="zoom:20%; align:left;" />

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

Posterior, comience a enviar mensajes por estos N-1 clientes, y posterior conecte el cliente número **N**. Esto permitirá el mantenimiento de los requerimientos: [#1](#req1), [#2](#req2), [#3](#req3) y [#4](#req4)

Luego, pruebe que la desconexión del servidor mediante el comando `$exit` con uno de los clientes, y una salida indirecta con otro cliente (cerrar consola o *Keyboard Interrupt*) para comprobar que el servidor sepa responder a dicha desconexión. Mantiene el requerimiento [#7](#req7).

Finalmente, corresponde 

#### Producción



## Manual de uso

El manual de uso de la aplicación se encuentra en el archivo **README.md** disponible en el repositorio de la app.