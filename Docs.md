# Chat App

En el siguiente documento detallaremos el proceso de desarrollo de la aplicación Chat App, correspondiente a los requerimientos, arquitectura, componentes, *testing* y manuales de uso (*end user*).

| Versión (Entrega)   | 1                                                            |
| ------------------- | ------------------------------------------------------------ |
| Épica               | Envío de mensajes privados                                   |
| Estado de Documento | Borrador                                                     |
| Equipo              | *Juan Aguillón* ([@vikingjuan](https://github.com/vikingjuan)) <br />*Benjamín Farías* ([@BFFV](https://github.com/BFFV)) <br />*Tomás García* ([@tgarcia5](https://github.com/tgarcia5)) <br />*Francisco Guíñez* ([@fguinez](https://github.com/fguinez))<br />*Christian Klempau* ([@Christian-Klempau](https://github.com/Christian-Klempau))<br />*Amaranta Salas* ([@amyaranta](https://github.com/amyaranta)) |

| Versión (Entrega)   | 2    |
| ------------------- | ---- |
| Épica-              | -    |
| Estado de Documento | -    |
| Equipo              | -    |

| Versión (Entrega)   | 3    |
| ------------------- | ---- |
| Épica-              | -    |
| Estado de Documento | -    |
| Equipo              | -    |



## Requerimientos

Se presentan los requerimientos del sistema solicitado mediante *user stories*:

| #    | Título                        | Descripción                                                  | Prioridad | Notas                                                        |
| ---- | ----------------------------- | ------------------------------------------------------------ | --------- | ------------------------------------------------------------ |
| 1    | Ingreso al servidor           | Un usuario puede ingresar al servidor de chat                | Alta      |                                                              |
| 2    | Envío de mensajes al servidor | Un usuario puede enviar un mensaje al servidor               | Alta      |                                                              |
| 3    | Ver los mensajes              | Un usuario puede ver los mensajes enviados al servidor       | Alta      |                                                              |
| 4    | Usuarios mínimos conectados   | Un usuario no verá los mensajes pasados hasta que se hayan conectado N clientes | Media     | - El parámetro N puede cambiar mediante comando <br />- Por defecto N es evaluado como 2. |
| 5    | Envío de mensajes privados    | Un usuario puede enviar un mensaje privado a otro usuario    | Media     |                                                              |
| 6    | Ver los mensajes privados     | Un usuario puede ver los mensajes privados enviados por otro usuario | Media     |                                                              |



## Arquitectura

Como equipo decidimos utilizar la arquitectura **cliente-servidor** con estructura **monolítica**. 

El servidor se encuentra montado sobre un contenedor Dynos de Heroku disponible en: https://pychat-io.herokuapp.com/.

### *Deployment*

(Agregar instrucciones de *deployment*)

## Componentes



<img src="D:\Users\Juan\Desktop\Distribuidos\Tarea 1\DistributedSystemsP1\figs\filemap.drawio.png" style="zoom:67%; align:left;" />

## Testeo 





## Manual de uso

El manual de uso de la aplicación se encuentra en el archivo **README.md** disponible en el repositorio de la app.