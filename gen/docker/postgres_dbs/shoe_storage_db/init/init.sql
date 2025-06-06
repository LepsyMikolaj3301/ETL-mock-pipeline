-- CREATE TABLESPACE shoe_tablespace LOCATION '/mnt/tablespace';

-- Create the user
DO
$$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'etl') THEN
      CREATE ROLE etl WITH LOGIN PASSWORD 'etl';
   END IF;
END
$$;
-- Grant connection and usage on the database
GRANT CONNECT ON DATABASE shoe_storage TO etl;

-- Grant privileges on schema public

\connect shoe_storage
GRANT USAGE ON SCHEMA public TO etl;

-- Grant privileges on all tables in public schema
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO etl;

-- Ensure future tables grant access too
ALTER DEFAULT PRIVILEGES IN SCHEMA public
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO etl;

-- Grant usage on sequences (for serial IDs, etc.)
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO etl;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
  GRANT USAGE ON SEQUENCES TO etl;

-- creating second user ( store )

-- Create the user
DO
$$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'store') THEN
      CREATE ROLE store WITH LOGIN PASSWORD 'store';
   END IF;
END
$$;

-- Grant connection and usage on the database
GRANT CONNECT ON DATABASE shoe_storage TO store;

-- Grant privileges on schema public

\connect shoe_storage
GRANT USAGE ON SCHEMA public TO store;

-- Grant privileges on all tables in public schema
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO store;

-- Ensure future tables grant access too
ALTER DEFAULT PRIVILEGES IN SCHEMA public
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO store;

-- Grant usage on sequences (for serial IDs, etc.)
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO store;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
  GRANT USAGE ON SEQUENCES TO store;



CREATE TABLE IF NOT EXISTS shoe_table (
    shoe_id VARCHAR(36) PRIMARY KEY,
    shoe_brand VARCHAR(100),
    shoe_model_name VARCHAR(100) NOT NULL,
    shoe_category VARCHAR(50),
    shoe_price DECIMAL(10, 2) NOT NULL
);

CREATE TABLE IF NOT EXISTS storage_table (
    product_id VARCHAR(13) PRIMARY KEY,
    shoe_id VARCHAR(10) REFERENCES shoe_table(shoe_id),
    product_quantity INTEGER DEFAULT 0
);


-- CREATE TABLE FOR STORAGE: storage_id, marka, size, quantity 
-- quantity INTEGER DEFAULT 0

