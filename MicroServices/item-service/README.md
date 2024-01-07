# Item Service

Item Service is a backend microservice built with Flask. It provides APIs for listing and searching items, including photo and bid information.

## API Specification

### Get All Listings

- **URL**: `/listings`
- **Method**: `GET`
- **Curl Command**:
  ```
  curl -X GET http://localhost:9991/listings
  ```
- **Success Response**:
  - **Code**: 200
  - **Content**: `{"success": True, "data": [listings data]}`

### Search Listings

- **URL**: `/search`
- **Method**: `POST`
- **Data Params**:
  ```json
  {
    "searchquery": "search term"
  }
  ```
- **Curl Command**:
  ```
  curl -X POST http://localhost:9991/search -H "Content-Type: application/json" -d '{"searchquery": "search term"}'
  ```
- **Success Response**:
  - **Code**: 200
  - **Content**: `{"success": True, "data": [filtered listings data]}`
