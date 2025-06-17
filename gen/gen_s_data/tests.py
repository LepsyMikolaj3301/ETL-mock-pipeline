import structured_data_gen as stdg
from factories import ItemQuant, Transaction, Vendor
from factories import Shoe, ShoeTableFactory
from factories import ReceiptMeta, ReceiptFactory, InvoiceMeta, InvoiceFactory
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import csv

def test_receipt_invoices():
    vendor_1 = Vendor(
        vendor_name="Acme Corp",
        vendor_vat="123-456-7890",
        vendor_eori="EORI123456",
        vendor_regon="REGON987654",
        street="Main St",
        num_of_addr="123",
        city="Springfield",
        postal_code="00-123",
        country="USA",
        email="contact@acmecorp.com"
    )
    items_list = [
        ItemQuant(
            item_name="Widget",
            item_size=10,
            item_brand="BrandA",
            item_barcode="1234567890123",
            quantity=5,
            price_ind=19.99,
            currency="USD"
        ),
        ItemQuant(
            item_name="Gadget",
            item_size=5,
            item_brand="BrandB",
            item_barcode="9876543210987",
            quantity=2,
            price_ind=29.99,
            currency="USD"
        )
    ]
    trans_1 = Transaction(
        items_list=items_list,
        transaction_type="cash",
        transaction_money="BANK123456789"
    )
    
    test_recept = [InvoiceFactory(vendor=vendor_1, transaction=trans_1) for _ in range(5)]
    print(test_recept[4])

def create_shoe_table_csv(shoe_db_conn_info, instances_count):
    host_port_shoe_db = ':'.join([shoe_db_conn_info['host'], str(shoe_db_conn_info['port'])])

    engine_connection = 'postgresql://{}:{}@{}/{}'.format(shoe_db_conn_info['user'],
                                                              shoe_db_conn_info['pass'],
                                                              host_port_shoe_db,
                                                              shoe_db_conn_info['name'])
        
    try:
        engine = create_engine(engine_connection)
        print(f'ENGINE _ SUCCESSFULLY TO: {engine_connection}')
    except Exception as e:
        print(f'CONNECTION UN_SUCCESSFUL - {e}')
        return None
    
    
    # Check if the Shoe table exists in the database
    if not engine.dialect.has_table(engine.connect(), Shoe.__tablename__):
        print(f"Table '{Shoe.__tablename__}' does not exist!")
        Shoe.__table__.create(engine)
    else:
        print(f"Table '{Shoe.__tablename__}' already exists.")
    
    Session = sessionmaker(bind=engine)
    
    # Inserting Data to table
    CURRENCY = 'EUR'
    ShoeTableFactory._meta.sqlalchemy_session = Session() #type: ignore
    shoes_inserted = [ShoeTableFactory.create(currency=CURRENCY) for _ in range(instances_count)]
    
    csv_filename = 'init_data/shoes_table.csv'
    fieldnames = ['shoe_id', 'shoe_brand', 'shoe_model_name', 'shoe_category', 'shoe_price', 'currency']

    with open(csv_filename, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for shoe in shoes_inserted:
            writer.writerow({
                'shoe_id': shoe.shoe_id,
                'shoe_brand': shoe.shoe_brand,
                'shoe_model_name': shoe.shoe_model_name,
                'shoe_category': shoe.shoe_category,
                'shoe_price': shoe.shoe_price,
                'currency': shoe.currency
            })
    print(f"CSV file '{csv_filename}' created with {len(shoes_inserted)} shoes.")

def test_choose_products():
    
    shoe_db_conn = {
    "name" : 'shoe_storage',
    "user" : 'store',
    "pass" : 'store',
    "host" : 'localhost',
    "port" : 5433
    }
    
    
    # SHOE_DB_NAME = 'shoe_storage'
    # SHOE_DB_USER =  'store'
    # SHOE_DB_PASS = 'store'
    # SHOE_DB_HOST = 'shoe_storage_db'
    # SHOE_DB_PORT = 5433

    # shoe_shop_sim = stdg.ShoeShopSimulation(shoe_db_conn)
    
    # print(shoe_shop_sim._choose_products(3))
    
    create_shoe_table_csv(shoe_db_conn, instances_count=130)

    


if __name__ == '__main__':
    test_choose_products()
    