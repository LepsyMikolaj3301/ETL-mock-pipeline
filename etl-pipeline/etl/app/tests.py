import transform
from pathlib import Path
from pyspark.sql import SparkSession



def test_parsing():
    
    paths = ['data/input/receipt_2025_06_23__12_20_07.xml', 
             'data/input/receipt_2025_06_23__12_20_07.json']
    
    spark = SparkSession.builder \
    .appName("NormalizeReceipts") \
    .master("spark://localhost:7077") \
    .getOrCreate() 
    
    receipt_parser = transform.UniversalReceiptParser(spark)
    receipt_parser.parse(paths)
    df_receipt = receipt_parser.get_df()
    
    if df_receipt:
        df_receipt.printSchema()
        df_receipt.show()
    
    
    
    
    
if __name__ == "__main__":
    test_parsing()


