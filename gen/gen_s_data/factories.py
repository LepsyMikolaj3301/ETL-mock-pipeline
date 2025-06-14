import random
import factory.utils
from faker import Faker
from faker. providers import barcode
from utils_gen import ShoeProvider, client_gender
from sqlalchemy.sql import func
from sqlalchemy.sql.expression import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Numeric, Integer, Float, Date
from dataclasses import dataclass, field
from sqlalchemy.orm import Session
import factory
from factory.alchemy import SQLAlchemyModelFactory
from typing import List




# BASIC OBJECTS
fake = Faker('pl_PL')
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
    currency = Column(String(3))

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
        
    class Params:
        currency: str

    shoe_id = factory.declarations.LazyAttribute(lambda _: fake.uuid4())
    brand = factory.declarations.LazyAttribute(lambda _: fake.shoe_brand())
    model_name = factory.declarations.LazyAttribute(lambda _: fake.shoe_name())
    category = factory.declarations.LazyAttribute(lambda _: fake.shoe_category())
    price = factory.declarations.LazyAttribute(lambda _: fake.shoe_price())
    currency = factory.declarations.LazyAttribute(lambda self: self.currency)


def init_storage_vals(shoe_ids) -> list:
    values = []
    for si in shoe_ids:
        for shoe_size in range(36, 47):
            values.append(Storage(fake.ean13(),
                                  si,
                                  shoe_size,
                                  random.randint(10, 100)))
    return values

def _maybe_value(func, prob=0.90):
    # Returns a lambda that with probability `prob` returns func(), else None
    return lambda _: func() if random.random() < prob else None


class ClientTableFactory(SQLAlchemyModelFactory):
    class Meta:  # type: ignore
        model = Client
        sqlalchemy_session = None

    client_id = factory.declarations.LazyAttribute(lambda _: fake.uuid4())
    client_first_name = factory.declarations.LazyAttribute(lambda _: fake.first_name())
    client_last_name = factory.declarations.LazyAttribute(lambda _: fake.last_name())
    client_gender = factory.declarations.LazyAttribute(_maybe_value(client_gender, 0.63))
    client_email = factory.declarations.LazyAttribute(lambda _: fake.unique.email())
    client_date_of_birth = factory.declarations.LazyAttribute(_maybe_value(lambda: fake.date_of_birth(minimum_age=13, maximum_age=80), 0.65))
    client_phone_number = factory.declarations.LazyAttribute(_maybe_value(fake.phone_number, 0.95))
    client_billing_address = factory.declarations.LazyAttribute(lambda _: fake.address())
    client_shipping_address = factory.declarations.LazyAttribute(_maybe_value(fake.address))
    client_city = factory.declarations.LazyAttribute(_maybe_value(fake.city))
    client_postal_code = factory.declarations.LazyAttribute(_maybe_value(fake.postcode))
    client_country = factory.declarations.LazyAttribute(_maybe_value(fake.country))
    client_acc_createAt = factory.declarations.LazyAttribute(lambda _: fake.date_this_decade())

# RECEIPT GENERATION
# IT CONSISTS OF:
#   - Receipt Metadata
#   - Vendor info (shop metadata)
#   - List of Bought Items

# class ProductFactory(factory.base.Factory):
#     class Meta: #type: ignore
#         model = Storage
    
    
    
#     @classmethod
#     def _create(cls, model_class, *args, **kwargs):
        
#         session = kwargs.pop("session", None)
#         if not isinstance("session", Session):
#             raise ValueError("A valid Session must be provided.")
#         # Try to pull an existing Product from the DB
#         existing = session.query(Storage).order_by(func.random()).first()
        
#         if not existing:
#             raise ValueError("No products available in the DB to generate a receipt.")
#         return existing

@dataclass
class Buyer:
    buyer_name: str
    buyer_vat: str
    buyer_eori: str
    buyer_regon: str
    address: str

