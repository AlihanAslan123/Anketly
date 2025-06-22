from sqlalchemy import Engine,create_engine,text
from sqlalchemy.exc import SQLAlchemyError
import yaml
from .file_utils import load_yaml,generate_unique_id
from .logger import get_logger
from flask import Flask
from flask_bcrypt import Bcrypt
import pyodbc
from flask_login import current_user
from datetime import datetime


logger = get_logger()


def get_db_engine() -> Engine:
    """
    Veritabanına bağlanarak bir SQLAlchemy Engine nesnesi döndürür.
    """

    try:
        logger.info("Veritabanı bağlantı bilgileri yükleniyor...")
        credentials = load_yaml()

        hostname = credentials.get("HOSTNAME")
        db_name = credentials.get("DB_NAME")
        driver = credentials.get("DRIVER")
        username = credentials.get("USERNAME")
        password = credentials.get("PASSWORD")

        if not all([hostname, db_name, driver, username, password]):
            raise ValueError("Bazı veritabanı bağlantı bilgileri eksik!")

        connection_url = f"mssql+pyodbc://{username}:{password}@{hostname}/{db_name}?driver={driver}"
        logger.info("Veritabanı bağlantısı oluşturuluyor...")
        engine = create_engine(url=connection_url)
        logger.info("Veritabanı bağlantısı başarıyla oluşturuldu.")

        return engine
    
    except Exception as e:
        logger.exception("Veritabanı bağlantısı oluşturulurken bir hata oluştu.")
        raise

engine = get_db_engine()


def register_user(app:Flask, email: str, password: str, cinsiyet: str) -> bool:
    """
    Bu fonksiyon kullanıcıdan alınan verileri güvenli bir şekilde `tbl_users` tablosuna kayıt ekler.

    Parametreler:
        app : flask app nesnesi
        email (str): Kullanıcının e-posta adresi.
        password (str): Kullanıcının düz şifresi (fonksiyon içinde hash'lenir).
        cinsiyet (str): Kullanıcının cinsiyeti.

    Döndürür:
        bool - Eklenme durumuna göre bool değer döndürür.
    """

    bcrypt = Bcrypt(app)
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    query = text("""
        INSERT INTO tbl_users ( email, password, cinsiyet)
        VALUES ( :email, :password, :cinsiyet)
    """)

    try:
        with engine.connect() as conn:
            conn.execute(query, {
                'email': email,
                'password': hashed_password,
                'cinsiyet': cinsiyet
            })
            conn.commit()
        return True

    except SQLAlchemyError as e:
        # Hata loglanabilir veya raise edilebilir
        print(f"Veritabanı hatası: {e}")
        return False
    


def get_categorys(engine:Engine):
    '''
    veritabanından kategorileri getirir.
    '''
    with engine.connect() as conn:
        result = conn.execute(text('SELECT * FROM tbl_Kategori;')).tuples()
        kategoriler = list(result)
        
    return kategoriler



def insert_anket(anket_adi: str, anket_aciklamasi: str, kategori_id: int, resim, yayin_tipi: str, sorular: list):
    
    '''
    Kullanıcının oluşturduğu anketi veritabanına ekler.
    '''
    
    
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    picture_name = getattr(resim, 'filename', None)

    insert_anket_query = text("""
        INSERT INTO tbl_anket (kategori_id, title, picture, description, created_at, is_private, kullanici_id)
        OUTPUT INSERTED.id
        VALUES (:kategori_id, :title, :picture, :description, :created_at, :is_private, :kullanici_id)
    """)

    insert_soru_query = text("""
        INSERT INTO tbl_sorular (anket_id, soru_text, cevap_tipi, soru_numarasi)
        OUTPUT INSERTED.id
        VALUES (:anket_id, :soru_text, :cevap_tipi, :soru_numarasi)
    """)

    insert_secenek_query = text("""
        INSERT INTO tbl_secenekler (soru_id, secenek_text)
        VALUES (:soru_id, :secenek_text)
    """)

    with engine.begin() as conn:
        try:
            result = conn.execute(insert_anket_query, {
                'kategori_id': kategori_id,
                'title': anket_adi,
                'picture': picture_name,
                'description': anket_aciklamasi,
                'created_at': now,
                'is_private': 1 if yayin_tipi == 'private' else 0,
                'kullanici_id': current_user.id
            })
            anket_id = result.scalar()
            logger.info('tbl_anket başarı ile eklendi.')
        except Exception as e:
            logger.error(f'tbl_anket ekleme sırasında hata {e}')

        for i, soru in enumerate(sorular):
            soru_text = soru['soru']
            secenekler = soru['secenekler']
            cevap_tipi = 'Metin' if not secenekler else 'Şıklar'
            soru_numarasi = i + 1

            try:
                result = conn.execute(insert_soru_query, {
                    'anket_id': anket_id,
                    'soru_text': soru_text,
                    'cevap_tipi': cevap_tipi,
                    'soru_numarasi': soru_numarasi
                })
                logger.info('tbl_sorulara eklenme başarılı')
            except Exception as e:
                logger.error(f'tbl_sorular eklenme sırasında hata {e}')
                
            soru_id = result.scalar()

            if cevap_tipi == 'Şıklar':
                for secenek in secenekler:
                    try:
                        conn.execute(insert_secenek_query, {
                            'soru_id': soru_id,
                            'secenek_text': secenek
                        })
                        logger.info('tbl_seceneklere secenek eklendi.')
                    except Exception as e:
                        logger.error(f'tbl_seceneklere eklenme sırasında hata {e}')
    
        if yayin_tipi == 'private':
            uniqid=generate_unique_id()
            insert_private_query = text(
                '''
                insert into private_anket(anket_id,anket_link) values (:anket_id, :anket_link)
                '''
            )
            try:
                conn.execute(insert_private_query, {
                    'anket_id': anket_id,
                    'anket_link':uniqid
                })
                logger.info('private anket eklendi.')
            except Exception as e:
                logger.error(f'private anket eklenme sırasında hata {e}')
                
        
            
        
def sum_anket():
    '''
    kullanıcının oluşturduğu ve katıldığı toplam anket sayısını döndürür.
    '''
    query_created_anket = text(
        '''
        Select count(*) from tbl_anket where kullanici_id = :kullanici_id
        '''
    )
    query_solved_anket = text('''
        SELECT count(*) from tbl_kullanici_anketleri where kullanici_id = :kullanici_id
    '''
    )
    
    with engine.connect() as conn:
        result = conn.execute(query_created_anket,{'kullanici_id':current_user.id}).fetchone()[0]
    with engine.connect() as conn:
        result2 = conn.execute(query_solved_anket,{'kullanici_id':current_user.id}).fetchone()[0]
    
    return result,result2
        
    
    
def get_all_anket():
    with engine.begin() as conn:
        result = conn.execute(text('SELECT * FROM tbl_anket where is_private = 0')).fetchall()
    return result