"""
Code for generating synthetic data using SDV (Synthetic Data Vault)
What kind of ERT data will be generated:
Jakie dane będą generowane:

SKLEP STACJONARNY

- Paragony i faktury | Sprzedaż detaliczna | EDI, JSON, CSV, XML - RANDOM
- Zwroty i reklamacje | Powód zwrotu, data, ID produktu, oryginalna sprzedaż | CSV, JSON - RANDOM

- Raporty dzienne | Przychody, forma płatności, saldo kasowe | CSV 
- Koszty | Zakupy towarów, wynajem, pensje | XML - RANDOM

- Grafik zmian pracowników | Harmonogramy zmian, wejścia/wyjścia | CSV, XML - NA STALE
- Lista Pracowników | Lista zatrudnionych pracowników w tym sklepie, dane personalne | Baza danych - NA STALE

MAGAZYN

- Stan magazynowy | Ilość dostępnych sztuk każdego modelu i rozmiaru | baza danych - ZALEŻNE
- Ruchy magazynowe | Przyjęcia, wydania, przemieszczenia między sklepem a Bazą | JSON, CSV
- Zamówienia do dostawców | Dostawy z hurtowni | XML, EDI, JSON


TODO: Tworzenie faktur/paragonów (info od Bazy)
"""
import random
import pandas as pd
import time
from sqlalchemy import create_engine, update
from sqlalchemy.orm import sessionmaker
import logging, datetime
from factories import Shoe, Client, Storage, init_storage_vals
from factories import ShoeTableFactory, ClientTableFactory, StorageTableFactory
# Receipt and Invoice generation
from factories import ItemQuant, Transaction, TransactionFactory, Vendor
from factories import ReceiptMeta, ReceiptFactory, InvoiceMeta, InvoiceFactory
from factories import fake
import os
from sqlalchemy.sql.expression import func


# FILE CREATION
import xml.etree.ElementTree as ET
import json
import pathlib

# CREATING LOGGER
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# GLOBALNE ZMIENNE - DO ZMIANY
CURRENCY = 'EUR'


   
def init_shoe_DB(shoe_db_conn_info: dict[str, str]):
    """This function inserts SYNTHETIC data into the Shoe Table

    Args:
        shoe_db_conn_info (dict[str]): info to connect to the ShoeDB
        instances_count (int): the count of instances to insert

    """
    
    
    host_port_shoe_db = ':'.join([shoe_db_conn_info['host'], shoe_db_conn_info['port']])

    engine_connection = 'postgresql://{}:{}@{}/{}'.format(shoe_db_conn_info['user'],
                                                              shoe_db_conn_info['pass'],
                                                              host_port_shoe_db,
                                                              shoe_db_conn_info['name'])
        
    try:
        engine = create_engine(engine_connection)
        logger.info(f'ENGINE _ SUCCESSFULLY TO: {engine_connection}')
    except Exception as e:
        logger.error(f'CONNECTION UN_SUCCESSFUL - {e}')
        return None
    
    
    # Check if the Shoe table exists in the database
    if not engine.dialect.has_table(engine.connect(), Shoe.__tablename__):
        logger.info(f"Table '{Shoe.__tablename__}' does not exist!")
        Shoe.__table__.create(engine)
    else:
        logger.info(f"Table '{Shoe.__tablename__}' already exists.")
    
    Session = sessionmaker(bind=engine)
    
    def init_shoe(session):
        try:
            with session:
                # Inserting Data to table
                shoes_df = pd.read_csv("init_data/shoes_table.csv")
                shoes_inserted = []
                for _, row in shoes_df.iterrows():
                    shoe = Shoe(
                        shoe_id=row["shoe_id"],
                        shoe_model_name=row["shoe_model_name"],
                        shoe_brand=row["shoe_brand"],
                        shoe_price=row["shoe_price"],
                        shoe_category=row["shoe_category"],
                        currency=row.get("currency", CURRENCY)
                    )
                    shoes_inserted.append(shoe)
                # ShoeTableFactory.create_batch(size=instances_count, currency=CURRENCY)
                session.add_all(shoes_inserted)
                session.commit()
                logger.info(f"Inserted {len(shoes_inserted)} shoes into shoe_table.")
        except Exception as e:
            logger.error(f"ORM insert error: {e}")

    def init_storage(session, shoe_ids):
        try:
            with session:
                StorageTableFactory._meta.sqlalchemy_session = session #type: ignore
                products = []
                for si in shoe_ids:
                    for shoe_size in range(36, 47):
                        storage_item = StorageTableFactory.create(shoe_id=si[0], shoe_size=shoe_size)
                        products.append(storage_item)
                session.add_all(products)
                session.commit()
                logger.info(f"Inserted {len(products)} storage items into storage_table.")
        except Exception as e:
            logger.error(f"ORM insert error: {e}")
    # INIT SHOE TABLE
    # Insert Data to Table SHOE
    with Session() as session:
        existing_count = session.query(Shoe).count()
    if existing_count == 0:
        init_shoe(Session())
    else: 
        logger.info(f"Shoe table already contains {existing_count} records. Skipping data insertion.")
    
    with Session() as session:
        existing_count = session.query(Storage).count()
        shoe_ids = session.query(Shoe.shoe_id).all()
    
    if existing_count == 0:
        init_storage(Session(), shoe_ids)
    else: 
        logger.info(f"Storage table already contains {existing_count} records. Skipping data insertion.")
    

    
    
