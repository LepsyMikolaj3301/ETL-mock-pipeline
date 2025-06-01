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


???
SKLEP INTERNETOWY

- Użytkownik ID:
    - Zamówienia online | ID zamówienia, koszyk, adres dostawy, metoda płatności | JSON
    - Historia transakcji | historia dla tego użytkownika | JSON, CSV
    ...
???

TODO: ZROBIENIE BAZY DANYCH Z PRODUKTAMI
TODO: Tworzenie faktur/paragonów (info od Bazy)
TODO: zrobienie Magazynu (info do bazy)
TODO: Zrobienie dziennego raportu 
"""
import random
import psycopg2
from faker import Faker
from faker.providers import barcode
from shoe_provider import ShoeProvider
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Numeric, Integer
from dataclasses import dataclass
import factory
from factory.alchemy import SQLAlchemyModelFactory
import logging, time
import os

# CREATING LOGGER
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# BASIC OBJECTS
fake = Faker()
fake.add_provider(ShoeProvider)
fake.add_provider(barcode.Provider)
Base = declarative_base()
# fake_providers = faker.providers.company.Provider()

# class DatabaseInsertions:
#     def __init__(self) -> None:
#         # Connect to the database
#         while True:
#             try:
#                 self.conn = psycopg2.connect(
#                 dbname="shoe_storage",
#                 user="postgres",
#                 password=789456,
#                 host="postgres",
#                 port=5432
#                 )
#                 if self.conn:
#                     print('CONNECTION SUCCESSFUL!')
#                     break
#             except Exception as e:
#                 print('CONNECTION UNSUCCESFUL', e)
    
#     def exec_print_stmt(self, stmt: str):
#         with self.conn.cursor() as cur:
#             try:
#                 cur.execute(stmt)
#                 rows = cur.fetchall()
#                 for row in rows:
#                     print(" | ".join(str(val) for val in row))
#             except Exception as e:
#                 print("Execute error", e)
#                 self.conn.rollback()
    
#     def init_brand_table(self, instances_count: int):
#         # Initialize Factory object
#         shoe_fac = BrandTableFactory()
        
#         values = [
#             (shoe_fac.shoe_id,
#              shoe_fac.brand, 
#              shoe_fac.model_name, 
#              shoe_fac.category, 
#              shoe_fac.price)
#             for _ in range(instances_count) 
#         ]
        
#         stmt = """INSERT INTO brand_table (shoe_id, brand, model_name, category, price)
#             VALUES (%s, %s, %s, %s, %s)
#             ON CONFLICT (shoe_id) DO NOTHING;
#             """
        
        
        
#         # Insert brands to db
#         with self.conn.cursor() as cur:
            
            
#             try:
#                 cur.executemany(stmt, values)
#                 rows = cur.fetchall()
#                 for row in rows:
#                     print(" | ".join(str(val) for val in row))
#             except Exception as e:
#                 print("Execute error", e)
#                 self.conn.rollback()
            
            
#         pass

#     def init_insert_storage(self):
#         pass
    
# #create_engine => username, password, hostname:port, database
# def get_db_engine():
#     return create_engine('postgresql://{}:{}@{}/{}'.format('postgres', 789456, 'postgres:5432', 'shoe_storage'))

# def insert_artificial_data_to_db():
#     db_wrp = DbWrap()
#     db_wrp.exec_print_stmt("SELECT * FROM brand_table;")


class Shoe(Base):
    __tablename__ = 'shoe_table'
    shoe_id = Column(String(36), primary_key=True)
    brand = Column(String(100))
    model_name = Column(String(100), nullable=False)
    category = Column(String(50))
    price = Column(Numeric(10, 2), nullable=False)

class Storage(Base):
    __tablename__ = 'storage_table'
    product_id = Column(String(13), primary_key=True)
    shoe_id = Column(String(36))
    quantity = Column(Integer())
    

class ShoeTableFactory(SQLAlchemyModelFactory):
    class Meta: # type: ignore
        model = Shoe
        sqlalchemy_session = None
    
    shoe_id = factory.declarations.LazyAttribute(lambda _: fake.uuid4())
    brand = factory.declarations.LazyAttribute(lambda _: fake.shoe_brand())
    model_name = factory.declarations.LazyAttribute(lambda _: fake.shoe_name())
    category = factory.declarations.LazyAttribute(lambda _: fake.shoe_category())
    price = factory.declarations.LazyAttribute(lambda _: fake.shoe_price())


class Receipt:
    def __init__(self, receipt_id, date, total, payment_method):
        self.receipt_id = receipt_id
        self.date = date
        # TODO: do dodania info o paragonahc
        self.items = None
        self.total = total
        self.payment_method = payment_method


        
class ReceiptFactory(factory.base.Factory):
    class Meta: # type: ignore
        model = Receipt
    
    


class InitDB:
    def __init__(self) -> None:
        #TODO #1 Change from HARDCODED connection to ENV variables
        self.engine = create_engine('postgresql://{}:{}@{}/{}'.format('postgres',
                                                                      789456,
                                                                      'postgres:5432',
                                                                      'shoe_storage'))
        self.Session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)  # Ensure tables exist

    def init_shoe_table(self, instances_count: int):
        # Insert Data to Table
        with self.Session() as session:
            # Inserting Data to table
            shoes_inserted = ShoeTableFactory.create_batch(size=instances_count, session=session)
            logger.info(f"Inserted {len(shoes_inserted)} shoes into shoe_table.")
            session.commit()
            
            
            
            
    def init_storage_table(self):
        with self.Session() as session:
            shoe_ids = session.query(Shoe.shoe_id)
            
        values = [Storage(fake.ean13(),
                          si,
                          random.randint(0, 200))
                  for si in shoe_ids]
        try:
            with self.Session() as session:
                session.add_all(values)
                session.commit()
                logger.info(f"Inserted {len(values)} storage itmes into storage_table.")
        except Exception as e:
            logger.error(f"ORM insert error: {e}")

# SHOE SHOP SIMULATOR (WITH DATABASE CONNECTION ORM)
class ShoeShopSimulation:
    """
    SHOE SHOP SIMULATION
    IT CREATES VARIOUS OBJECTS FOR DATA GENERATION
        DAILY 
        
    """
    def __init__(self) -> None:
        self.engine = create_engine('postgresql://{}:{}@{}/{}'.format('postgres',
                                                                      789456,
                                                                      'postgres:5432',
                                                                      'shoe_storage'))
        self.Session = sessionmaker(bind=self.engine)


    def _create_receipt(self):
        # Create a receipt 
    
    




# TODO: Generowanie przychodzących oraz odchodzących produktów
# class ShoeWarehouse:
#     def __init__(self) -> None:
#         pass
    


   
# TODO: Generowanie paragonów i zwrotów
# class ShoeShop:
#     def __init__(self) -> None:
#         pass

if __name__ == '__main__':
    # insert_artificial_data_to_db()
    test_factory()
    