class BuyerFactory(factory.base.Factory):
    class Meta:  # type: ignore
        model = Buyer

    buyer_name = factory.declarations.LazyAttribute(lambda _: fake.company())
    buyer_vat = factory.declarations.LazyAttribute(lambda _: fake.company_vat())
    buyer_eori = factory.declarations.LazyAttribute(lambda _: f"PL{fake.random_number(digits=12, fix_len=True)}")
    buyer_regon = factory.declarations.LazyAttribute(lambda _: fake.regon())
    address = factory.declarations.LazyAttribute(lambda _: f"{fake.address().replace(chr(10), ', ')}, {fake.country()}")



@dataclass
class ItemQuant:
    item_name: str
    item_size: int
    item_brand: str
    item_barcode: str
    quantity: int
    price_ind: float
    currency: str

@dataclass
class Transaction:
    client_info: Client | None
    items_list: list[ItemQuant]


@dataclass
class Vendor:
    vendor_name: str
    vendor_vat: str
    vendor_eori: str
    vendor_regon: str
    street: str
    num_of_addr: str
    city: str
    postal_code: str
    country: str
    email: str
    
# --------------------------------------------------------------------
#    RECEIPTs
# --------------------------------------------------------------------


# ITEM (SUB)FACTORY


@dataclass
class ItemReceipt:
    item_name_brand_size: str
    item_barcode: str
    item_quantity: int
    price_ind: float
    total_value: float
    item_vat: float
    currency: str

class ItemReceiptFactory(factory.base.Factory):
    class Meta: #type: ignore
        model = ItemReceipt
        
    class Params:
        item_quant: ItemQuant
    
    # item_name_brand_size = factory.declarations.LazyAttribute(lambda o: o.item_quant)
    
    @factory.helpers.lazy_attribute
    def item_name_brand_size(self):
        return '|'.join([self.item_quant.item_name, #type: ignore
                         self.item_quant.item_brand, #type: ignore
                         self.item_quant.item_size #type: ignore
                         ])
    
    item_barcode = factory.declarations.LazyAttribute(lambda self: self.item_quant.item_barcode)
    item_quantity = factory.declarations.LazyAttribute(lambda self: self.item_quant.quantity)
    price_ind = factory.declarations.LazyAttribute(lambda self: self.item_quant.price_ind)
    currency = factory.declarations.LazyAttribute(lambda self: self.item_quant.currency)
    item_vat = 0.23
    
    @factory.helpers.lazy_attribute
    def total_value(self):
        return self.item_quant.quantity * self.item_quant.price_ind #type: ignore
    
        
# RECEIPT PARENT FACTORY 

@dataclass
class ReceiptMeta:
    receipt_id: str
    receipt_barcode: str
    receipt_date: str
    vendor_vat: str
    vendor_name: str
    vendor_address: str
    items: List[ItemReceipt]
    value_sum: float
    currency: str
    cash_reg_id: str

class ReceiptFactory(factory.base.Factory):
    class Meta: # type: ignore
        model = ReceiptMeta

    class Params:
        vendor: Vendor
        transaction: Transaction
    
    receipt_date = factory.declarations.LazyAttribute(lambda _: fake.date_this_month(before_today=True).strftime("%Y-%m-%d"))
    receipt_id = factory.declarations.Sequence(lambda n: f"GR-{factory.declarations.SelfAttribute('..receipt_date')}-{n}")
    receipt_barcode = factory.declarations.LazyAttribute(lambda _: fake.localized_ean8())
    vendor_vat = factory.declarations.LazyAttribute(lambda self: self.vendor.vendor_vat)
    vendor_name = factory.declarations.LazyAttribute(lambda self: self.vendor.vendor_name)
    
    @factory.helpers.lazy_attribute
    def vendor_address(self):
        return ' '.join([self.vendor.street, self.vendor.num_of_addr, self.vendor.city, self.vendor.country]) #type: ignore
    
    items = factory.declarations.List([factory.declarations.SubFactory(ItemReceiptFactory, item_quant=item_quant) for item_quant in self.transaction.items_list]) #type: ignore

    @factory.helpers.lazy_attribute
    def value_sum(self):
        fact_items = factory.declarations.SelfAttribute('..items')
        list_prices = [it.price_sum_by_item for it in fact_items] #type: ignore
        return sum(list_prices)
    
    @factory.helpers.lazy_attribute
    def currency(self):
        fact_items = factory.declarations.SelfAttribute('..items')
        currencies = set([it.currency for it in fact_items]) #type: ignore
        return currencies
    
    
    cash_reg_id = factory.declarations.LazyFunction(lambda : f'CASHREG{fake.uuid4()}')

