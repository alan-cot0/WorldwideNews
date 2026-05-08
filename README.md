# WorldWide News
A web application that allows users to click on any country in the world and take a look at the most popular news articles from that country. Users can change various relevancy parameters to configure the different types of news they are interested in seeing. All news articles are sourced from the GDELT 2.0 API.

## Installation and Running

### PostgreSQL (required before running the backend)
Download PostgreSQL from here: [https://www.postgresql.org/download/](https://www.postgresql.org/download/) and follow the download instructions. Make sure that the psql is installed properly and also remember your username and password provided.

### Additional Backend Setup
If you are using a cached CSV file, the script expects `data/gkg.csv` to be in the backend folder. This is a CSV containing rows from the GDELT GKG api. By default, on startup the app will pull the third link (the gkg data) from [http://data.gdeltproject.org/gdeltv2/lastupdate.txt](http://data.gdeltproject.org/gdeltv2/lastupdate.txt). This process is rather expensive and if you would prefer this not to happen, then you can manually download the CSV from the link.

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

```bash
python3 -m venv .venv
pip install -r requirements.txt
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
npm i
# Runs vite dev server
npm run dev
```

## Testing

### Backend

### Frontend