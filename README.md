# 📚 Library Management API
A RESTful API for managing a library system, including books, borrowings, payments (with Stripe), and user authentication. Built with Django, Django REST Framework, and SimpleJWT.
## Main features
- User registration and login with JWT
- Create and update own profile
- View list of books and detailed information
- Borrow and return books
- Stripe integration for payments and fines
- Daily check for overdue borrowings

## Installing using GitHub

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/library-api.git
   cd library-api
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables: Create a `.env` file with the following:
   ```bash
   SECRET_KEY=your-secret-key
   DEBUG=True
   ALLOWED_HOSTS=*
   DATABASE_URL=postgres://user:password@localhost:5432/dbname
   STRIPE_SECRET_KEY=your_stripe_secret
   STRIPE_WEBHOOK_SECRET=your_webhook_secret
   ```

5. Apply migrations:
   ```bash
   python manage.py migrate
   ```

6. Run the server:
   ```bash
   python manage.py runserver
   ```
## Running with Docker
- Ensure Docker is installed on your system.
- Build and run the containers:
  ```bash
  docker-compose build
  docker-compose up
  ```
## API Documentation
The API is documented using DRF's built-in OpenAPI schema. You can explore it via:
  - `/scheme/swagger-ui/`
## Endpoints
### Authentication
- `POST /users/` - Register a new user
- `POST /users/token/` - Obtain JWT token
- `POST /users/token/refresh/` - Refresh token
- `GET /users/me/` - Retrieve your user data
- `PUT /users/me/` - Update your user data
### Books
- `GET /api/books/` - List all books (id, title, author)
- `GET /api/books/<id>/` - Retrieve full book details
### Borrowings
- `GET /borrowings/` - List all your borrowings (filterable)
- `POST /borrowings/` - Create a new borrowing
- `GET /borrowings/<id>/` - Borrowing details
- `POST /borrowings/<id>/return/` - Return the book
### Payments (Stripe)
- `GET /payments/` -  List all payments
- `POST /payments/` - Create a payment session for borrowing/fine
- `GET /payments/success/` - Success redirect URL (Stripe)
- `GET /payments/cancel/` - Cancel redirect URL (Stripe)
