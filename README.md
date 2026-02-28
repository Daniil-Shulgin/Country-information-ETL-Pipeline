# Junior DE test task


## Project Overview

This project is a complete data pipeline (ETL) that collects country information via a REST API, saves it to a PostgreSQL database, and visualizes the results through a Dash web interface.

## How to launch a project
 
1. **Clone the project into an empty folder**
    ```bash

    git clone https://github.com/Daniil-Shulgin/Junior-DE-test-task.git .
    
    ```

2. **Infrastructure Setup**
    ```bash

    docker-compose up -d
    
    ```

3. **Install Dependencies**
    ```bash

    pip install -r requirements.txt
    
    ```
    
4. **Run ETL Pipeline**
    ```bash

    python pipeline/ETL_pipeline.py
    
    ```
5. **Run Visualization**
    ```bash

    python dash/dash_visualization.py
    
    ```
6. **Once started, open your browser at: http://127.0.0.1:8050/**

## Tech Stack
 
1. **Python 3.x**
2. Pandas (Data processing)
3. SQLAlchemy (Database ORM)
4. PostgreSQL (Data storage)
5. Dash / Plotly (Visualization)
6. Docker (Infrastructure)
