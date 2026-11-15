CREATE TABLE IF NOT EXISTS weather_daily (
    location            TEXT NOT NULL,
    date                DATE NOT NULL,
    avg_temperature     REAL,
    avg_humidity        REAL,
    total_precipitation REAL,
    max_wind_speed      REAL,
    ingested_at         TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (location, date)
);