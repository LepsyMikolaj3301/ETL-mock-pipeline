import random
from faker import Faker
from faker. providers import barcode
from utils_gen import ShoeProvider, client_gender
from sqlalchemy.sql import func
from sqlalchemy.sql.expression import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Numeric, Integer, Float, Date
from sqlalchemy.orm import relationship
from dataclasses import dataclass, field
from datetime import datetime
import factory
from factory.alchemy import SQLAlchemyModelFactory
from typing import List
from sqlalchemy import ForeignKey




# BASIC OBJECTS
fake = Faker('pl_PL')
fake.add_provider(ShoeProvider)
fake.add_provider(barcode.Provider)
Base = declarative_base()


class Shoe(Base):
    __tablename__ = 'shoe_table'
    shoe_id = Column(String(36), ForeignKey('storage_table.product_id'), primary_key=True)
    shoe_brand = Column(String(100))
    shoe_model_name = Column(String(100), nullable=False)
    shoe_category = Column(String(50))
    shoe_price = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3))

    storage = relationship("Storage", back_populates="shoe", uselist=False)

class Storage(Base):
    __tablename__ = 'storage_table'
    product_id = Column(String(13), primary_key=True)
    # Add ForeignKey constraint to reference Shoe.shoe_id
    shoe_id = Column(String(36), nullable=False)
    shoe_size = Column(Integer())
    product_quantity = Column(Integer())
    
    shoe = relationship("Shoe", back_populates="storage", uselist=False)

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
        sqlalchemy_session_persistence = 'flush'
    
    shoe_id = factory.declarations.LazyAttribute(lambda _: fake.uuid4())
    shoe_brand = factory.declarations.LazyAttribute(lambda _: fake.shoe_brand())
    shoe_model_name = factory.declarations.LazyAttribute(lambda _: fake.shoe_name())
    shoe_category = factory.declarations.LazyAttribute(lambda _: fake.shoe_category())
    shoe_price = factory.declarations.LazyAttribute(lambda _: fake.shoe_price())
    currency = factory.declarations.LazyAttribute(lambda self: self.currency)

    
class StorageTableFactory(SQLAlchemyModelFactory):
    class Meta: # type: ignore
        model = Storage
        sqlalchemy_session = None
        sqlalchemy_session_persistence = 'flush'
    
    # class Params:
    #     shoe_id: str | None = None
    #     shoe_size: int | None = None
    
    product_id = factory.declarations.LazyAttribute(lambda _: fake.ean13())
    shoe_id = factory.declarations.LazyAttribute(lambda o: o.shoe_id)
    shoe_size = factory.declarations.LazyAttribute(lambda o: o.shoe_size)
    product_quantity = factory.declarations.LazyAttribute(lambda _: random.randint(10, 45))
    
    # @classmethod
    # def _create(cls, model, **kwargs):
    #     """Custom instantiation to handle custom parameters."""
    #     shoe_id = kwargs.pop('shoe_id')  # you can manipulate here
    #     shoe_size = kwargs.pop('shoe_size')
    #     storage = model(shoe_id=shoe_id, shoe_size=shoe_size, **kwargs)

    #     return storage
    
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
    items_list: list[ItemQuant]
    transaction_type: str
    transaction_money: str

class TransactionFactory(factory.base.Factory):
    class Meta:  # type: ignore
        model = Transaction

    class Params:
        items_list_param: list[ItemQuant] | None = None

    items_list = factory.declarations.LazyAttribute(lambda self: self.items_list_param if self.items_list_param is not None else [])
    
    transaction_type = factory.declarations.LazyFunction(lambda: random.choice(['CARD', 'CASH', 'ONLINE', 'BLIK', 'PAYPAL']))
    
    @factory.helpers.lazy_attribute
    def transaction_money(self):
        if self.transaction_type == 'CARD':
            return fake.iban()
        elif self.transaction_type == 'BLIK':
            return fake.bothify(text='######')
        elif self.transaction_type == 'PAYPAL':
            return fake.phone_number()
        else:
            return None
    

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
        item_q: ItemQuant | None = None
    
    # item_q = factory.declarations.LazyAttribute(lambda o: o.item_quant)    
    # item_name_brand_size = factory.declarations.LazyAttribute(lambda o: o.item_quant)
    # self.item_q = self.item_quant #type: ignore
    
    item_name_brand_size = factory.declarations.LazyAttribute(lambda self: '|'.join([self.item_q.item_name, #type: ignore
                         self.item_q.item_brand, #type: ignore
                         str(self.item_q.item_size) #type: ignore
                         ]))
    
    item_barcode = factory.declarations.LazyAttribute(lambda self: self.item_q.item_barcode)
    item_quantity = factory.declarations.LazyAttribute(lambda self: self.item_q.quantity)
    price_ind = factory.declarations.LazyAttribute(lambda self: self.item_q.price_ind)
    currency = factory.declarations.LazyAttribute(lambda self: self.item_q.currency)
    item_vat = 0.23
    
    total_value = factory.declarations.LazyAttribute(lambda self: self.item_q.quantity * self.item_q.price_ind) #type: ignore
    
        
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
    """Receipt Factory

    Args:
        Params.vendor (Vendor): Vendor info
        Params.transaction (Transaction): Transaction for Receipt
    Returns:
        ReceiptMeta: Receipt Dataclass
    """
    class Meta: # type: ignore
        model = ReceiptMeta

    class Params:
        vendor: Vendor | None = None
        transaction: Transaction | None = None
    
    receipt_date = factory.declarations.LazyAttribute(lambda _: datetime.today().strftime('%Y-%m-%d;%H:%M:%S'))
    receipt_id = factory.declarations.LazyAttributeSequence(lambda o, n: f"GR-{o.receipt_date}-{n}")
    receipt_barcode = factory.declarations.LazyAttribute(lambda _: fake.localized_ean8())
    vendor_vat = factory.declarations.LazyAttribute(lambda self: self.vendor.vendor_vat)
    vendor_name = factory.declarations.LazyAttribute(lambda self: self.vendor.vendor_name)
    vendor_address = factory.declarations.LazyAttribute(lambda self: ' '.join([self.vendor.street, self.vendor.num_of_addr, self.vendor.city, self.vendor.country])) #type: ignore
    
    @factory.helpers.lazy_attribute
    def items(self):
        return [ItemReceiptFactory(item_q=itqt) for itqt in self.transaction.items_list] #type: ignore

    @factory.helpers.lazy_attribute
    def value_sum(self):
        list_prices = [it.total_value for it in self.items] #type: ignore
        return round(sum(list_prices), 2)
    
    @factory.helpers.lazy_attribute
    def currency(self):
        currencies = set([it.currency for it in self.items]) #type: ignore
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

