
# Do zmiany
def insert_to_postgres_spark(
    dim_item_df, dim_vendor_df, dim_currency_df, fact_receipt_df, fact_receipt_item_df,
    pg_conn_params
):
    url = f"jdbc:postgresql://{pg_conn_params['host']}:{pg_conn_params['port']}/{pg_conn_params['dbname']}"
    properties = {
        "user": pg_conn_params["user"],
        "password": pg_conn_params["password"],
        "driver": "org.postgresql.Driver"
    }

    # Write dim tables
    dim_item_df.select("item_name_brand_size", "item_barcode") \
        .distinct() \
        .write \
        .jdbc(url, "dim_item", mode="append", properties=properties)

    dim_vendor_df.select("vendor_name", "vendor_vat", "vendor_eori", "vendor_regon", "vendor_address") \
        .distinct() \
        .write \
        .jdbc(url, "dim_vendor", mode="append", properties=properties)

    dim_currency_df.select("currency_code", "description") \
        .distinct() \
        .write \
        .jdbc(url, "dim_currency", mode="append", properties=properties)

    # Write fact tables
    fact_receipt_df.select(
        "receipt_id", "receipt_barcode", "receipt_date", "value_sum",
        fact_receipt_df["currency"].alias("currency_code"),
        "cash_reg_id", "vendor_vat"
    ).write \
        .jdbc(url, "fact_receipt", mode="append", properties=properties)

    fact_receipt_item_df.select(
        "receipt_id", "item_name_brand_size", "item_barcode", "item_quantity",
        "price_ind", "total_value", "item_vat"
    ).write \
        .jdbc(url, "fact_receipt_item", mode="append", properties=properties)
