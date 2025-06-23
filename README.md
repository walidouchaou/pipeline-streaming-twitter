# Twitter Scraping Pipeline

This project is a data pipeline that scrapes tweets from specific Twitter accounts related to Paris public transport (RER and Metro) and stores them in a PostgreSQL database. The pipeline is orchestrated using Apache Airflow and the entire application is containerized using Docker.

## Features

- **Automated Scraping:** The pipeline automatically scrapes tweets every 5 minutes.
- **Scalable:** The use of Airflow and Docker allows for easy scaling of the application.
- **Resilient:** The pipeline is designed to be resilient to errors and failures.
- **Data Storage:** Scraped tweets are stored in a PostgreSQL database for easy access and analysis.
- **Containerized:** The entire application is containerized, making it easy to set up and run on any machine.

## Prerequisites

- Docker
- Docker Compose

## Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/votre-utilisateur/votre-repo.git
    cd votre-repo/piplineScrapingTwitter
    ```

2.  **Create a `.env` file:**

    Create a `.env` file in the `piplineScrapingTwitter` directory and add the following environment variables:

    ```
    POSTGRES_USER=airflow
    POSTGRES_PASSWORD=airflow
    POSTGRES_DB=airflow
    _AIRFLOW_WWW_USER_USERNAME=airflow
    _AIRFLOW_WWW_USER_PASSWORD=airflow
    ```

3.  **Build and run the containers:**

    ```bash
    docker-compose up --build -d
    ```

## Usage

Once the containers are running, you can access the Airflow UI at `http://localhost:8080`. The DAG `il_de_france_twitter` will be listed in the UI. You can enable it to start the scraping process.

The scraped tweets will be stored in the `tweets_db` PostgreSQL database. You can connect to this database using the following credentials:

-   **Host:** `localhost`
-   **Port:** `5433`
-   **Username:** `root`
-   **Password:** `root`
-   **Database:** `twitter_data`

## Project Structure

```
pipeline-streaming-twitter/
  - piplineScrapingTwitter/
    - dags/
      - __init__.py
      - BasePage.py
      - LoginPage.py
      - loginTwitter.py
      - main.py
      - test.py
      - twitter_database.py
      - twitter_login_dag.py
    - docker-compose.yml
    - Dockerfile
    - init-airflow.sh
    - requirements.txt
```

## Built With

-   [Python](https://www.python.org/)
-   [Apache Airflow](https://airflow.apache.org/)
-   [Selenium](https://www.selenium.dev/)
-   [Docker](https://www.docker.com/)
-   [PostgreSQL](https://www.postgresql.org/)
