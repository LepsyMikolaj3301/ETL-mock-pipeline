import spark_schema as spschm
import json
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode
import xml.etree.ElementTree as ET
import pydifact
import os
import glob
import logging

# CREATING LOGGER
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)



class UniversalReceiptParser:
    def __init__(self, spark: SparkSession):
        self.spark = spark
        self.schema = spschm.RECEIPT_SCHEMA
        self.df = None

    def parse_json(self, paths):
        if isinstance(paths, str):
            paths = [paths]
        df_new = self.spark.read.schema(self.schema).json(paths)
        if self.df is None:
            self.df = df_new
        else:
            self.df = self.df.unionByName(df_new)
        return self.df

    def parse_xml(self, paths, root_tag: str = "Receipt"):
        if isinstance(paths, str):
            paths = [paths]
        df_new = self.spark.read \
            .format("xml") \
            .option("rowTag", root_tag) \
            .schema(self.schema) \
            .load(paths)
        if self.df is None:
            self.df = df_new
        else:
            self.df = self.df.unionByName(df_new)
        return self.df

    def auto_detect_format(self, path: str) -> str:
        ext = os.path.splitext(path)[1].lower()
        if ext in [".json"]:
            return "json"
        elif ext in [".xml"]:
            return "xml"
        else:
            raise ValueError(f"Cannot detect format for file: {path}")

    def parse(self, paths):
        if isinstance(paths, str):
            paths = [paths]
        if not paths:
            raise ValueError("No input files provided.")
        fmt = self.auto_detect_format(paths[0])
        if not all(self.auto_detect_format(p) == fmt for p in paths):
            raise ValueError("All files must have the same format.")
        if fmt == "json":
            return self.parse_json(paths)
        elif fmt == "xml":
            return self.parse_xml(paths)
        else:
            raise ValueError(f"Unsupported format: {fmt}")
        
    def get_df(self):
        return self.df
        

