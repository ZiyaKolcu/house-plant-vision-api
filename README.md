# House Plant Vision - Backend API

**House Plant Vision** is a robust backend system designed to power a cross-platform mobile application (built with React Native/Expo). It enables users to identify houseplant species from photos with high accuracy using a fine-tuned deep learning model.
This API handles user authentication, image processing, AI inference, and plant data management using **FastAPI**, **PostgreSQL**, and **Redis**.

## Features

  * **AI-Powered Identification:** Integrates with Hugging Face Transformers to classify plant species from uploaded images using the `ZiyaKolcu/House-Plant-Vision-Model`.
  * **High-Performance API:** Built with **FastAPI** for asynchronous request handling and high throughput.
  * **Secure Authentication:** JWT-based authentication with token blacklisting (Logout functionality) utilizing **Redis**.
  * **Data Management:** Stores plant information, user profiles, and submission history in **PostgreSQL** using the `psycopg` (v3) async driver.
  * **Usage Logging:** Asynchronous logging of user actions and errors for system monitoring.
  * **Containerized Environment:** Fully dockerized setup for the database and caching layers.

## Tech Stack

  * **Framework:** FastAPI
  * **Database:** PostgreSQL
  * **Caching/Blacklist:** Redis
  * **ORM/Database Driver:** Psycopg 3 (Async)
  * **AI/ML:** PyTorch, Hugging Face Transformers, PIL (Pillow)
  * **Deployment/Dev:** Docker & Docker Compose

## Project Structure

```text
├── api
│   ├── core
│   │   └── config.py        # Environment configuration
│   ├── db
│   │   └── database.py      # Async Database connection logic
│   ├── routes               # API Route Controllers
│   │   ├── auth.py
│   │   ├── plants.py
│   │   └── ...
│   ├── utils
│   │   ├── image_utils.py   # Image saving and processing
│   │   ├── logger.py        # usage_logs insertion logic
│   │   └── blacklist.py     # Redis token management
│   └── services
│       └── submission_service.py # AI Inference & logic orchestration
├── docker-compose.yml       # DB and Redis container config
├── main.py                  # App entry point
└── requirements.txt
```

## Installation & Setup

### Prerequisites

  * Python 3.9+
  * Docker & Docker Compose (Recommended for DB/Redis)
  * CUDA-capable GPU (Optional, for faster AI inference)

### 1\. Clone the Repository

```bash
git clone https://github.com/yourusername/house-plant-vision-backend.git
cd house-plant-vision-backend
```

### 2\. Environment Configuration

Create a `.env` file in the root directory. Use the variables defined in `api/config.py`:

```ini
# Database Config
POSTGRES_HOST=localhost
POSTGRES_PORT=5433  # Mapped port in docker-compose
POSTGRES_USER=postgres
POSTGRES_PASSWORD=yourpassword
POSTGRES_DB=plant_vision_db

# Security
SECRET_KEY=your_super_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 3\. Start Infrastructure (Docker)

Start the PostgreSQL and Redis containers using Docker Compose. Note that PostgreSQL is mapped to port **5433** externally to avoid conflicts with local instances.

```bash
docker-compose up -d
```

### 4\. Install Dependencies

It is recommended to use a virtual environment.

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 5\. Run the Application

Start the FastAPI server:

```bash
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

## API Documentation

Once the server is running, you can access the interactive documentation (Swagger UI) at:

  * **Swagger UI:** `http://127.0.0.1:8000/docs`
  * **ReDoc:** `http://127.0.0.1:8000/redoc`

### Key Endpoints

#### Plants

  * `GET /api/v1/plants/`: Retrieve all plant species.
  * `GET /api/v1/plants/{common_name}`: Search for a plant by name.
  * `GET /api/v1/plants/id/{plant_id}`: Get detailed info by ID.

#### Submissions & AI

  * `POST /api/v1/submissions/`: Upload an image. The backend will:
    1.  Save the image locally.
    2.  Run the image through the `AutoModelForImageClassification`.
    3.  Save the prediction confidence and species to the database.
    4.  Return the identified plant details.

#### Authentication

  * `POST /api/v1/auth/login`: Get JWT access token.
  * `POST /api/v1/auth/logout`: Blacklist the current token via Redis.

## AI Model Details

The application uses a fine-tuned Vision Transformer model hosted on Hugging Face.

  * **Model Source:** `ZiyaKolcu/House-Plant-Vision-Model`
  * **Processor:** `AutoImageProcessor`
  * **Framework:** PyTorch

The `submission_service.py` handles the logic of loading the model onto the available device (CPU or CUDA) and processing the logits to determine the highest confidence species.

```python
# Snippet from submission_service.py
model = AutoModelForImageClassification.from_pretrained("ZiyaKolcu/House-Plant-Vision-Model")
logits = outputs.logits
predicted_idx = logits.argmax(-1).item()
```

## Security

  * **Token Management:** Uses Redis to implement a blacklist strategy, ensuring that logged-out tokens cannot be reused immediately.
  * **Data Validation:** Utilizes Pydantic schemas (`UserCreate`, `UserLogin`) to validate all incoming data.

## License

This project is licensed under the MIT License.