def init_client_db(client_db_conn_info: dict[str, str], instances_count: int):
    host_port_client_db = ':'.join([client_db_conn_info['host'], client_db_conn_info['port']])

    engine_connection = 'postgresql://{}:{}@{}/{}'.format(client_db_conn_info['user'],
                                                                        client_db_conn_info['pass'],
                                                                        host_port_client_db,
                                                                        client_db_conn_info['name'])
    
    try:
        engine = create_engine(engine_connection)
        logger.info(f'CONNECTED SUCCESSFULLY TO: {engine_connection}')
    except Exception as e:
        logger.error(f'CONNECTION UN_SUCCESSFUL - {e}')
        return None
    
    # Check if the Shoe table exists in the database
    if not engine.dialect.has_table(engine.connect(), Client.__tablename__):
        logger.info(f"Table '{Client.__tablename__}' does not exist!")
        Client.__table__.create(engine)
    else:
        logger.info(f"Table '{Client.__tablename__}' already exists.")

    Session = sessionmaker(bind=engine)
    
    # INIT CLIENT DB
    with Session() as session:
        # Inserting Data to table
        client_inserted = ClientTableFactory.create_batch(size=instances_count, sqlalchemy_session=session)
        logger.info(f"Inserted {len(client_inserted)} clients into {Client.__tablename__}.")
        session.commit()
    

