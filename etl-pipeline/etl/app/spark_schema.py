from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType, ArrayType

RECEIPT_ITEM_SCHEMA = StructType([
    StructField("item_name_brand_size", StringType(), True),
    StructField("item_barcode", StringType(), True),
    StructField("item_quantity", IntegerType(), True),
    StructField("price_ind", DoubleType(), True),
    StructField("total_value", DoubleType(), True),
    StructField("item_vat", DoubleType(), True),
    StructField("currency", StringType(), True),
])

RECEIPT_SCHEMA = StructType([
    StructField("receipt_id", StringType(), True),
    StructField("receipt_barcode", StringType(), True),
    StructField("receipt_date", StringType(), True),
    StructField("vendor_vat", StringType(), True),
    StructField("vendor_name", StringType(), True),
    StructField("vendor_address", StringType(), True),
    StructField("items", ArrayType(RECEIPT_ITEM_SCHEMA), True),
    StructField("value_sum", DoubleType(), True),
    StructField("currency", StringType(), True),
    StructField("cash_reg_id", StringType(), True)
])

INVOICE_ITEM_SCHEMA = StructType([
    StructField("item_name_brand_size", StringType(), True),
    StructField("item_barcode", StringType(), True),
    StructField("item_meta_quantity", StringType(), True),
    StructField("item_quantity", IntegerType(), True),
    StructField("price_ind_net", DoubleType(), True),
    StructField("value_net", DoubleType(), True),
    StructField("price_ind_gross", DoubleType(), True),
    StructField("value_gross", DoubleType(), True),
    StructField("item_vat", StringType(), True),
    StructField("currency", StringType(), True),
])

INVOICE_BUYER_SCHEMA = StructType([
    StructField("buyer_name", StringType(), True),
    StructField("buyer_vat", StringType(), True),
    StructField("buyer_eori", StringType(), True),
    StructField("buyer_regon", StringType(), True),
    StructField("address", StringType(), True),
])

INVOICE_SCHEMA = StructType([
    StructField("invoice_id", StringType(), True),
    StructField("invoice_date", StringType(), True),
    StructField("vendor_name", StringType(), True),
    StructField("vendor_vat", StringType(), True),
    StructField("vendor_eori", StringType(), True),
    StructField("vendor_regon", StringType(), True),
    StructField("vendor_address", StringType(), True),
    StructField("buyer", INVOICE_BUYER_SCHEMA, True),
    StructField("items", ArrayType(INVOICE_ITEM_SCHEMA), True),
    StructField("value_sum_net", DoubleType(), True),
    StructField("value_sum_gross", DoubleType(), True),
    StructField("addit_notes", StringType(), True),
    StructField("currency", StringType(), True),
])