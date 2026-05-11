import os
import sys
from app import app, db
from models import SubCriterion
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_database():
    """
    SubCriterion tablosuna detail_weight alanını ekleyen ve varsayılan değerlerini ayarlayan betik.
    Bu betik aşağıdaki işlemleri yapar:
    1. Veritabanındaki mevcut sub_criterion tablosunu kontrol eder
    2. detail_weight sütunu zaten mevcutsa, işlem yapılmaz
    3. Sütun mevcut değilse, detail_weight sütunu eklenir ve varsayılan değerleri 1.0 olarak ayarlanır
    4. İşlem başarılı olursa, bir onay mesajı yazdırır
    """
    try:
        with app.app_context():
            # Sütun var mı yok mu kontrol et
            inspector = db.inspect(db.engine)
            columns = [column['name'] for column in inspector.get_columns('sub_criterion')]
            
            if 'detail_weight' in columns:
                logger.info("detail_weight sütunu zaten mevcut, hiçbir değişiklik yapılmadı.")
                return
            
            # ALTER TABLE komutu ile sütun ekle
            sql = text("ALTER TABLE sub_criterion ADD COLUMN detail_weight NUMERIC(8,6) DEFAULT 1.0")
            db.session.execute(sql)
            
            # Değişiklikleri kaydet
            db.session.commit()
            
            # Başarılı olduğunu doğrula
            sub_criteria = SubCriterion.query.all()
            for sub in sub_criteria:
                logger.info(f"Alt kriter #{sub.id} {sub.name}, detail_weight={sub.detail_weight}")
            
            logger.info("Veritabanı güncelleme işlemi başarıyla tamamlandı!")
            logger.info(f"Toplam {len(sub_criteria)} alt kriter güncellendi.")
    
    except Exception as e:
        logger.error(f"Veritabanı güncellenirken bir hata oluştu: {str(e)}")
        db.session.rollback()

if __name__ == "__main__":
    update_database()