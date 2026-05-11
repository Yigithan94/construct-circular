import os
import sys
import logging
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import inspect, text
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Loglama yapılandırması
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def update_database():
    """KeyPerformanceIndicator ve KPIDocument modellerine AI değerlendirme alanları ekler"""
    try:
        # Flask uygulamasını oluştur ve yapılandır
        app = Flask(__name__)
        
        # Veritabanı yapılandırması
        app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
        app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
            "pool_recycle": 300,
            "pool_pre_ping": True,
        }
        
        # SQLAlchemy nesnesini oluştur
        class Base(DeclarativeBase):
            pass
        
        db = SQLAlchemy(model_class=Base)
        db.init_app(app)
        
        with app.app_context():
            logger.info("Veritabanı güncellemesi başlatılıyor...")
            
            # Mevcut tabloları kontrol et
            conn = db.engine.connect()
            inspector = inspect(db.engine)
            
            # KeyPerformanceIndicator tablosuna yeni sütunlar ekle
            if 'key_performance_indicator' in inspector.get_table_names():
                # AI değerlendirme kriterleri sütunu
                if 'ai_evaluation_criteria' not in [col['name'] for col in inspector.get_columns('key_performance_indicator')]:
                    logger.info("'ai_evaluation_criteria' sütunu ekleniyor...")
                    conn.execute(text("ALTER TABLE key_performance_indicator ADD COLUMN ai_evaluation_criteria TEXT;"))
                    
                # AI değerlendirme kullanım bayrağı sütunu
                if 'use_ai_evaluation' not in [col['name'] for col in inspector.get_columns('key_performance_indicator')]:
                    logger.info("'use_ai_evaluation' sütunu ekleniyor...")
                    conn.execute(text("ALTER TABLE key_performance_indicator ADD COLUMN use_ai_evaluation BOOLEAN DEFAULT FALSE;"))
                    
                logger.info("KeyPerformanceIndicator tablosu güncellendi.")
            else:
                logger.warning("'key_performance_indicator' tablosu bulunamadı.")
            
            # KPIDocument tablosuna yeni sütunlar ekle
            if 'kpi_document' in inspector.get_table_names():
                # AI değerlendirme bayrağı sütunu
                if 'ai_evaluated' not in [col['name'] for col in inspector.get_columns('kpi_document')]:
                    logger.info("'ai_evaluated' sütunu ekleniyor...")
                    conn.execute(text("ALTER TABLE kpi_document ADD COLUMN ai_evaluated BOOLEAN DEFAULT FALSE;"))
                
                # AI puanı sütunu
                if 'ai_score' not in [col['name'] for col in inspector.get_columns('kpi_document')]:
                    logger.info("'ai_score' sütunu ekleniyor...")
                    conn.execute(text("ALTER TABLE kpi_document ADD COLUMN ai_score INTEGER;"))
                
                # AI açıklaması sütunu
                if 'ai_explanation' not in [col['name'] for col in inspector.get_columns('kpi_document')]:
                    logger.info("'ai_explanation' sütunu ekleniyor...")
                    conn.execute(text("ALTER TABLE kpi_document ADD COLUMN ai_explanation TEXT;"))
                
                logger.info("KPIDocument tablosu güncellendi.")
            else:
                logger.warning("'kpi_document' tablosu bulunamadı.")
            
            # İşlemler tamamlandı, değişiklikleri kaydet
            conn.close()
            logger.info("Veritabanı güncellemesi tamamlandı.")
            
    except Exception as e:
        logger.error(f"Veritabanı güncellemesi sırasında hata oluştu: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    if update_database():
        logger.info("Veritabanı başarıyla güncellendi.")
        sys.exit(0)
    else:
        logger.error("Veritabanı güncellenemedi.")
        sys.exit(1)