class UniversalInvoiceParser:
    def __init__(self, spark: SparkSession):
        self.spark = spark
        self.schema = spschm.INVOICE_SCHEMA
        self.df = None

    def get_df(self):
        return self.df
    
    def auto_detect_format(self, path: str) -> str:
        ext = os.path.splitext(path)[1].lower()
        if ext in [".json"]:
            return "json"
        elif ext in [".xml"]:
            return "xml"
        elif ext in [".edi", ".edifact", ".txt"]:
            return "edifact"
        else:
            raise ValueError(f"Cannot detect format for file: {path}")

    def parse(self, paths):
        if isinstance(paths, str):
            paths = [paths]
        for path in paths:
            fmt = self.auto_detect_format(path)
            if fmt == "xml":
                df_new = self.parse_xml(path)
                if self.df is None:
                    self.df = df_new
                else:
                    self.df = self.df.unionByName(df_new)
            elif fmt == "edifact":
                df_new = self.parse_edifact(path)
                if self.df is None:
                    self.df = df_new
                else:
                    self.df = self.df.unionByName(df_new)
            else:
                raise ValueError(f"Unsupported format: {fmt}")
        # Optionally, you can return both or one depending on your use case
        return self.df

    def parse_xml(self, path: str, root_tag: str = "Invoice"):
        return self.spark.read \
            .format("xml") \
            .option("rowTag", root_tag) \
            .schema(self.schema) \
            .load(path)

    def parse_edifact(self, path: str):
        # Parse EDIFACT INVOIC messages using pydifact and map to INVOICE_SCHEMA
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        segments = list(pydifact.parser.Parser().parse(content))
        invoices = []

        invoice = {
            "invoice_id": None,
            "invoice_date": None,
            "vendor_name": None,
            "vendor_vat": None,
            "vendor_eori": None,
            "vendor_regon": None,
            "vendor_address": None,
            "buyer": {
            "buyer_name": None,
            "buyer_vat": None,
            "buyer_eori": None,
            "buyer_regon": None,
            "address": None,
            },
            "items": [],
            "value_sum_net": None,
            "value_sum_gross": None,
            "addit_notes": None,
            "currency": None,
        }
        current_item = {}
        for segment in segments:
            tag = segment.tag
            elements = segment.elements

            if tag == "BGM":
                invoice["invoice_id"] = elements[1] if len(elements) > 1 else None
            elif tag == "DTM" and elements and elements[0] == "137":
                invoice["invoice_date"] = elements[1][:8] if len(elements) > 1 else None #type: ignore
            elif tag == "NAD":
                if elements[0] == "SU":
                    invoice["vendor_name"] = elements[1] if len(elements) > 1 else None
                    invoice["vendor_vat"] = elements[2] if len(elements) > 2 else None
                    invoice["vendor_address"] = elements[4] if len(elements) > 4 else None
                elif elements[0] == "BY":
                    invoice["buyer"]["buyer_name"] = elements[1] if len(elements) > 1 else None
                    invoice["buyer"]["buyer_vat"] = elements[2] if len(elements) > 2 else None
                    invoice["buyer"]["address"] = elements[4] if len(elements) > 4 else None
            elif tag == "LIN":
                if current_item:
                    invoice["items"].append(current_item)
                current_item = {
                    "item_name_brand_size": None,
                    "item_barcode": elements[2] if len(elements) > 2 else None,
                    "item_meta_quantity": None,
                    "item_quantity": None,
                    "price_ind_net": None,
                    "value_net": None,
                    "price_ind_gross": None,
                    "value_gross": None,
                    "item_vat": None,
                    "currency": None,
                }
            elif tag == "IMD" and current_item:
                if len(elements) > 3:
                    current_item["item_name_brand_size"] = elements[3]
            elif tag == "QTY" and current_item:
                if elements[0] == "47":
                    try:
                        current_item["item_quantity"] = int(elements[1]) #type: ignore
                    except Exception:
                        current_item["item_quantity"] = None
            elif tag == "PRI" and current_item:
                if elements[0] == "AAA":
                    try:
                        current_item["price_ind_net"] = float(elements[1]) #type: ignore
                    except Exception:
                        current_item["price_ind_net"] = None
                elif elements[0] == "AAB":
                    try:
                        current_item["price_ind_gross"] = float(elements[1]) #type: ignore
                    except Exception:
                        current_item["price_ind_gross"] = None
            elif tag == "MOA":
                if elements[0] == "77":
                    try:
                        invoice["value_sum_net"] = float(elements[1]) #type: ignore
                    except Exception:
                        invoice["value_sum_net"] = None
                elif elements[0] == "79":
                    try:
                        invoice["value_sum_gross"] = float(elements[1]) #type: ignore
                    except Exception:
                        invoice["value_sum_gross"] = None
                elif elements[0] == "203" and current_item:
                    try:
                        current_item["value_net"] = float(elements[1]) #type: ignore
                    except Exception:
                        current_item["value_net"] = None
                elif elements[0] == "124" and current_item:
                    try:
                        current_item["value_gross"] = float(elements[1]) #type: ignore
                    except Exception:
                        current_item["value_gross"] = None
            elif tag == "TAX" and current_item:
                if len(elements) > 2:
                    current_item["item_vat"] = elements[2]
            elif tag == "CUX":
                if len(elements) > 1:
                    invoice["currency"] = elements[1]
                    if current_item:
                        current_item["currency"] = elements[1]
            elif tag == "FTX":
                if not invoice["addit_notes"]:
                    invoice["addit_notes"] = elements[-1] if elements else None

        if current_item:
            invoice["items"].append(current_item)
        invoices.append(invoice)

        return self.spark.createDataFrame(invoices, schema=self.schema)

