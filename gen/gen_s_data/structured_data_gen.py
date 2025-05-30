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
import psycopg2
from faker import Faker
import logging, time
import os


class DbWrap:
    def __init__(self) -> None:
        # Connect to the database
        while True:
            try:
                self.conn = psycopg2.connect(
                dbname="shoe_storage",
                user="postgres",
                password=789456,
                host="postgres",
                port=5432
                )
                if self.conn:
                    print('CONNECTION SUCCESSFUL!')
                    break
            except Exception as e:
                print('CONNECTION UNSUCCESFUL', e)
    
    def exec_print_stmt(self, stmt: str):
        with self.conn.cursor() as cur:
            try:
                cur.execute(stmt)
                rows = cur.fetchall()
                for row in rows:
                    print(" | ".join(str(val) for val in row))
            except Exception as e:
                print("Execute error", e)
                self.conn.rollback()
            
 
            


# #create_engine => username, password, hostname:port, database
# def get_db_engine():
#     return create_engine('postgresql://{}:{}@{}/{}'.format('postgres', 789456, 'postgres:5432', 'shoe_storage'))

def insert_artificial_data_to_db():
    db_wrp = DbWrap()
    db_wrp.exec_print_stmt("SELECT * FROM shoes_table;")
    
# TODO: Generowanie przychodzących oraz odchodzących produktów
class ShoeWarehouse:
    def __init__(self) -> None:
        pass
    


   
# TODO: Generowanie paragonów i zwrotów
class ShoeShop:
    def __init__(self) -> None:
        pass


if __name__ == '__main__':
    insert_artificial_data_to_db()
    




