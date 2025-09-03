# ACEest Fitness & Gym - Workout Tracker

Flask web app for tracking workouts. Features Docker support, REST API, automated tests, and CI/CD pipeline.

## Features

- Add/view workouts
- REST API
- Docker containerization
- Automated tests (pytest)
- CI/CD with GitHub Actions

## Quick Start

1. Clone repo: `git clone https://github.com/mach2605/aceest-fitness.git`
2. Install Python 3.11+, (optional: Docker)
3. Install dependencies: `pip install -r requirements.txt`
4. Run: `python app.py` (or use Docker)

### 1. Clone the Repository

```bash
git clone https://github.com/mach2605/aceest-fitness.git
cd aceest-fitness
```

docker build -t aceest-fitness .
docker run -d -p 5000:5000 --name fitness-app aceest-fitness

### Docker Usage

Build: `docker build -t aceest-fitness .`
Run: `docker run -d -p 5000:5000 aceest-fitness`
App: [http://localhost:5000](http://localhost:5000)

docker build -t aceest-fitness:latest .
docker build -t aceest-fitness:v1.0 .
docker run -d -p 5000:5000 --name fitness-app aceest-fitness
docker run -d -p 5000:5000 -e FLASK_ENV=production --name fitness-app aceest-fitness
docker run -d -p 5000:5000 -v $(pwd):/app --name fitness-app aceest-fitness
docker logs fitness-app
docker exec -it fitness-app bash
docker stop fitness-app && docker rm fitness-app
docker exec fitness-app curl -f http://localhost:5000/health

## API Endpoints

- `GET /api/workouts` - List workouts
- `POST /api/workouts` - Add workout
- `DELETE /api/workouts/{id}` - Delete workout
- `GET /health` - Health check

pip install pytest pytest-flask pytest-cov
docker run --rm -v $(pwd):/app -w /app aceest-fitness:latest pytest -v
docker run --rm -v $(pwd):/app -w /app aceest-fitness:latest pytest --cov=app --cov-report=term-missing

## Testing

Run tests: `pytest` (or in Docker)

## CI/CD Pipeline

Automated build, test, and deploy via GitHub Actions. See `.github/workflows/main.yml`.

## Tech Stack

- Frontend: HTML, CSS, JS
- Backend: Python 3.11, Flask
- Testing: Pytest
- Container: Docker
- CI/CD: GitHub Actions

## Deployment

Run in production: set `FLASK_ENV=production` and use Docker or cloud platforms (AWS, GCP, Azure, Heroku, DigitalOcean).
