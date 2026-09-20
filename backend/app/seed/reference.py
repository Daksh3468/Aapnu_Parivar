import logging
from sqlalchemy.orm import Session
from app.core.db import engine, Base, SessionLocal
from app.models.district import District
from app.models.pincode import PincodeMaster

logger = logging.getLogger("aapnu_parivar")

GUJARAT_DISTRICTS = [
    (1, "Ahmedabad"),
    (2, "Amreli"),
    (3, "Anand"),
    (4, "Aravalli"),
    (5, "Banaskantha"),
    (6, "Bharuch"),
    (7, "Bhavnagar"),
    (8, "Botad"),
    (9, "Chhota Udaipur"),
    (10, "Dahod"),
    (11, "Dang"),
    (12, "Devbhumi Dwarka"),
    (13, "Gandhinagar"),
    (14, "Gir Somnath"),
    (15, "Jamnagar"),
    (16, "Junagadh"),
    (17, "Kheda"),
    (18, "Kutch"),
    (19, "Mahisagar"),
    (20, "Mehsana"),
    (21, "Morbi"),
    (22, "Narmada"),
    (23, "Navsari"),
    (24, "Panchmahal"),
    (25, "Patan"),
    (26, "Porbandar"),
    (27, "Rajkot"),
    (28, "Sabarkantha"),
    (29, "Surat"),
    (30, "Surendranagar"),
    (31, "Tapi"),
    (32, "Vadodara"),
    (33, "Valsad"),
]

# Sample realistic pincodes mapping per district
SAMPLE_PINCODES = [
    ("380001", 1, "Ahmedabad City", "Bhadra / Ellisbridge"),
    ("380015", 1, "Ahmedabad West", "Satellite / Vastrapur"),
    ("365601", 2, "Amreli Central", "Amreli Main"),
    ("388001", 3, "Anand City", "Anand Central"),
    ("383315", 4, "Modasa", "Modasa Main"),
    ("385001", 5, "Palanpur", "Palanpur Main"),
    ("392001", 6, "Bharuch Central", "Bharuch Main"),
    ("364001", 7, "Bhavnagar City", "Bhavnagar Main"),
    ("364710", 8, "Botad City", "Botad Central"),
    ("391165", 9, "Chhota Udaipur", "Town Area"),
    ("389151", 10, "Dahod Central", "Dahod Main"),
    ("394710", 11, "Ahwa", "Ahwa Main"),
    ("361335", 12, "Dwarka", "Dwarka Town"),
    ("382010", 13, "Gandhinagar", "Sector 11"),
    ("362265", 14, "Veraval", "Somnath Temple Area"),
    ("361001", 15, "Jamnagar", "Jamnagar Central"),
    ("362001", 16, "Junagadh", "Junagadh City"),
    ("387001", 17, "Nadiad", "Nadiad Main"),
    ("370001", 18, "Bhuj", "Bhuj Town"),
    ("389230", 19, "Lunawada", "Lunawada Main"),
    ("384001", 20, "Mehsana", "Mehsana Main"),
    ("363641", 21, "Morbi", "Morbi Main"),
    ("393145", 22, "Rajpipla", "Rajpipla Main"),
    ("396445", 23, "Navsari", "Navsari Town"),
    ("389001", 24, "Godhra", "Godhra Main"),
    ("384265", 25, "Patan", "Patan Main"),
    ("360575", 26, "Porbandar", "Porbandar Town"),
    ("360001", 27, "Rajkot", "Rajkot Central"),
    ("383001", 28, "Himmatnagar", "Himmatnagar Main"),
    ("395003", 29, "Surat", "Varachha / Adajan"),
    ("363001", 30, "Surendranagar", "Surendranagar Main"),
    ("394650", 31, "Vyara", "Vyara Main"),
    ("390001", 32, "Vadodara", "Alkapuri / Raopura"),
    ("396001", 33, "Valsad", "Valsad Central"),
]


def init_db_and_seed_reference():
    """Initialize database tables and seed Gujarat 33 Districts & Pincodes."""
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    try:
        # Seed Districts
        district_count = db.query(District).count()
        if district_count == 0:
            for code, name in GUJARAT_DISTRICTS:
                db.add(District(district_code=code, name=name))
            db.commit()
            logger.info("Successfully seeded 33 Gujarat Districts.")

        # Seed Pincodes
        pincode_count = db.query(PincodeMaster).count()
        if pincode_count == 0:
            for pin, dcode, taluka, area in SAMPLE_PINCODES:
                db.add(PincodeMaster(pincode=pin, district_code=dcode, taluka=taluka, area_name=area))
            db.commit()
            logger.info("Successfully seeded master pincodes.")
    finally:
        db.close()


if __name__ == "__main__":
    init_db_and_seed_reference()