def transform():
    spark = SparkSession.builder.getOrCreate()
    receipt_parser = UniversalReceiptParser(spark)
    invoice_parser = UniversalInvoiceParser(spark)

    input_files = glob.glob("data/input/*")
    formats = set()
    for file_path in input_files:
        ext = os.path.splitext(file_path)[1].lower()
        if ext in [".json"]:
            formats.add("json")
        elif ext in [".xml"]:
            formats.add("xml")
        elif ext in [".edi", ".edifact", ".txt"]:
            formats.add("edi")
        else:
            formats.add("unknown")
    logger.info(f"Detected formats in data/input: {formats}")
    
    # FOR INVOICES
    for form in formats:
        input_files_invoice = glob.glob(f"data/input/invoice*.{form}")
        if input_files_invoice:
            invoice_parser.parse(input_files_invoice)
            logger.info(f"Parsed invoice files num: {len(input_files_invoice)}")

    # FOR RECEIPTS
    for form in formats:
        input_files_receipt = glob.glob(f"data/input/receipt*.{form}")
        if input_files_receipt:
            invoice_parser.parse(input_files_receipt)
            logger.info(f"Parsed receipt files num: {len(input_files_receipt)}")
    
    
    
    df_invoice = invoice_parser.get_df() 
    df_receipt = receipt_parser.get_df()
    
    
    # DIMENSION TABLES

    # dim_item
    df_item = (
        df_invoice.selectExpr("explode(items) as item")
        .select(
            col("item.item_name_brand_size").alias("item_name_brand_size"),
            col("item.item_barcode").alias("item_barcode"),
        )
        .unionByName(
            df_receipt.selectExpr("explode(items) as item")
            .select(
                col("item.item_name_brand_size").alias("item_name_brand_size"),
                col("item.item_barcode").alias("item_barcode"),
            )
        )
        .dropDuplicates(["item_barcode"])
    )

    # dim_vendor
    df_vendor = (
        df_invoice.select(
            col("vendor_name"),
            col("vendor_vat"),
            col("vendor_eori"),
            col("vendor_regon"),
            col("vendor_address"),
        )
        .unionByName(
            df_receipt.select(
                col("vendor_name"),
                col("vendor_vat"),
                col("vendor_address"),
            ).withColumn("vendor_eori", col("vendor_vat") * 0)  # dummy nulls
             .withColumn("vendor_regon", col("vendor_vat") * 0)
        )
        .dropDuplicates(["vendor_vat", "vendor_name"])
    )

    # dim_buyer
    df_buyer = (
        df_invoice.select(
            col("buyer.buyer_name").alias("buyer_name"),
            col("buyer.buyer_vat").alias("buyer_vat"),
            col("buyer.buyer_eori").alias("buyer_eori"),
            col("buyer.buyer_regon").alias("buyer_regon"),
            col("buyer.address").alias("buyer_address"),
        )
        .dropDuplicates(["buyer_vat", "buyer_name"])
    )



    # FACT TABLES

    # fact_receipt
    df_fact_receipt = (
        df_receipt
        .join(df_vendor, ["vendor_name", "vendor_vat", "vendor_address"], "left")
        .select(
            col("receipt_id"),
            col("receipt_barcode"),
            col("receipt_date"),
            col("vendor_id"),
            col("value_sum"),
            col("currency"),
            col("cash_reg_id"),
        )
    )

    # fact_receipt_item
    df_receipt_items = (
        df_receipt
        .select(
            col("receipt_id"),
            explode(col("items")).alias("item")
        )
        .join(df_item, col("item.item_barcode") == df_item.item_barcode, "left")
        .select(
            col("receipt_id"),
            col("item_id"),
            col("item.item_quantity").alias("item_quantity"),
            col("item.price_ind").alias("price_ind"),
            col("item.total_value").alias("total_value"),
            col("item.item_vat").alias("item_vat"),
        )
    )

    # fact_invoice
    df_fact_invoice = (
        df_invoice
        .join(df_vendor, ["vendor_name", "vendor_vat", "vendor_address"], "left")
        .join(df_buyer, [df_invoice.buyer.buyer_name == df_buyer.buyer_name,
                         df_invoice.buyer.buyer_vat == df_buyer.buyer_vat], "left")
        .select(
            col("invoice_id"),
            col("invoice_date"),
            col("vendor_id"),
            col("buyer_id"),
            col("value_sum_net"),
            col("value_sum_gross"),
            col("addit_notes"),
            col("currency"),
        )
    )

    # fact_invoice_item
    df_invoice_items = (
        df_invoice
        .select(
            col("invoice_id"),
            explode(col("items")).alias("item")
        )
        .join(df_item, col("item.item_barcode") == df_item.item_barcode, "left")
        .select(
            col("invoice_id"),
            col("item_id"),
            col("item.item_meta_quantity").alias("item_meta_quantity"),
            col("item.item_quantity").alias("item_quantity"),
            col("item.price_ind_net").alias("price_ind_net"),
            col("item.value_net").alias("value_net"),
            col("item.price_ind_gross").alias("price_ind_gross"),
            col("item.value_gross").alias("value_gross"),
            col("item.item_vat").alias("item_vat"),
        )
    )
    
    
    
    
    
    return {"dimensions": [df_buyer, df_vendor, df_item],
            "invoice": [df_fact_invoice, df_invoice_items],
            "receipt": [df_fact_receipt, df_receipt_items]}
