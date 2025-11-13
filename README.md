# V2 Funcionalidades
Cosas a tener en cuenta:
- Se tiene que tener una posibilidad de controlar completamente los cps desde la central, ignorando el hecho de que TENGA O NO salida de forntend
- Tambien se tiene que tener la posiblida de controlar los cps desde la linea de comandos de cada uno
- Cada uno de ellos tiene que mostrar los datos, lo que pasa por pantalla y consola

## Diseño tecnico
![alt text](/readme/image.png)
## EV_Central - NO DOCUMENTADO / SIN DIAGRAMA
### Endpoints

//Especificar payloads de cada endpoint

Especificación de endpoints:
- **Parte del navegador**:
  - http://Ev_central.es/
    - Este es el endpoint del frontend
    - Mostrara todos los datos
    - PERMITE -> (GET) 
               
- **Parte de api**:
  - http://EV_central.es/api/
    - No permite nada                   
    - http://EV_central.es/api/cps/
      - Este endpoint permtie guardar cps o leerlos todos
      - PERMITE -> (POST, GET)
      - Post para guardar un endpoint
      - get para leerlos todos
      - Payload (POST):
        - X
      - Payload (GET):
        - X              
      - http://EV_central.es/api/cps/:id
        - Este endpoint permite trabajar con un cp especifico via su id
        - PEMITE -> (GET, DELETE, UPDATE)    
        - Payload (GET):
          - X
        - Payload (DELETE):
          - X
        - Payload (UPDATE):
          - X
      - http://EV_central.es/api/cps/:city
        - Este endpoint permite recibir todos los CPS de una ciudad especifica
        - PERMITE -> (GET)
        - Payload:
          - X       
      - http://EV_central.es/api/cps/cities
        - Este endpoint devuelve todas las ciudades que contengan algun CP
        - PERMITE -> (GET)
        - Payload (GET):
          - X
    - http://EV_central.es/api/drivers/
    	- Este endpoint muestra todos los drivers
      - PERMTIE -> (POST, GET)
      - Payload (POST):
        - X
      - Payload (GET):
        - X
      - http://EV_central.es/api/drivers/:id
      - Este endpoint permite trabajar con un driver especifico
      - PERMiTE -> (GET, DELETE, UPDATE)
      - Payload (GET):
        - X
      - Payload (DELETE):
        - X
      - Payload (UPDATE):
        - X
    - http://EV_central.es/api/receipts/
    - Este endpoint muestra todos los recibos
      - PERMITE -> (POST, GET)
      - Payload (POST):
        - X
      - Payload (GET):
        - X        
      - http://EV_central.es/api/receipts/:id
      - Este endpoint permite trabahar con un recibo especifico
      - PERMITE -> (GET, DELETE, UPDATE)
      - Payload (GET):
        - X
      - Payload (DELETE):
        - X
      - Payload (UPDATE):
        - X   
    - http://EV_central.es/api/alerts/:city
    - Este endpoint sirve para postear alertas en caso de que alguna de las ciudades tenga temoeratura negativa, sera usado por **WCO**
    - PERMITE -> (POST)
    - Payload (POST):
      - X

### Practica 2 

