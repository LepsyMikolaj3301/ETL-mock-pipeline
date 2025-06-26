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
GRANT CONNECT ON DATABASE dw TO etl;

-- Grant privileges on schema public

\connect dw
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



-- DIMENSIONS --------------------------------------------

CREATE TABLE IF NOT EXISTS dim_item (
  item_id SERIAL PRIMARY KEY,
  item_name_brand_size TEXT,
  item_barcode TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS dim_vendor (
  vendor_id SERIAL PRIMARY KEY,
  vendor_name TEXT,
  vendor_vat TEXT,
  vendor_eori TEXT,
  vendor_regon TEXT,
  vendor_address TEXT
);

CREATE TABLE IF NOT EXISTS dim_buyer (
  buyer_id SERIAL PRIMARY KEY,
  buyer_name TEXT,
  buyer_vat TEXT,
  buyer_eori TEXT,
  buyer_regon TEXT,
  buyer_address TEXT
);


-- FACT TABLES --------------------------------------------

CREATE TABLE IF NOT EXISTS fact_receipt (
  receipt_id TEXT PRIMARY KEY,
  receipt_barcode TEXT,
  receipt_date DATE,
  vendor_id INT REFERENCES dim_vendor(vendor_id),
  value_sum NUMERIC,
  currency_code TEXT,
  cash_reg_id TEXT
);

CREATE TABLE IF NOT EXISTS fact_receipt_item (
  fact_item_id SERIAL PRIMARY KEY,
  receipt_id TEXT REFERENCES fact_receipt(receipt_id),
  item_id INT REFERENCES dim_item(item_id),
  item_quantity INT,
  price_ind NUMERIC,
  total_value NUMERIC,
  item_vat NUMERIC
);

CREATE TABLE IF NOT EXISTS fact_invoice (
  invoice_id TEXT PRIMARY KEY,
  invoice_date DATE,
  vendor_id INT REFERENCES dim_vendor(vendor_id),
  buyer_id INT REFERENCES dim_buyer(buyer_id),
  value_sum_net NUMERIC,
  value_sum_gross NUMERIC,
  addit_notes TEXT,
  currency TEXT
);

CREATE TABLE IF NOT EXISTS fact_invoice_item (
  fact_item_id SERIAL PRIMARY KEY,
  invoice_id TEXT REFERENCES fact_invoice(invoice_id),
  item_id INT REFERENCES dim_item(item_id),
  item_meta_quantity TEXT,
  item_quantity INT,
  price_ind_net NUMERIC,
  value_net NUMERIC,
  price_ind_gross NUMERIC,
  value_gross NUMERIC,
  item_vat TEXT
);
