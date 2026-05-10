# WorldWide News
A web application that allows users to click on any country in the world and take a look at the most popular news articles from that country. Users can change various relevancy parameters to configure the different types of news they are interested in seeing. All news articles are sourced from the GDELT 2.0 API.

## Installation and Running

### PostgreSQL (required before running the backend)
Download PostgreSQL from here: [https://www.postgresql.org/download/](https://www.postgresql.org/download/) and follow the download instructions. Make sure that the PSQL is installed properly and also remember your username and password you entered.

### Additional Backend Setup
If you are using a cached CSV file, the script expects cached CSV to be in the backend folder. This is at the same location as the `CACHE_CSV` parameter. This is a CSV containing rows from the GDELT GKG api. By default, on startup the app will pull the third link (the gkg data) from [http://data.gdeltproject.org/gdeltv2/lastupdate.txt](http://data.gdeltproject.org/gdeltv2/lastupdate.txt). This process is rather expensive and if you would prefer this not to happen, then you can manually download the CSV from the link.

Further, the script expects `.env` file to be present in the backend folder. In should look similar to the following:
```
USER=postgres
PASS=mypassword
RUN_SETUP=True
USE_CACHE=True
CACHE_CSV=data/translingual.csv
```

The fields are as follows:
- `USER`: The initial superuser created during install. By default, this is postgres.
- `PASS`: The password associated with this user created during install. It is important to not forget this.
- `RUN_SETUP`: Boolean value representing whether or not to run the setup process, which consists of getting GKG data and setting up the database relations / inserting rows. This is a fairly expensive process so it is recommended to set this option to false after running the setup process once.
- `USE_CACHE`: Boolean value representing whether or not to use a cached CSV. Otherwise, the data will be loaded live from the GDELT API.
- `CACHE_CSV`: File path to your cached CSV (relative to the backend folder).  

Finally, install the required backend python packages:

```
python3 -m venv .venv
pip install -r requirements.txt
```

### Frontend Setup

Download Node.JS from here: [https://nodejs.org/en](https://nodejs.org/en) and follow the download instructions. Once installed, you can run the following commands:

```
cd frontend
npm i
```

## Running
It's recommended to have two terminals open for both the backend and frontend.

### Backend
```
cd backend

# Runs fastapi server
fastapi dev main.py
```

### Frontend
```
cd frontend

# Runs vite dev server
npm run dev
```

## Testing

### Frontend

The frontend is manually tested. The user should perform these steps:


1. Enter the website through the URL
2. Check for methodology being displayed on the page
3. Check About and Scoring pages can be opened closed, and scrolled on
4. Test dragging functionality with mouse (make sure not too laggy)
5. Click on a country, make sure it zooms in and displays country name, and highlights it
6. Check for popup when zoomed in with title, link, and publisher
7. Verify scoring sliders when used update articles displayed in a manner consistent with expectations
8. Click the zoom out button and make sure it goes back to original view seamlessly
9. Repeat steps 5-8 10 times.
10. Check the mousepad/scroll wheel zoom is smooth and functional. Try doing steps 5-8 while starting from a partially zoomed state. Additionally, when executing step 8, make sure it zooms back out to the full globe view if the user was zoomed in when entering the country view.


### Backend

The backend is tested using unit tests. In order to run tests, you will first need to setup a test database on Postgres. In PSQL, run the following command:

```sql
CREATE DATABASE worldwidenews_test;
```

Afterwards, you can run the test cases using pytest (which should be installed from the `requirements.txt`):

```
cd backend
pytest -v -s
```


