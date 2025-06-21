import yaml
from .logger import get_logger
from PIL import Image
from werkzeug.utils import secure_filename
import os,string,random

logger = get_logger()  # Logger'ı modül adına göre başlat

def load_yaml(file_path='credentials.yaml') -> dict:
    """_summary_

        aldığı file_path e göre yaml dosyasını yükleyip içeriğini döndürür.
        
    Args:
        file_path (str, optional): içeriği döndürülecek olan yaml dosyasının pathi

    Returns:
        dict: _description_
    """
    try:
        with open(file_path, encoding="utf-8") as file:
            data = yaml.safe_load(file)
            logger.info(f"YAML dosyası başarıyla yüklendi: {file_path}")
            return data
    except FileNotFoundError:
        logger.error(f"YAML dosyası bulunamadı: {file_path}")
    except yaml.YAMLError as e:
        logger.error(f"YAML ayrıştırma hatası: {e}")
    except Exception as e:
        logger.exception(f"YAML yükleme sırasında beklenmeyen bir hata oluştu: {e}")
    return None  # Hata durumunda None döner



def dosya_gecerlimi(file, max_size_mb=2):
    """
    Verilen dosyanın JPG veya PNG olup olmadığını ve dosya boyutunun max_size_mb MB'den
    büyük olmadığını kontrol eder.
    
    :param file: Flask FileStorage nesnesi
    :param max_size_mb: Maksimum dosya boyutu (MB cinsinden)
    :return: True (geçerli) veya False (geçersiz)
    """
    if not file or file.filename == '':
        logger.error('Resim boş geldi.')
        return False

    # Dosya boyutu kontrolü (seek ve tell ile)
    file.seek(0, 2)  # Dosyanın sonuna git
    boyut = file.tell()  # Dosya boyutunu al (byte)
    file.seek(0)  # Dosya başına dön

    if boyut > max_size_mb * 1024 * 1024:
        logger.error('Resim boyutu çok yüksek')
        return False

    try:
        img = Image.open(file)
        if img.format not in ('JPEG', 'PNG'):
            logger.error(f'Resim uzantısı yanlış. yüklenmek isteyen dosya uzantısı : {img.format}')
            return False
    except Exception:
        return False

    file.seek(0)  # Dosya konumunu başa al ki sonra kaydedilsin
    logger.info('Geçerli resim dosyası')
    return True


def resim_yukle(file, max_size_mb=2):
    if dosya_gecerlimi(file,max_size_mb):
        filename = secure_filename(file.filename)
        upload_path = os.path.join('static/anketImages',filename)
        file.save(upload_path)
        logger.info('Resim başarıyla yüklendi')
        return True
    else: 
        logger.error('Resim yüklenmesinde hata')
        return False



def generate_unique_id():
    # Rastgele harf ve rakamlardan oluşan uzun bir string üretir
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(100))

