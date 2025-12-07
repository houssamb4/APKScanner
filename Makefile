install:
	pip install -r requirements.txt

run:
	uvicorn main:app --reload

test:
	pytest tests/

docker-build:
	docker build -t apkscanner -f docker/Dockerfile .

docker-run:
	docker run -p 8000:8000 apkscanner

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete