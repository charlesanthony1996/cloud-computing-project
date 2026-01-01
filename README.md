## How to run

### Step 1

- Pull the latest repo of the project
- start with the docker command **docker compose build**
- then **docker compose up**

### Step 2

- Start the data generator service by a curl call
- curl -X POST http://localhost/8083/start

### Step 2.1 (optional)

- Check the generator's status
- curl -X POST http://localhost:8083/status

### Step 2.2 (optional)

- Check the health of the ingestion service
- curl -X POST http://localhost:8081/health

### Step 3

- Start the carbon controller service by a curl call
- curl -X POST http://localhost:8084/start

### Step 4

- login to prometheus by this url
- http://localhost:3000

### Step 5

- login to grafana by this url
- http://localhost:9090

### Step 6


