CREATE TABLE IF NOT EXISTS raw_articles (
    url TEXT NOT NULL,
    country_code CHAR(2) NOT NULL,
    country_confidence REAL,
    source_name TEXT,
    pub_date TIMESTAMP,
    update_batch TIMESTAMP,
    themes TEXT,
    persons TEXT,
    organizations TEXT,
    locations_raw TEXT,
    tone_raw TEXT,
    UNIQUE (url, country_code)
);

CREATE INDEX IF NOT EXISTS idx_raw_country ON raw_articles (country_code);
CREATE INDEX IF NOT EXISTS idx_raw_batch ON raw_articles (update_batch);

CREATE TABLE IF NOT EXISTS country_articles (
    url TEXT NOT NULL,
    country_code CHAR(2) NOT NULL,
    country_confidence REAL,
    source_name TEXT,
    pub_date TIMESTAMP,
    update_batch TIMESTAMP,
    themes TEXT,
    persons TEXT,
    organizations TEXT,
    locations_raw TEXT,
    tone REAL,
    positive_score REAL,
    negative_score REAL,
    polarity REAL,
    theme_count INTEGER,
    person_count INTEGER,
    location_count INTEGER,
    total_location_count INTEGER,
    UNIQUE (url, country_code)
);

CREATE INDEX IF NOT EXISTS idx_ca_country ON country_articles (country_code);

CREATE TABLE IF NOT EXISTS top5_cache (
    country_code CHAR(2) NOT NULL,
    rank INTEGER NOT NULL,
    url TEXT NOT NULL,
    headline TEXT NOT NULL,
    relevancy_score REAL NOT NULL,
    country_name TEXT NOT NULL,
    source_name TEXT,
    themes TEXT,
    last_updated TIMESTAMP,
    is_cached BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (country_code, rank)
);

CREATE TABLE IF NOT EXISTS country_status (
    country_code CHAR(2) PRIMARY KEY,
    country_name TEXT,
    last_fresh_update TIMESTAMP,
    article_count INTEGER,
    status TEXT
);