Lo que pide la practica:
- **Dato 1 ❌**: Consumo de API_rest de una Oficina de Control de Clima: EV_Central expondrá un interface (API) para que un nuevo módulo llamado EV_W (Weather Control Office) le informe si la localización en la que se encuentra un CP tiene una climatología adecuada para su uso. Para ello, EV_W ante una situación de alerta climatológica en una determinada localización, notificará dicha alerta vía API a EV_Central . Más adelante se indica el funcionamiento de EV_W.
    - A tener en cuenta:
      - Con openWheater se puede hacer llamadas API (Consultas) para una ciudad / region especifica
      - Las consultas se tienen que hacer cada 4 segundos
    - **Mi solución**:
      - ❌ WCO va a tener un banco de datos con las ciudades (Ciudades)
        - El banco de datos sera un array de datos guardados en memoria
        - Tendra el siguente formato:
          - CIUDADES: Array[String] = ["Ciudad1", "Ciudad2"...]
      - ❌ WCO no va a realizar ningun tipo de petición hasta que no tenga al menos una ciudad en su banco de datos
      - ❌ WCO recibira las ciudades que se tiene que tener en cuenta para realizar las consultas cada vez que:
        - Se realiza un cambio en la base de datos respecto a los CPs (POST, UPDATE, DELETE)
        - Recibira las ciudades en este **ENDPOINT** -> http://IpWCO:Puerto/api/cities
        - Con este formato:
          - {ciudad, ciudad, ciudad...}
      - ❌ WCO actualizara el banco de datos cada vez que reciba los datos
      - ❌ WCO cada 4 segundos realizara una peticion a https://openweathermap.org/ usando su API:
        - ![alt text](/readme/apiConsulta.png)
        - Este es el formato de la consulta a realizar
        - ![alt text](/readme/response.png)
        - Este es el formato de la respuesta a esperar
        - Cada 4 segundos, el programa recorrera el array, realizando las peticiones a cada una de las ciudades dentro de este
        - Al realizar esa peticion y recibir la respuesta, la desenglosa, traduciendo la temperatura de kelvins a grados
        - En el caso de que la temperatura sea negativa, enviara al endpoint de alertas (http://EV_central.es/api/alerts/:city), una alerta.
- **Dato 2 ❌**: Implementación de la autenticación entre EV_Central y los CP: Como se ha comentado anteriormente, para poder realizar la autenticación, los CPs previamente se deberán de haber registrado en el EV_Registry. Tras el proceso de registro los CPs estarán disponibles para su uso. Para ello deberán autenticarse en EV_Central con las credenciales que EV_Registry habrá proporcionado a tal propósito. En el momento de la autenticación, si esta se resuelve con éxito, la central devolverá a EV_M, la clave (de cifrado simétrico ÚNICA POR CP) que deberá ser usada por este para el cifrado de todos los mensajes que envíe a la Central. La central descifrará los mensajes teniendo en cuenta dicha clave. Estas claves podrán ser revocadas por EV_Central ante una supuesta vulnerabilidad de la seguridad. Para simular este efecto, en EV_Central, se implementará una opción para restaurar claves. Al pulsarla, se borrarán las claves de un CP específico el cual quedará fuera de servicio. Esto obligará a EV_CP_M a realizar una nueva autenticación mediante una opción incorporada en el mismo y, de esta manera, obtener sus nuevas claves de cifrado. Opcional: Tal y como se refleja en el diagrama de arquitectura conceptual, la autenticación seguirá siendo por sockets pero el alumno que lo desee podrá implementar un API Rest entre CP y Central a tal propósito lo que, en la práctica profesional sería más correcto. En este caso Central expondría un API de Autenticación que el CP consumiría.
  

## Base de datos - NO DOCUMENTADO / SIN DIAGRAMA

//

DATOS:
- CP:
  - ID: UUID
  - JWT: STRING
  - LastAccess:
  - DataRegistry:
  - Ciudad:
  - Calle: 
  - Precio: 
  - 

## EV Registry - NO DOCUMENTADO / SIN DIAGRAMA

## Frontend
- Este módulo consistirá en una simple página web que, haciendo peticiones al API_Central, muestre el cuadro de monitorización de la central con todos sus elementos.
- Como se ha comentado anteriormente, este interfaz front deberá contener todos los elementos necesarios para visualizar claramente el estado de situación de todos los elementos del sistema: CPs (incluyendo su estado de registro, activación y token), Drivers, mensajes de error de cualquier parte del sistema, mensajes de estado del EV_W, clima, alertas ante cualquier fallo de cualquier módulo del sistema, etc.

Endpoint: http://Ev_central.es/