# SHOE SHOP SIMULATOR (WITH DATABASE CONNECTION ORM)
class ShoeShopSimulation:
    """
    SHOE SHOP SIMULATION
    IT CREATES VARIOUS OBJECTS FOR DATA GENERATION IN INTERVALS (CRON)
    """    
    
    def __init__(self, shoe_db_conn_info, vendor_info: dict, formats: list[str], client_db_conn_info=None) -> None:
        host_port_shoe_db = ':'.join([shoe_db_conn_info['host'], str(shoe_db_conn_info['port'])])
        
        engine_connection_shoe_db = 'postgresql://{}:{}@{}/{}'.format(shoe_db_conn_info['user'],
                                                              shoe_db_conn_info['pass'],
                                                              host_port_shoe_db,
                                                              shoe_db_conn_info['name'])
        
        
        self.engine_shoe_db = create_engine(engine_connection_shoe_db)
        
        self.SessionShoe = sessionmaker(bind=self.engine_shoe_db)
        with self.engine_shoe_db.connect() as conn:
            self.shoe_table = pd.read_sql_table('shoe_table', conn) 

        
        if client_db_conn_info:
            host_port_client_db = ':'.join([client_db_conn_info['host'], client_db_conn_info['port']])
            engine_connection_client_db = 'postgresql://{}:{}@{}/{}'.format(client_db_conn_info['user'],
                                                                        client_db_conn_info['pass'],
                                                                        host_port_client_db,
                                                                        client_db_conn_info['name'])
            self.engine_client_db = create_engine(engine_connection_client_db)
            with self.engine_client_db.connect() as conn:
                self.client_table = pd.read_sql_table('clients_table', conn)
        
        # Create VENDOR
        self.vendor = Vendor(**vendor_info)
        
        # Counter for import
        self.import_timer = 0
        
        # DIRECTORY for storage
        self.DATA_DIRECTORY = "data"
        self.RECEIPT_DIRECTORY = self.DATA_DIRECTORY + "/receipts"
        self.INVOICE_DIRECTORY = self.DATA_DIRECTORY + "/invoices"
        
        # AVAILABLE FORMATS TO USE:
        self.formats = formats
        # Create amount of time to wait to restock STORAGE
        logger.info(f"Current working directory: {os.getcwd()}")
    # ORAZ W AFEKCIE GENERACJA ZAMÓWIEŃ ORAZ PRZYSYŁEK
    
    def simulate(self, sim_duration):
        for _ in range(sim_duration):
            self._simulate_buying()
            time.sleep(5)
            # after creation, check magazine levels
            self._update_storage()
            time.sleep(5)
            
    
    def _simulate_buying(self):
        # Generate new client info
        trans = self._create_transaction()
        # Pass it down to the create receipt OR invoice
        # PROBABILITY 3 to 1
        if random.random() < 0.75:
            self._create_receipt(transaction=trans, file_format=self.formats)
        else:
            self._create_invoice(transaction=trans, file_format=self.formats)
        

    def _update_storage(self):
        with self.SessionShoe() as session:
            low_stock_items = session.query(Storage).filter(Storage.product_quantity < 4).all()
            logger.info(f"Found {len(low_stock_items)} storage items with quantity < 4.")
            # self.__create_import_order()
            if low_stock_items:
                self.import_timer = int(random.normalvariate(30, 10))
                
                
                # PRzez brak czasu - od razu UPDATE
                for item in low_stock_items:
                    session.query(Storage).filter(Storage.product_id == item.product_id).update(
                        {Storage.product_quantity: Storage.product_quantity + 15}
                    )
                session.commit()
                logger.info("Restocked low stock items by +15 units each.")
            
            
    # DO DODANIA  
    def __create_import_order(self, items: list[Storage]):
        pass        
    
    def _choose_products(self, num: int) -> list[ItemQuant]:
        with self.SessionShoe() as session:

            products_bought = []
            # Join Storage and Shoe tables on shoe_id, randomize order, and get first 'num' results
            query = (
                session.query(Storage, Shoe)
                .join(Shoe, Storage.shoe_id == Shoe.shoe_id)
                .filter(Storage.product_quantity > 0)
                .order_by(func.random())
                .limit(num)
            )

            results = query.all()
            # print(f'results: {results}')
            # print(f'show: {results[0]}')# Display the first 'num' randomized joined values
            # ADD LOGGER
            
            for prod, shoe in results:
                prod_bought_quant = max(1, int(random.expovariate(1/3)))
                # prod_shoe = self.shoe_table[self.shoe_table['shoe_id'] == prod.shoe_id]
                # if not prod_shoe: continue
                products_bought.append(ItemQuant(shoe.shoe_model_name,
                                                 prod.shoe_size,
                                                 shoe.shoe_brand,
                                                 prod.product_id,
                                                 prod_bought_quant,
                                                 shoe.shoe_price,
                                                 shoe.currency
                                                ))
            
                # ZMNIEJSZ LICZBE QUANTITY ABY ZASYMULOWAĆ SPRZEDARZ
                stmt = (
                    update(Storage).
                    where(Storage.product_id == prod.product_id).
                    values(product_quantity = Storage.product_quantity - prod_bought_quant)
                )    
                session.execute(stmt)
                session.commit()
            return products_bought

    def _create_transaction(self) -> Transaction:
        
        # Losuj ilość z rozkładu wykładniczego (np. średnia 2, zaokrąglona do min. 1)
        quantity_diff_prod = max(1, int(random.expovariate(1/2)))
        
        # Create Bought Items
        bought_items: list[ItemQuant] = self._choose_products(quantity_diff_prod)
        
        # Create Transition
        logger.info(f"TRANSACTION MADE AT {datetime.datetime.now()}")
        return TransactionFactory(items_list_param=bought_items)       
    
    def _create_receipt(self, transaction: Transaction, file_format: list[str]):
        
        # Create a receipt 
        receipt_meta_obj: ReceiptMeta = ReceiptFactory(vendor=self.vendor, transaction=transaction)

        for ff in file_format:
            if ff == 'xml':
                self.__xml_receipt(receipt_meta_obj)
            if ff == 'json':
                self.__json_receipt(receipt_meta_obj)
        
    
    def __xml_receipt(self, receipt: ReceiptMeta) :
        

        # Each item in receipt.items is an ItemReceipt with the following fields:
        # item_name_brand_size, item_barcode, item_quantity, price_ind, total_value, item_vat, currency


        root = ET.Element("Receipt")

        def safe_set(parent, tag, value):
            ET.SubElement(parent, tag).text = str(value) if value is not None else ""

        safe_set(root, "ReceiptID", getattr(receipt, "receipt_id", None))
        safe_set(root, "ReceiptBarcode", getattr(receipt, "receipt_barcode", None))
        safe_set(root, "ReceiptDate", getattr(receipt, "receipt_date", None))
        safe_set(root, "VendorVAT", getattr(receipt, "vendor_vat", None))
        safe_set(root, "VendorName", getattr(receipt, "vendor_name", None))
        safe_set(root, "VendorAddress", getattr(receipt, "vendor_address", None))

        items_elem = ET.SubElement(root, "Items")
        for item in getattr(receipt, "items", []):
            item_elem = ET.SubElement(items_elem, "Item")
            for key, value in getattr(item, "__dict__", {}).items():
                safe_set(item_elem, key, value)

        safe_set(root, "ValueSum", getattr(receipt, "value_sum", None))
        safe_set(root, "Currency", getattr(receipt, "currency", None))
        safe_set(root, "CashRegisterID", getattr(receipt, "cash_reg_id", None))

        tree = ET.ElementTree(root)
        file_path_name = f"{self.RECEIPT_DIRECTORY}/receipt_{datetime.datetime.now().strftime('%Y_%m_%d__%H:%M:%S')}.xml"
        with open(file_path_name, "wb+") as f:
            tree.write(f, encoding="utf-8", xml_declaration=True)
        logger.info(f"Receipt XML file created as {file_path_name}")

    
    def __json_receipt(self, receipt: ReceiptMeta) :
        def item_to_dict(item):
            # Convert ItemReceipt to dict, handling nested objects if needed
            if hasattr(item, "__dict__"):
                return {k: str(v) for k, v in item.__dict__.items()}
            return dict(item)

        receipt_dict = {
            "receipt_id": getattr(receipt, "receipt_id", None),
            "receipt_barcode": getattr(receipt, "receipt_barcode", None),
            "receipt_date": getattr(receipt, "receipt_date", None),
            "vendor_vat": getattr(receipt, "vendor_vat", None),
            "vendor_name": getattr(receipt, "vendor_name", None),
            "vendor_address": getattr(receipt, "vendor_address", None),
            "items": [item_to_dict(item) for item in getattr(receipt, "items", [])],
            "value_sum": str(getattr(receipt, "value_sum", None)),
            "currency": str(getattr(receipt, "currency", None)),
            "cash_reg_id": getattr(receipt, "cash_reg_id", None)
        }

        file_path_name = f"{self.RECEIPT_DIRECTORY}/receipt_{datetime.datetime.now().strftime('%d_%m_%Y__%H:%M:%S')}.json"
        with open(file_path_name, "w+", encoding="utf-8") as f:
            json.dump(receipt_dict, f, ensure_ascii=False, indent=4)
        logger.info(f"Receipt JSON file created as {file_path_name}")
        
    # WIĘCEJ FORMATOW
    
    def _create_invoice(self, transaction: Transaction, file_format: list[str]):
        # Create an invoice from B2B or B2C
        # Create a receipt 
        invoice_meta_obj: InvoiceMeta = InvoiceFactory(vendor=self.vendor, transaction=transaction)

        for ff in file_format:
            if ff == 'xml':
                self.__xml_invoice(invoice_meta_obj)
            if ff == 'edi':
                self.__edifact_invoice(invoice_meta_obj)
        
            
    
    def __xml_invoice(self, invoice: InvoiceMeta):
        # Create XML structure for InvoiceMeta, Buyer, and ItemInvoice
        root = ET.Element("Invoice")

        def safe_set(parent, tag, value):
            ET.SubElement(parent, tag).text = str(value) if value is not None else ""

        safe_set(root, "InvoiceID", getattr(invoice, "invoice_id", None))
        safe_set(root, "InvoiceDate", getattr(invoice, "invoice_date", None))
        safe_set(root, "VendorName", getattr(invoice, "vendor_name", None))
        safe_set(root, "VendorVAT", getattr(invoice, "vendor_vat", None))
        safe_set(root, "VendorEORI", getattr(invoice, "vendor_eori", None))
        safe_set(root, "VendorREGON", getattr(invoice, "vendor_regon", None))
        safe_set(root, "VendorAddress", getattr(invoice, "vendor_address", None))

        # Buyer section
        buyer = getattr(invoice, "buyer", None)
        if buyer:
            buyer_elem = ET.SubElement(root, "Buyer")
            safe_set(buyer_elem, "BuyerName", getattr(buyer, "buyer_name", None))
            safe_set(buyer_elem, "BuyerVAT", getattr(buyer, "buyer_vat", None))
            safe_set(buyer_elem, "BuyerEORI", getattr(buyer, "buyer_eori", None))
            safe_set(buyer_elem, "BuyerREGON", getattr(buyer, "buyer_regon", None))
            safe_set(buyer_elem, "Address", getattr(buyer, "address", None))
        else:
            ET.SubElement(root, "Buyer")  # Empty Buyer element if missing

        # Items section
        items_elem = ET.SubElement(root, "Items")
        for item in getattr(invoice, "items", []):
            item_elem = ET.SubElement(items_elem, "Item")
            safe_set(item_elem, "ItemNameBrandSize", getattr(item, "item_name_brand_size", None))
            safe_set(item_elem, "ItemBarcode", getattr(item, "item_barcode", None))
            safe_set(item_elem, "ItemMetaQuantity", getattr(item, "item_meta_quantity", None))
            safe_set(item_elem, "ItemQuantity", getattr(item, "item_quantity", None))
            safe_set(item_elem, "PriceIndNet", getattr(item, "price_ind_net", None))
            safe_set(item_elem, "ValueNet", getattr(item, "value_net", None))
            safe_set(item_elem, "PriceIndGross", getattr(item, "price_ind_gross", None))
            safe_set(item_elem, "ValueGross", getattr(item, "value_gross", None))
            safe_set(item_elem, "ItemVAT", getattr(item, "item_vat", None))
            safe_set(item_elem, "Currency", getattr(item, "currency", None))

        safe_set(root, "ValueSumNet", getattr(invoice, "value_sum_net", None))
        safe_set(root, "ValueSumGross", getattr(invoice, "value_sum_gross", None))
        safe_set(root, "AdditionalNotes", getattr(invoice, "addit_notes", None))
        safe_set(root, "Currency", getattr(invoice, "currency", None))

        file_path_name = f"{self.RECEIPT_DIRECTORY}/invoice_{datetime.datetime.now().strftime('%Y_%m_%d_%H:%M:%S')}.xml"
        tree = ET.ElementTree(root)
        with open(file_path_name, "wb+") as f:
            tree.write(f, encoding="utf-8", xml_declaration=True)
        logger.info(f"Invoice XML file created as {file_path_name}")
    
    def __edifact_invoice(self, invoice: InvoiceMeta):
        def escape_edifact(value):
            if value is None:
                return ''
            return str(value).replace("'", "?").replace("+", "?").replace(":", "?")

        def invoice_to_edifact(invoice: InvoiceMeta) -> str:
            # UNH - Message header
            segments = []
            segments.append(f"UNH+{escape_edifact(invoice.invoice_id)}+INVOIC:D:96A:UN:1.1'")
            # BGM - Beginning of message
            segments.append(f"BGM+380+{escape_edifact(invoice.invoice_id)}+9'")
            # DTM - Date/time/period
            segments.append(f"DTM+137:{escape_edifact(invoice.invoice_date)}:102'")
            # NAD+SU - Supplier (vendor)
            segments.append(
                f"NAD+SU+{escape_edifact(invoice.vendor_vat)}::VAT++{escape_edifact(invoice.vendor_name)}+{escape_edifact(invoice.vendor_address)}+++++{escape_edifact(invoice.vendor_eori)}:{escape_edifact(invoice.vendor_regon)}'"
            )
            # NAD+BY - Buyer
            buyer = getattr(invoice, "buyer", None)
            if buyer:
                segments.append(
                    f"NAD+BY+{escape_edifact(getattr(buyer, 'buyer_vat', ''))}::VAT++{escape_edifact(getattr(buyer, 'buyer_name', ''))}+{escape_edifact(getattr(buyer, 'address', ''))}+++++{escape_edifact(getattr(buyer, 'buyer_eori', ''))}:{escape_edifact(getattr(buyer, 'buyer_regon', ''))}'"
                )
            # CUX - Currencies
            segments.append(f"CUX+2:{escape_edifact(invoice.currency)}:9'")
            # Loop through items
            for idx, item in enumerate(getattr(invoice, "items", []), start=1):
                segments.append(
                    f"LIN+{idx}++{escape_edifact(item.item_barcode)}:SRV'"
                )
                segments.append(
                    f"IMD+F++{escape_edifact(item.item_name_brand_size)}'"
                )
                segments.append(
                    f"QTY+47:{escape_edifact(item.item_quantity)}:{escape_edifact(item.item_meta_quantity)}'"
                )
                segments.append(
                    f"PRI+AAA:{escape_edifact(item.price_ind_net)}'"
                )
                segments.append(
                    f"MOA+203:{escape_edifact(item.value_net)}'"
                )
                segments.append(
                    f"PRI+AAB:{escape_edifact(item.price_ind_gross)}'"
                )
                segments.append(
                    f"MOA+39:{escape_edifact(item.value_gross)}'"
                )
                segments.append(
                    f"TAX+7+{escape_edifact(item.item_vat)}:VAT'"
                )
            # MOA - Monetary amounts
            segments.append(f"MOA+77:{escape_edifact(invoice.value_sum_net)}'")
            segments.append(f"MOA+79:{escape_edifact(invoice.value_sum_gross)}'")
            # FTX - Free text (additional notes)
            if getattr(invoice, "addit_notes", None):
                segments.append(f"FTX+AAI+++{escape_edifact(invoice.addit_notes)}'")
            # UNT - Message trailer
            segments.append(f"UNT+{len(segments)+1}+{escape_edifact(invoice.invoice_id)}'")
            return "\n".join(segments)

        # Write the EDIFACT file
        edifact_str = invoice_to_edifact(invoice)
        file_path_name = f"{self.INVOICE_DIRECTORY}/invoice_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.edi"
        with open(file_path_name, "w+", encoding="utf-8") as f:
            f.write(edifact_str)
        logger.info(f"Invoice EDIFACT file created as {file_path_name}")
    
    
    
    def _create_import_received(self):
        pass
    

