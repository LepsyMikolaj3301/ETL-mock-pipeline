-- Create the user
CREATE USER etl WITH PASSWORD 'etl';

-- Grant connection and usage on the database
GRANT CONNECT ON DATABASE mydb TO etl;

-- Grant privileges on schema public

\connect clients
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

CREATE TABLE IF NOT EXISTS clients_table (
    client_id VARCHAR(36) PRIMARY KEY,
    client_first_name VARCHAR(120) NOT NULL,
    client_last_name VARCHAR(120) NOT NULL,
    client_gender TEXT,
    client_email VARCHAR(100) NOT NULL UNIQUE,
    client_date_of_birth DATE,
    client_phone_number VARCHAR(30),
    client_billing_address TEXT,
    client_shipping_address TEXT,
    client_city VARCHAR(100),
    client_postal_code VARCHAR(20),
    client_country VARCHAR(50),
    client_acc_createAt DATE DEFAULT NOW(),
)
