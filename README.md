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

- Visit prometheus by this url
- http://localhost:9090

- Add data source:
- Settings -> Data Sources -> Add
- Type: Prometheus
- url: http://localhost:9090
- Save and test

### Step 5

- login to grafana by this url
- http://localhost:3000
- username: admin
- password: admin

### Step 6

- Force behaviour changes to test whether rate changes
- curl -X POST http://localhost:8083/self-rate -H "Content-Type: application/json" -d '{"rate":"high"}'

- The watch:
- generator speed increases
- ingestion fills faster
- carbon controller works

### Step 7

- Create panels by typing these terms on the query input text field
- ingestion_buffer_size
- generator_rate
- ingestion_fog_total