class ItemInvoiceFactory(factory.base.Factory):
    class Meta: #type: ignore
        model = ItemInvoice
        
    class Params:
        item_quant: ItemQuant | None = None
    
    # item_name_brand_size = factory.declarations.LazyAttribute(lambda o: o.item_quant)
    
    @factory.helpers.lazy_attribute
    def item_name_brand_size(self):
        return ';'.join([self.item_quant.item_name, #type: ignore
                         self.item_quant.item_brand, #type: ignore
                         str(self.item_quant.item_size) #type: ignore
                         ])
    
    item_barcode = factory.declarations.LazyAttribute(lambda o: o.item_quant.item_barcode)
    item_meta_quantity = 'Szt.'
    item_quantity = factory.declarations.LazyAttribute(lambda o: o.item_quant.quantity)
    price_ind_net = factory.declarations.LazyAttribute(lambda o: round(float(o.item_quant.price_ind) - (0.23 * float(o.item_quant.price_ind)), 2))
    value_net = factory.declarations.LazyAttribute(lambda o: round(o.price_ind_net * int(o.item_quant.quantity), 2))
    price_ind_gross = factory.declarations.LazyAttribute(lambda o: o.item_quant.price_ind)
    value_gross = factory.declarations.LazyAttribute(lambda o: round(o.item_quant.price_ind * o.item_quant.quantity, 2))
    item_vat = "23%"
    currency = factory.declarations.LazyAttribute(lambda o: o.item_quant.currency)
    


@dataclass
class InvoiceMeta:
    invoice_id: str
    invoice_date: str
    vendor_name: str
    vendor_vat: str
    vendor_eori: str
    vendor_regon: str
    vendor_address: str
    buyer: Buyer
    items: List[ItemInvoice]
    value_sum_net: float
    value_sum_gross: float
    addit_notes: str
    currency: str
    
        
class InvoiceFactory(factory.base.Factory):
    """The invoice factory
    

    Args:
        Params.vendor(Vendor): Accepts the vendor Parameter
        Params.transaction(Transaction): Accepts a transaction
    Returns:
        InvoiceMeta: Invoice dataclass
    """
    class Meta: #type: ignore
        model = InvoiceMeta
        
        
    class Params:
        vendor: Vendor | None = None
        transaction: Transaction | None = None
    
    invoice_date = factory.declarations.LazyAttribute(lambda _: datetime.today().strftime('%Y-%m-%d;%H:%M:%S'))
    invoice_id = factory.declarations.LazyAttributeSequence(lambda o, n: f"INV-{o.invoice_date}-{n}")
    vendor_vat = factory.declarations.LazyAttribute(lambda self: self.vendor.vendor_vat)
    vendor_eori = factory.declarations.LazyAttribute(lambda self: self.vendor.vendor_eori)
    vendor_regon = factory.declarations.LazyAttribute(lambda self: self.vendor.vendor_regon)
    vendor_name = factory.declarations.LazyAttribute(lambda self: self.vendor.vendor_name)
    
    @factory.helpers.lazy_attribute
    def vendor_address(self):
        return ' '.join([self.vendor.street, self.vendor.num_of_addr, self.vendor.city, self.vendor.country]) #type: ignore

    buyer = factory.declarations.SubFactory(BuyerFactory)

    @factory.helpers.lazy_attribute
    def items(self):
        return [ItemInvoiceFactory(item_quant=item_quant) for item_quant in self.transaction.items_list]  # type: ignore
    
    @factory.helpers.lazy_attribute
    def value_sum_net(self):
        list_prices = [it.value_net for it in self.items] #type: ignore
        return round(sum(list_prices), 2)
    
    @factory.helpers.lazy_attribute
    def value_sum_gross(self):
        list_prices = [it.value_gross for it in self.items] #type: ignore
        return round(sum(list_prices), 2)
    
    @factory.helpers.lazy_attribute
    def currency(self):
        return set([it.currency for it in self.items]) #type: ignore
    
    addit_notes = factory.declarations.LazyAttribute(lambda n: fake.text(300))

    
 

 



