# Experiment 9 - Authentication using JWT (Flask)

This project demonstrates three authentication approaches using a simple Flask API:

- Basic Authentication (Authorization header)
- Simple Token Authentication (custom header)
- JWT Authentication (Bearer token)

## Tech Stack

- Python (Flask)
- Flask-JWT-Extended

## Setup (Windows)

1. Create and activate a virtual environment:

```powershell
python -m venv venv
.\venv\Scripts\activate
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Run the server:

```powershell
python app.py
```

Server will run on:

- http://127.0.0.1:5000

## Routes

- `GET /`
- `GET /basic-protected`
- `POST /token-login`
- `GET /token-protected`
- `POST /jwt-login`
- `GET /jwt-protected`
- `GET /jwt-admin`

## Testing with Postman

### 1) JWT Login

- Method: `POST`
- URL: `http://127.0.0.1:5000/jwt-login`
- Headers:
  - `Content-Type: application/json`
- Body (raw JSON):

```json
{
  "username": "admin",
  "password": "admin123"
}
```

Copy `access_token` from the response.

Optional: In the **Tests** tab, save token to an environment variable named `jwt`:

```javascript
const jsonData = pm.response.json();
pm.environment.set("jwt", jsonData.access_token);
```

### 2) JWT Protected

- Method: `GET`
- URL: `http://127.0.0.1:5000/jwt-protected`
- Authorization tab:
  - Type: `Bearer Token`
  - Token: `{{jwt}}` (or paste the copied token)

### 3) JWT Admin (Role based)

- Method: `GET`
- URL: `http://127.0.0.1:5000/jwt-admin`
- Authorization:
  - Bearer Token: `{{jwt}}`

Login as `admin/admin123` to get access.

Login as `john/john123` to see a `403` response.

### 4) Basic Auth

- Method: `GET`
- URL: `http://127.0.0.1:5000/basic-protected`
- Authorization tab:
  - Type: `Basic Auth`
  - Username: `admin`
  - Password: `admin123`

### 5) Simple Token Auth

1. Token login

- Method: `POST`
- URL: `http://127.0.0.1:5000/token-login`
- Headers:
  - `Content-Type: application/json`
- Body:

```json
{
  "username": "admin",
  "password": "admin123"
}
```

2. Token protected

- Method: `GET`
- URL: `http://127.0.0.1:5000/token-protected`
- Header:
  - `x-auth-token: <token from /token-login>`

## Testing with curl

### Basic Auth

```bash
curl -u admin:admin123 http://127.0.0.1:5000/basic-protected
```

### Simple Token Auth

```bash
curl -X POST http://127.0.0.1:5000/token-login -H "Content-Type: application/json" -d '{"username":"admin","password":"admin123"}'
```

Then:

```bash
curl http://127.0.0.1:5000/token-protected -H "x-auth-token: <token>"
```

### JWT Auth

```bash
curl -X POST http://127.0.0.1:5000/jwt-login -H "Content-Type: application/json" -d '{"username":"admin","password":"admin123"}'
```

Then:

```bash
curl http://127.0.0.1:5000/jwt-protected -H "Authorization: Bearer <jwt_token>"
```

Admin-only:

```bash
curl http://127.0.0.1:5000/jwt-admin -H "Authorization: Bearer <jwt_token>"
```