def connect_test(username, password, host_port, db_name):
    engine_connection = 'postgresql://{}:{}@{}/{}'.format(username,
                                                              password,
                                                              host_port,
                                                              db_name )
    engine = create_engine(engine_connection)
    print(f'CONNECTED! TO {engine}')



if __name__ == '__main__':
    time.sleep(5)
    logger.info('############ BEGIN ###############')
    
    shoe_db_conn = {
    "name" : os.environ.get('SHOE_DB_NAME'),
    "user" : os.environ.get('SHOE_DB_USER'),
    "pass" : os.environ.get('SHOE_DB_PASS'),
    "host" : os.environ['SHOE_DB_HOST'],
    "port" : os.environ['SHOE_DB_PORT']
    }
    setup_id = os.environ['SETUP_ID']
    
    # Read setup.json file

    with open("init_data/setups.json", "r", encoding="utf-8") as f:
        setups = json.load(f)
        setup_config = setups.get(setup_id)
    logger.info(f"Loaded setup.json: {setup_config}")
    
    
    
    init_shoe_DB(shoe_db_conn)
    
    sim_duration = setup_config.get('sim_duration', 1000000)
    
    vendor = Vendor(**setup_config['vendor'])
    
    shoe_shop_sim = ShoeShopSimulation(shoe_db_conn, 
                                       vendor_info=vendor.__dict__, 
                                       formats=['json', 'xml', 'edi'])
    shoe_shop_sim.simulate(sim_duration=sim_duration)
    # print(shoe_shop_sim._create_transaction())
    # while True:
    #     shoe_shop_sim._simulate_buying()
    #     time.sleep(20)
    # 'postgres'
    # 789456
    # 'postgres:5432'
    # 'shoe_storage'
        
    
    
    # insert_artificial_data_to_db()
    # test_factory()
    pass
    




