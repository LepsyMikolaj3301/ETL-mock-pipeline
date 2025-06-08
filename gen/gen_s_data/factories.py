import random
from faker import Faker
from faker.providers import barcode
from utils_gen import ShoeProvider, client_gender
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Numeric, Integer, Float, Date
from dataclasses import dataclass, field
import factory
from factory.alchemy import SQLAlchemyModelFactory
import logging, datetime
from typing import List



# BASIC OBJECTS
fake = Faker()
fake.add_provider(ShoeProvider)
fake.add_provider(barcode.Provider)
Base = declarative_base()


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
    shoe_size = Column(Float)
    quantity = Column(Integer())
    
class Client(Base):
    __tablename__ = 'clients_table'
    client_id = Column(String(36), primary_key=True)
    client_first_name = Column(String(120), nullable=False)
    client_last_name = Column(String(120), nullable=False)
    client_gender = Column(String)
    client_email = Column(String(100), nullable=False, unique=True)
    client_date_of_birth = Column(Date)  # Use Date if you want: from sqlalchemy import Date
    client_phone_number = Column(String(30))
    client_billing_address = Column(String)
    client_shipping_address = Column(String)
    client_city = Column(String(100))
    client_postal_code = Column(String(20))
    client_country = Column(String(50))
    client_acc_createAt = Column(Date, onupdate=func.now())  # Use Date and func.now() for real DB default

class ShoeTableFactory(SQLAlchemyModelFactory):
    class Meta: # type: ignore
        model = Shoe
        sqlalchemy_session = None

    shoe_id = factory.declarations.LazyAttribute(lambda _: fake.uuid4())
    brand = factory.declarations.LazyAttribute(lambda _: fake.shoe_brand())
    model_name = factory.declarations.LazyAttribute(lambda _: fake.shoe_name())
    category = factory.declarations.LazyAttribute(lambda _: fake.shoe_category())
    price = factory.declarations.LazyAttribute(lambda _: fake.shoe_price())



def maybe_value(func, prob=0.90):
    # Returns a lambda that with probability `prob` returns func(), else None
    return lambda _: func() if random.random() < prob else None


class ClientTableFactory(SQLAlchemyModelFactory):
    class Meta:  # type: ignore
        model = Client
        sqlalchemy_session = None

    client_id = factory.declarations.LazyAttribute(lambda _: fake.uuid4())
    client_first_name = factory.declarations.LazyAttribute(lambda _: fake.first_name())
    client_last_name = factory.declarations.LazyAttribute(lambda _: fake.last_name())
    client_gender = factory.declarations.LazyAttribute(maybe_value(client_gender, 0.63))
    client_email = factory.declarations.LazyAttribute(lambda _: fake.unique.email())
    client_date_of_birth = factory.declarations.LazyAttribute(maybe_value(lambda: fake.date_of_birth(minimum_age=13, maximum_age=80), 0.65))
    client_phone_number = factory.declarations.LazyAttribute(maybe_value(fake.phone_number, 0.95))
    client_billing_address = factory.declarations.LazyAttribute(lambda _: fake.address())
    client_shipping_address = factory.declarations.LazyAttribute(maybe_value(fake.address))
    client_city = factory.declarations.LazyAttribute(maybe_value(fake.city))
    client_postal_code = factory.declarations.LazyAttribute(maybe_value(fake.postcode))
    client_country = factory.declarations.LazyAttribute(maybe_value(fake.country))
    client_acc_createAt = factory.declarations.LazyAttribute(lambda _: fake.date_this_decade())

# RECEIPT GENERATION
# IT CONSISTS OF:
#   - Receipt Metadata
#   - Vendor info (shop metadata)
#   - List of Bought Items

@dataclass
class Vendor:
    vendor_id: str
    vendor_name: str
    vat_id: str
    street: str
    city: str
    postal_code: str
    country: str
    
@dataclass
class ReceiptItem:
    receipt_item_id: int
    barcode_id: 
    unit_of_entry: str
    quantity: int
    movement_type: str
    storage_bin: str
    batch_number: str    

@dataclass
class ReceiptMeta:
    receipt_id: str
    receipt_data: str
    reference_document: str
    plant: str
    storage_location: str
    document_currency: str
    vendor: Vendor
    items: List[ReceiptItem] = field(default_factory=list)


        # ZOBACZ CHAT CO WYGENEROWAŁ - Czat = SAP invoice XML
class ReceiptFactory(factory.base.Factory):
    class Meta: # type: ignore
        model = ReceiptMeta
        
    
 

 



def init_storage_vals(shoe_ids) -> list:
    values = []
    for si in shoe_ids:
        for shoe_size in range(36, 47):
            values.append(Storage(fake.ean13(),
                                  si,
                                  shoe_size,
                                  random.randint(0, 100)))
    return values