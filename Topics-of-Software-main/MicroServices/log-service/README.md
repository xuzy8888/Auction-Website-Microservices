# Log Service

Log Service is a flask backend application to read and write logs.

# API
## 1. Write log to DB
* **URL**: /log
* **Method**: POST
* **Command**:
    ```
    curl -X POST http://localhost:9981/log -H "Content-Type: application/json" -d '{"msg": "your log message"}'
    ```
* **Response**:
    
    * **Code**: 200
    * **Content**: `{"Success": True}`


## 2. Check logs from DB
* **URL**: /logReader
* **Method**: GET
* **Command**:
    ```
    curl -X GET http://localhost:9981/logReader
    ```
* **Response**:
    
    * **Code**: 200
    * **Content**: `{"Success": True, 'log': logs}`