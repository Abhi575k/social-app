# Example Requests

### Register

#### Request
```http
POST http://localhost:8000/api/register/
Content-Type: application/json

{
    "email": "temp@gmail.com",
    "password": "password"
}
```

#### Response
```json
{
  "user": {
    "id": 1,
    "email": "temp@gmail.com"
  },
  "token": "b2c21ea77cfdfe8ccf1d2c006784865de4e7f5efff6635f07b5f43f6ddfd21ee"
}
```

### Login

#### Request
```http
POST http://localhost:8000/api/login/
Content-Type: application/json

{
    "email": "temp@gmail.com",
    "password": "password"
}
```
#### Response
```json
{
  "user": {
    "id": 1,
    "email": "temp@gmail.com"
  },
  "token": "0e062d67d97efc9ac6f81da23fd88a669b5042e8890968bb5c44cf97ea4fe3b9"
}
```


### Logout

#### Request
```http
POST http://localhost:8000/api/logout/
Authorization: Token 0e062d67d97efc9ac6f81da23fd88a669b5042e8890968bb5c44cf97ea4fe3b9
```

#### Response
```json
{
  "message": "Successfully logged out"
}
```

### Profile View

#### Request

```http
GET http://localhost:8000/api/profile/
Authorization: Token 01765314b01c670ac3f559093bdd5669f51411bf42f7f4d01e4fe75ad7559d5f
```

#### Response

```json
{
  "id": 1,
  "email": "temp@gmail.com",
  "name": "",
  "date_joined": "2024-06-11T21:02:23.388200Z",
  "last_login": "2024-06-11T21:02:23.388231Z",
  "is_active": true,
  "is_staff": false,
  "is_superuser": false
}
```

### Profile Update

#### Request
```http
PUT http://localhost:8000/api/profile/
Content-Type: application/json
Authorization: Token b06cc6e528d3514c00690d080f1c45f0ee171dbffef7ed379e95e09af687d10c

{
    "name": "abhinav",
    "password1": "password1",
    "password2": "password1"
}
```

#### Response
```json
{
  "message": "Profile updated successfully"
}
```

### User Search

#### Request
```http
GET http://localhost:8000/api/search/?q=abhinav
Authorization: Token b06cc6e528d3514c00690d080f1c45f0ee171dbffef7ed379e95e09af687d10c
```

#### Response
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "abhinav",
      "email": "temp@gmail.com"
    }
  ]
}
```

### Send Friend Request

#### Request
```http
POST http://localhost:8000/api/send-request/
Content-Type: application/json
Authorization: Token 1eb4bf4eb4173562d6eb863aaa3e15f018f512f2fee7e598dec95055dc9e2dd1

{
    "to_user_id": 2
}
```

#### Response
```json
{
  "message": "Friend request sent successfully"
}
```

### View Sent Requests

#### Request
```http
GET http://localhost:8000/api/sent-requests/
Authorization: Token 1eb4bf4eb4173562d6eb863aaa3e15f018f512f2fee7e598dec95055dc9e2dd1
```

#### Response
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "",
      "email": "temp1@gmail.com"
    }
  ]
}
```

### View Received Requests

#### Request
```http
GET http://localhost:8000/api/received-requests/
Authorization: Token 1eb4bf4eb4173562d6eb863aaa3e15f018f512f2fee7e598dec95055dc9e2dd1
```

#### Response
```json
{
  "count": 0,
  "next": null,
  "previous": null,
  "results": []
}
```

### Friend Request Response

#### Request
```http
POST http://localhost:8000/api/request-response/
Content-Type: application/json
Authorization: Token bbc559870bed314a22e7edab59ec0a3ee13a3d68590461f4279c63fffc93a484

{
    "request_id": 1,
    "response": "accept/reject"
}
```

#### Response
```json
{
  "message": "Friend request response sent successfully"
}
```

### View Friends

#### Request
```http
GET http://localhost:8000/api/friends/
Authorization: Token bbc559870bed314a22e7edab59ec0a3ee13a3d68590461f4279c63fffc93a484
```

#### Response
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "abhinav",
      "email": "temp@gmail.com"
    }
  ]
}
```






