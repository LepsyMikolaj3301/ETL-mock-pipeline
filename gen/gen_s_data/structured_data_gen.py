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
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging, datetime
from factories import Shoe, Client, Storage, init_storage_vals
from factories import ShoeTableFactory, ClientTableFactory
# Receipt and Invoice generation
from factories import ItemQuant, Transaction, TransactionFactory, Vendor
from factories import ReceiptMeta, ReceiptFactory, InvoiceMeta, InvoiceFactory
import os
from sqlalchemy.sql.expression import func

# CREATING LOGGER
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# GLOBALNE ZMIENNE - DO ZMIANY
CURRENCY = 'EUR'


   
def init_shoe_DB(shoe_db_conn_info: dict[str, str], instances_count: int):
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
        logger.info(f'CONNECTED SUCCESSFULLY TO: {engine_connection}')
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
    
    # INIT SHOE TABLE
    # Insert Data to Table SHOE
    with Session() as session:
        # Inserting Data to table
        shoes_inserted = ShoeTableFactory.create_batch(size=instances_count, session=session, currency=CURRENCY)
        logger.info(f"Inserted {len(shoes_inserted)} shoes into shoe_table.")
        session.commit()
        shoe_ids = session.query(Shoe.shoe_id)
            
    # STORAGE DATA MADE WITHOUT 
    # Insert Data to Table STORAGE
    values = init_storage_vals(shoe_ids)
    
    try:
        with Session() as session:
            session.add_all(values)
            session.commit()
            logger.info(f"Inserted {len(values)} storage iteMs into storage_table.")
    except Exception as e:
        logger.error(f"ORM insert error: {e}")
    
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
        client_inserted = ClientTableFactory.create_batch(size=instances_count, session=session)
        logger.info(f"Inserted {len(client_inserted)} clients into {Client.__tablename__}.")
        session.commit()
    

# SHOE SHOP SIMULATOR (WITH DATABASE CONNECTION ORM)
class ShoeShopSimulation:
    """
    SHOE SHOP SIMULATION
    IT CREATES VARIOUS OBJECTS FOR DATA GENERATION IN INTERVALS (CRON)
    """    
    
    def __init__(self, shoe_db_conn_info, client_db_conn_info) -> None:
        host_port_shoe_db = ':'.join([shoe_db_conn_info['host'], shoe_db_conn_info['port']])
        host_port_client_db = ':'.join([client_db_conn_info['host'], client_db_conn_info['port']])
        
        engine_connection_shoe_db = 'postgresql://{}:{}@{}/{}'.format(shoe_db_conn_info['user'],
                                                              shoe_db_conn_info['pass'],
                                                              host_port_shoe_db,
                                                              shoe_db_conn_info['name'])
        
        engine_connection_client_db = 'postgresql://{}:{}@{}/{}'.format(client_db_conn_info['user'],
                                                                        client_db_conn_info['pass'],
                                                                        host_port_client_db,
                                                                        client_db_conn_info['name'])
        
        self.engine_shoe_db = create_engine(engine_connection_shoe_db)
        self.engine_client_db = create_engine(engine_connection_client_db)
        
        self.SessionShoe = sessionmaker(bind=self.engine_shoe_db)
        
        # connect to db to download static databases
        with self.engine_client_db.connect() as conn:
            self.client_table = pd.read_sql_table('clients_table', conn)
        with self.engine_shoe_db.connect() as conn:
            self.shoe_table = pd.read_sql_table('shoe_table', conn) 

        # Create amount of time to wait to restock STORAGE
        
    # @dataclass
    # class Client:
        
    # TODO: GENERACJA PARAGONÓW I FAKTUR PRZEZ SYMULACJA
    # ORAZ W AFEKCIE GENERACJA ZAMÓWIEŃ ORAZ PRZYSYŁEK
    
        
    def simulate_buy(self, sim_metadata: dict):
        # Generate new client info
        
        # Pass it down to the create receipt OR invoice
        # PICK A FORMAT
        
        # after creation, update 
        
        
        pass

    
    def __choose_products(self, num: int) -> list[ItemQuant]:
        with self.SessionShoe() as session:

            # DO ZMIANY
            products_bought = []
            # ADD LOGGER
            
            for product_result in session.query(Storage).filter(Storage.quantity > 10).order_by(func.random()).limit(num).all():
                prod = product_result[0]
                prod_shoe = self.shoe_table[self.shoe_table['shoe_id'] == prod.shoe_id]
                if not prod_shoe:
                    continue
                products_bought.append(ItemQuant(prod_shoe.model_name,
                                                 prod.shoe_size,
                                                 prod_shoe.brand,
                                                 prod.product_id,
                                                 max(1, int(random.expovariate(1/3))),
                                                 prod_shoe.price,
                                                 prod_shoe.currency
                                                ))
                # ZMNIEJSZ LICZBE QUANTITY ABY ZASYMULOWAĆ SPRZEDARZ
            return products_bought

    def _create_transaction(self) -> Transaction:
        
        # Losuj ilość z rozkładu wykładniczego (np. średnia 2, zaokrąglona do min. 1)
        quantity_diff_prod = max(1, int(random.expovariate(1/2)))
        
        # Create Bought Items
        bought_items: list[ItemQuant] = self.__choose_products(quantity_diff_prod)
        
        # Create Transition
        return TransactionFactory(items_list=bought_items)       
    
    def _create_receipt(self):
        
        # Create a receipt 

        pass
    
    def __xml_receipt(self, receipt: ReceiptMeta) :
        pass
    
    def __json_receipt(self, receipt: ReceiptMeta) :
        pass
    
    # WIĘCEJ FORMATOW
    
    def _create_invoice(self):
        # Create an invoice from B2B or B2C
        pass
    
    def __xml_invoice(self):
        pass
    
    def _create_import_order(self, ):
        pass
    
    def _create_import_receiver(self):
        pass
    

def connect_test(username, password, host_port, db_name):
    engine_connection = 'postgresql://{}:{}@{}/{}'.format(username,
                                                              password,
                                                              host_port,
                                                              db_name )
    engine = create_engine(engine_connection)
    print(f'CONNECTED! TO {engine}')


# TODO: Generowanie przychodzących oraz odchodzących produktów
# class ShoeWarehouse:
#     def __init__(self) -> None:
#         pass
    


   
# TODO: Generowanie paragonów i zwrotów
# class ShoeShop:
#     def __init__(self) -> None:
#         pass




if __name__ == '__main__':

    shoe_db_conn = {
    "name" : os.environ.get('SHOE_DB_NAME'),
    "user" : os.environ.get('SHOE_DB_USER'),
    "pass" : os.environ.get('SHOE_DB_PASS'),
    "host" : os.environ['SHOE_DB_HOST'],
    "port" : os.environ['SHOE_DB_PORT']
    }
    
    
    client_db_name = os.environ.get('CLIENT_DB_NAME')
    client_db_user = os.environ.get('CLIENT_DB_USER')
    client_db_pass = os.environ.get('CLIENT_DB_PASS')
    client_db_host_port = ':'.join([os.environ['CLIENT_DB_HOST'], os.environ['CLIENT_DB_PORT']])
    
    
    
    # 'postgres'
    # 789456
    # 'postgres:5432'
    # 'shoe_storage'
        
        
    
    # insert_artificial_data_to_db()
    # test_factory()
    pass
    




