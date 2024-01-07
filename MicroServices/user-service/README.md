# User Service

User Service is a backend microservice built with Flask. It provides APIs for user registration, login, profile management, and listing related operations.

## API Specification

### User Registration

- **URL**: `/register`
- **Method**: `POST`
- **Data Params**:
  ```
  {
    "username": "[username]",
    "password": "[password]",
    "confirm_password": "[confirm_password]",
    "fname": "[first_name]",
    "lname": "[last_name]",
    "email": "[email]"
  }
  ```
- **Success Response**:
  - **Code**: 201
  - **Content**: `{"success": True, "message": "User registered successfully"}`

- **CURL**:

```shell
curl -X POST http://localhost:9990/register -H "Content-Type: application/json" -d '{"username": "exampleUsername", "password": "examplePassword", "confirm_password": "examplePassword", "fname": "John", "lname": "Doe", "email": "john@example.com"}'
```

    


### User Login

- **URL**: `/login`
- **Method**: `POST`
- **Data Params**:
  ```
  {
    "username": "[username]",
    "password": "[password]"
  }
  ```
- **Success Response**:
  - **Code**: 200
  - **Content**: `{"success": True, "user": {"username": "user", "email": "user@example.com", "id": 1}}`

- **CURL**:

```shell
curl -X POST http://localhost:9990/login -H "Content-Type: application/json" -d '{"username": "exampleUsername", "password": "examplePassword"}'
```

### Get User Profile

- **URL**: `/user/<int:user_id>/profile`
- **Method**: `GET`
- **URL Params**: `user_id=[integer]`
- **Success Response**:
  - **Code**: 200
  - **Content**: `{"success": True, "data": [user data]}`
 
- *CURL**:

```shell
curl -X GET http://localhost:9990/user/1/profile
```


### Get Active Listings for a User

- **URL**: `/user/<int:user_id>/active-listings`
- **Method**: `GET`
- **URL Params**: `user_id=[integer]`
- **Success Response**:
  - **Code**: 200
  - **Content**: `{"success": True, "data": [listings]}`
- *CURL**:
```shell
curl -X GET http://localhost:9990/user/1/active-listings
```


### Get Bid History for a User

- **URL**: `/user/<int:user_id>/bid-history`
- **Method**: `GET`
- **URL Params**: `user_id=[integer]`
- **Success Response**:
  - **Code**: 200
  - **Content**: `{"success": True, "data": [bid history]}`
- *CURL**:
```shell
curl -X GET http://localhost:9990/user/1/bid-history
```

