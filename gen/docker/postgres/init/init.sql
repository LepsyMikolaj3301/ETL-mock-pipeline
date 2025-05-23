-- CREATE TABLESPACE shoe_tablespace LOCATION '/mnt/tablespace';
CREATE TABLE IF NOT EXISTS shoes_table (
    shoe_id VARCHAR(10) PRIMARY KEY,
    brand VARCHAR(100),
    model_name VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    price DECIMAL(10, 2),
    
) TABLESPACE shoe_tablespace;

-- CREATE TABLE FOR STORAGE: storage_id, marka, size, quantity 
-- quantity INTEGER DEFAULT 0

