## How to run

### Step 1

- Pull the latest repo of the project
- start with the docker command **docker compose build**
- then **docker compose up**

### Step 2

- Start the data generator service by a curl call
- curl -X POST http://generator/8083/start

### Step 3

- Start the carbon controller service by a curl call
- curl -X POST http://carbon:8084/start

### Step 4

- login to prometheus by this url
- http://localhost:3000

### Step 5

- login to grafana by this url
- http://localhost:9090

### Step 6


