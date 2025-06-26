
# Do zmiany
def insert_to_postgres_spark(
    dim_item_df, dim_vendor_df, dim_buyer_df,
    fact_receipt_df, fact_receipt_item_df,
    fact_invoice_df, fact_invoice_item_df,
    pg_conn_params
):
    url = f"jdbc:postgresql://{pg_conn_params['host']}:{pg_conn_params['port']}/{pg_conn_params['dbname']}"
    properties = {
        "user": pg_conn_params["user"],
        "password": pg_conn_params["password"],
        "driver": "org.postgresql.Driver"
    }

    # Write dimension tables
    dim_item_df.select("item_name_brand_size", "item_barcode") \
        .distinct() \
        .write \
        .jdbc(url, "dim_item", mode="append", properties=properties)

    dim_vendor_df.select("vendor_name", "vendor_vat", "vendor_eori", "vendor_regon", "vendor_address") \
        .distinct() \
        .write \
        .jdbc(url, "dim_vendor", mode="append", properties=properties)

    dim_buyer_df.select("buyer_name", "buyer_vat", "buyer_eori", "buyer_regon", "buyer_address") \
        .distinct() \
        .write \
        .jdbc(url, "dim_buyer", mode="append", properties=properties)

    # Write fact tables
    fact_receipt_df.select(
        "receipt_id", "receipt_barcode", "receipt_date", "vendor_id",
        "value_sum", "currency_code", "cash_reg_id"
    ).write \
        .jdbc(url, "fact_receipt", mode="append", properties=properties)

    fact_receipt_item_df.select(
        "receipt_id", "item_id", "item_quantity",
        "price_ind", "total_value", "item_vat"
    ).write \
        .jdbc(url, "fact_receipt_item", mode="append", properties=properties)

    fact_invoice_df.select(
        "invoice_id", "invoice_date", "vendor_id", "buyer_id",
        "value_sum_net", "value_sum_gross", "addit_notes", "currency"
    ).write \
        .jdbc(url, "fact_invoice", mode="append", properties=properties)

    fact_invoice_item_df.select(
        "invoice_id", "item_id", "item_meta_quantity", "item_quantity",
        "price_ind_net", "value_net", "price_ind_gross", "value_gross", "item_vat"
    ).write \
        .jdbc(url, "fact_invoice_item", mode="append", properties=properties)
