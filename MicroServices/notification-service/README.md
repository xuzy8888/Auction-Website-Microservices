# Email Service

Email Service is a flask backend application to send email notifications and alerts.

# API
## 1. Send notifications
* **URL**: /notice
* **Method**: POST
* **Command**:
    ```
    curl -X POST http://localhost:9982/notice -H "Content-Type: application/json" -d '{"msg": "notice message", "receiver": "example@domain"}'
    ```
* **Response**:
    
    * **Code**: 200
    * **Content**: `{"Success": True, "error": None}`


## 2. Send Alerts
* **URL**: /alert
* **Method**: POST
* **Command**:
    ```
    curl -X POST http://localhost:9982/alert -H "Content-Type: application/json" -d '{"msg": "alert message", "receiver": "example@domain"}'
    ```
* **Response**:
    
    * **Code**: 200
    * **Content**: `{"Success": True, "error": None}`