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

CREATE TABLE IF NOT EXISTS dim_currency (
  currency_code TEXT PRIMARY KEY,
  description TEXT
);

-- FACT TABLES --------------------------------------------

CREATE TABLE IF NOT EXISTS fact_receipt (
  receipt_id TEXT PRIMARY KEY,
  receipt_barcode TEXT,
  receipt_date DATE,
  vendor_id INT REFERENCES dim_vendor(vendor_id),
  value_sum NUMERIC,
  currency_code TEXT REFERENCES dim_currency(currency_code),
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
  currency_code TEXT REFERENCES dim_currency(currency_code)
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
