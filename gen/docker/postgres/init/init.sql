-- CREATE TABLESPACE shoe_tablespace LOCATION '/mnt/tablespace';
\connect shoe_storage
CREATE TABLE IF NOT EXISTS brand_table (
    shoe_id VARCHAR(10) PRIMARY KEY,
    brand VARCHAR(100),
    model_name VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    price DECIMAL(10, 2)
);

CREATE TABLE IF NOT EXISTS storage_table (
    product_id VARCHAR(10) PRIMARY KEY,
    shoe_id VARCHAR(10) REFERENCES brand_table(shoe_id),
    quantity INTEGER DEFAULT 0
);

-- CREATE TABLE FOR STORAGE: storage_id, marka, size, quantity 
-- quantity INTEGER DEFAULT 0

