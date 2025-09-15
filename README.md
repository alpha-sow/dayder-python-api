# DAYDER API

## Overview
DAYDER API is a FastAPI-based application that provides user management and announcements functionality.

## Default Admin User

The application automatically creates a default admin user on startup for easier initial setup and development.

### Configuration

The admin user credentials can be configured using environment variables:

- `ADMIN_USERNAME`: The username for the admin user (default: "admin")
- `ADMIN_PASSWORD`: The password for the admin user (default: "admin123")

### Environment Variables

Create a `.env` file in the project root with the following configuration:

```env
# Admin User Configuration
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_secure_password_here

# Security Configuration
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database Configuration
MONGO_URL=mongodb://localhost:27017/
```

### Production Security

⚠️ **Important for Production**: 
- Always set a strong password for the admin user using the `ADMIN_PASSWORD` environment variable
- Change the default `SECRET_KEY` to a secure random string
- The default development password "admin123" should never be used in production

### Startup Behavior

On application startup:
1. The system checks if an admin user with the configured username already exists
2. If no admin user exists, it creates one with the configured credentials
3. If using default credentials, a warning is logged
4. The admin user is created with full access to the system

### Login

Once the application is running, you can authenticate using:
- **Username**: The configured admin username (default: "admin")
- **Password**: The configured admin password (default: "admin123")

Use the `/token` endpoint to obtain an access token for authenticated requests.

## Running the Application

1. Install dependencies: `pip install -r requirements.txt`
2. Set up environment variables in `.env` file
3. Start the application: `uvicorn app.main:app --reload`
4. Access the API documentation at `http://localhost:8000/docs`

## API Endpoints

- `POST /token` - Authenticate and obtain access token
- `GET /users/me` - Get current user information
- `POST /users` - Create a new user
- `/announcements/*` - Announcement management endpoints

## Development

The application uses:
- FastAPI for the web framework
- MongoDB for data storage
- JWT for authentication
- Bcrypt for password hashing