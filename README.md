# V2 Funcionalidades
## Diseño tecnico
![alt text](/readme/image.png)
## EV_Central - NO DOCUMENTADO / SIN DIAGRAMA
### Endpoints

//Especificar payloads de cada endpoint
//Terminar la especificación de los endpoints

Especificación de endpoints:
- **Parte del navegador**:
  - http://Ev_central.es/
    - Este es el endpoint del frontend
    - Mostrara todos los datos
    - PERMITE -> (GET) 
               
- **Parte de api**:
  - http://EV_central.es/api/                   
    - http://EV_central.es/api/cps/
      - Este endpoint permtie guardar cps o leerlos todos
      - PERMITE -> (POST, GET)
      - Post para guardar un endpoint
      - get para leerlos todos              
      - http://EV_central.es/api/cps/:id
        - Este endpoint permite trabajar con un cp especifico via su id
        - PEMITE -> (POST, GET, DELETE, UPDATE)        
      - http://EV_central.es/api/cps/:city
        - Este endpoint permite recibir todos los CPS de una ciudad especifica
        - PERMITE -> (GET)
        - Payload:
          - X       
      - http://EV_central.es/api/cps/cities
        - Este endpoint devuelve todas las ciudades que contengan algun CP
        - PERMITE -> (GET)
        - Payload:
          - X     
    - http://EV_central.es/api/drivers/        
      - http://EV_central.es/api/drivers/:id    
    - http://EV_central.es/api/receipts/        
      - http://EV_central.es/api/receipts/:id   
    - http://EV_central.es/api/alerts/:city

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
        - En el caso

## Base de datos - NO DOCUMENTADO / SIN DIAGRAMA

## EV Registry - NO DOCUMENTADO / SIN DIAGRAMA

## Frontend
- Este módulo consistirá en una simple página web que, haciendo peticiones al API_Central, muestre el cuadro de monitorización de la central con todos sus elementos.
- Como se ha comentado anteriormente, este interfaz front deberá contener todos los elementos necesarios para visualizar claramente el estado de situación de todos los elementos del sistema: CPs (incluyendo su estado de registro, activación y token), Drivers, mensajes de error de cualquier parte del sistema, mensajes de estado del EV_W, clima, alertas ante cualquier fallo de cualquier módulo del sistema, etc.

Endpoint: http://Ev_central.es/