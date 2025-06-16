import structured_data_gen as stdg
from factories import ItemQuant, Transaction, Vendor
from factories import ReceiptMeta, ReceiptFactory, InvoiceMeta, InvoiceFactory

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


if __name__ == '__main__':
    test_receipt_invoices()
    