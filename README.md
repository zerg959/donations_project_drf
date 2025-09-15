# GroupCollectAPI
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white)
![Redis](https://img.shields.io/badge/redis-%23DD0031.svg?&style=for-the-badge&logo=redis&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)

**GroupCollectAPI** is a Django REST Framework backend for managing collective fundraising campaigns (donation collections). It allows users to create donation goals, contribute to them, and track payments in real time.

Built with:
-  **Django & Django REST Framework**
-  **Database** SQLite
-  **Caching** Redis
-  **JWT Authentication** SimpleJWT (registration, login, profile)
-  **Image uploads** for collections
-  **Payment tracking**
-  **Custom business logic** (auto-increment collected amount, participants count, goal completion)
-  **Auto-generated API documentation** via Swagger UI and ReDoc

---
## Features

### Core Functionality
- User registration and JWT-based authentication
- Create, read, update, and delete donation collections
- Upload images for each collection
- Make payments to any collection
- View payment feed for a specific collection
- Automatic calculation of:
  - Total collected amount
  - Number of unique contributors
  - Goal completion (auto-close when target reached)

### Permissions
- Only the **author** of a collection can edit or delete it
- Anyone can view collections and make payments
- Full protection against unauthorized modifications

### Notifications
*Ssent to console in dev mode*
- Email sent to the author upon successful creation of a new collection.
- Email sent to the donor upon successful creation of a new paymnet.

### API Documentation
- Interactive docs available at:
  - [http://localhost:8000/swagger/](http://localhost:8000/swagger/)

---

## Quick Start with Docker

This project is fully containerized. <br>
You can run it using **Docker** and **Docker Compose plugin** (`docker compose`, not `docker-compose`).

### Prerequisites

1) Make sure you have installed:
- [Docker Engine](https://docs.docker.com/engine/install/)
- [Docker Compose Plugin](https://docs.docker.com/compose/install/) (comes with Docker Desktop or install separately)
2) Check installation:
```bash
docker --version
docker compose version
```
3) Clone the repository:
```bash
git clone https://git@github.com:zerg959/donations_project_drf.git
cd donations_project_drf
```
4) Create .env file with secret keys:
```bash
touch .env
```
5) Add to .env-file basic settings:<br>
```python
DEBUG=True
SECRET_KEY=change-this-to-a-secure-secret-key
REDIS_URL=redis://redis:6379/1
```
7) Create directories for database and media
```bash
mkdir -p db media
```
8) Create empty db file.
```bash
touch db/db.sqlite3
```
9) Build container and start Docker
```bash
docker compose up --build
```
On first run, this will:<br>
- Build the Docker image<br>
- Install Python dependencies<br>
- Apply database migrations<br>
- Start the Django development server on port 8000<br>
- Start the Redis on port 6379

10)  Run migrations (if not done automatically)
```bash
docker compose run --rm api python manage.py makemigrations
docker compose run --rm api python manage.py migrate
```
11) You can run custom management commands inside the container.<br>
Generates 10 users, 50 collections, 100 payments by default: 
```bash
docker compose run --rm api python manage.py generate_fake_data
```
For custom numbers use: 
```bash
docker compose run --rm api python manage.py generate_fake_data --users 200 --collections 100 --payments 2000
```
12) Create a superuser (optional) to access Django admin (localhost/admin).
```bash
docker compose run --rm api python manage.py createsuperuser
```
### Use the API

Once the server is running, open the following in your browser:

- **Swagger UI**: [http://localhost:8000/swagger/](http://localhost:8000/swagger/)
- **Admin Panel**: [http://localhost:8000/admin/](http://localhost:8000/admin/)

#### Example API Flow
**Register a user**  
   `POST /api/auth/register/`  
   ```json
   {
     "username": "your_username",
     "email": "user@example.com",
     "password": "your_password",
     "password_confirm": "your_password"
   }
   ```
**Get JWT tokens**  
   `POST /api/token/`  
   ```json
    {
    "username": "your_username",
    "password": "your_password"
    }
```
**Set Authorization in Swagger**
In Swagger UI, click "Authorize" and enter:
   `Bearer <your_access_token>`

**Make a payment**
`POST /api/collections/{id}/pay/`
 ```json
    {
    "amount": 1000,
    }
  ```
**Create a collection**  
`POST /api/collections/`  
   ```json
        {
        "title": "Wedding Fund",
        "purpose": "wedding",
        "description": "Help us celebrate our wedding!",
        "target_amount": 50000,
        "image": "file"
        }

   ```