# --------------------------------------------------------------------
#    INVOICE
# --------------------------------------------------------------------


# ITEM (SUB)FACTORY


@dataclass
class ItemInvoice:
    item_name_brand_size: str
    item_barcode: str
    item_meta_quantity: str # Liczba poj, litry itd
    item_quantity: int
    price_ind_net: float
    value_net: float
    price_ind_gross: float
    value_gross: float
    item_vat: str
    currency: str

# TODO: Dokończenie fabryki Faktur
class ItemInvoiceFactory(factory.base.Factory):
    class Meta: #type: ignore
        model = ItemReceipt
        
    class Params:
        item_quant: ItemQuant
    
    # item_name_brand_size = factory.declarations.LazyAttribute(lambda o: o.item_quant)
    
    @factory.helpers.lazy_attribute
    def item_name_brand_size(self):
        return ';'.join([self.item_quant.item_name, #type: ignore
                         self.item_quant.item_brand, #type: ignore
                         self.item_quant.item_size #type: ignore
                         ])
    
    item_barcode = factory.declarations.LazyAttribute(lambda self: self.item_quant.item_barcode)
    item_meta_quantity = 'Szt.'
    item_quantity = factory.declarations.LazyAttribute(lambda self: self.item_quant.quantity)
    price_ind = factory.declarations.LazyAttribute(lambda self: self.item_quant.price_ind)
    currency = factory.declarations.LazyAttribute(lambda self: self.item_quant.currency)
    item_vat = "23%"
    
    
      
    
    @factory.helpers.lazy_attribute
    def price_sum_by_item(self):
        return self.item_quant.quantity * self.item_quant.price_ind #type: ignore
    


@dataclass
class InvoiceMeta:
    invoice_id: str
    invoice_date: str
    vendor_name: str
    vendor_vat: str
    vendor_eori: str
    vendor_regon: str
    vendor_address: str
    buyer: str
    items: List[ItemInvoice]
    price_sum: float
    
    
        
class InvoiceFactory(factory.base.Factory):
    class Meta: #type: ignore
        model = InvoiceMeta
        
        
    class Params:
        vendor: Vendor
        transaction: Transaction
    
    invoice_date = factory.declarations.LazyAttribute(lambda _: fake.date_this_century(before_today=True).strftime("%Y-%m-%d"))
    invoice_id = factory.declarations.Sequence(lambda n: f"INV-{factory.declarations.SelfAttribute('..receipt_date')}-{n}")
    vendor_vat = factory.declarations.LazyAttribute(lambda self: self.vendor.vendor_vat)
    vendor_eori = factory.declarations.LazyAttribute(lambda self: self.vendor.vendor_eori)
    vendor_regon = factory.declarations.LazyAttribute(lambda self: self.vendor.vendor_regon)
    vendor_name = factory.declarations.LazyAttribute(lambda self: self.vendor.vendor_name)
    
    @factory.helpers.lazy_attribute
    def vendor_address(self):
        return ' '.join([self.vendor.street, self.vendor.num_of_addr, self.vendor.city, self.vendor.country]) #type: ignore

    buyer = factory.declarations.SubFactory(BuyerFactory)
    items = factory.declarations.List([factory.declarations.SubFactory(ItemReceiptFactory, item_quant=item_quant) for item_quant in self.transaction.items_list]) #type: ignore
    
    @factory.helpers.lazy_attribute
    def price_sum(self):
        fact_items = factory.declarations.SelfAttribute('..items')
        list_prices = [it.price_sum_by_item for it in fact_items] #type: ignore
        return sum(list_prices)
    
    @factory.helpers.lazy_attribute
    def currency(self):
        fact_items = factory.declarations.SelfAttribute('..items')
        currencies = set([it.currency for it in fact_items]) #type: ignore
        return currencies

    
 

 


