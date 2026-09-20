import random
import logging
import uuid
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from app.core.db import engine, Base, SessionLocal
from app.models.district import District
from app.models.pincode import PincodeMaster
from app.models.family import Family
from app.models.person import Person
from app.models.membership import FamilyMembership
from app.models.address import Address
from app.models.scheme import Scheme
from app.models.application import SchemeApplication
from app.models.document import Document
from app.models.enums import (
    FamilyStatusEnum, GenderEnum, MaritalStatusEnum,
    SocialCategoryEnum, RationCardTypeEnum, IncomeBandEnum, HouseTypeEnum, OccupationTypeEnum,
    RelationToHeadEnum, RoleInFamilyEnum, MembershipReasonEnum,
    VerificationStatusEnum, ApplicationStatusEnum, DocumentTypeEnum, DocumentStatusEnum
)
from app.utils.family_id import new_family_id

logger = logging.getLogger("aapnu_parivar")

FIRST_NAMES_MALE = ["Rameshbhai", "Suresh", "Rajesh", "Jignesh", "Vijay", "Nilesh", "Paresh", "Bhavik", "Haresh", "Kishore", "Amit", "Dhaval", "Chetan", "Deepak", "Jayesh"]
FIRST_NAMES_FEMALE = ["Savitaben", "Kavitaben", "Nipaben", "Hetalthi", "Pujaben", "Dahiben", "Rekhaben", "Kinjal", "Bhavanaben", "Geetaben", "Anitaben", "Dharaben"]
LAST_NAMES = ["Patel", "Shah", "Joshi", "Parmar", "Solanki", "Rathod", "Chavda", "Vaghela", "Makwana", "Thakor", "Desai", "Gohil", "Prajapati", "Mehta", "Bhatt"]

VILLAGES_TALUKAS = [
    ("Ahmedabad", "Bhadra", 1, "380001"),
    ("Satellite", "Vastrapur", 1, "380015"),
    ("Amreli", "Amreli Central", 2, "365601"),
    ("Anand", "Anand City", 3, "388001"),
    ("Modasa", "Modasa Main", 4, "383315"),
    ("Palanpur", "Banaskantha Main", 5, "385001"),
    ("Bharuch", "Bharuch Central", 6, "392001"),
    ("Bhavnagar", "Bhavnagar City", 7, "364001"),
    ("Botad", "Botad City", 8, "364710"),
    ("Dahod", "Dahod Central", 10, "389151"),
    ("Gandhinagar", "Sector 11", 13, "382010"),
    ("Veraval", "Somnath Area", 14, "362265"),
    ("Jamnagar", "Jamnagar Central", 15, "361001"),
    ("Junagadh", "Junagadh City", 16, "362001"),
    ("Bhuj", "Kutch Main", 18, "370001"),
    ("Mehsana", "Mehsana Central", 20, "384001"),
    ("Rajkot", "Rajkot Central", 27, "360001"),
    ("Surat", "Varachha", 29, "395003"),
    ("Vadodara", "Alkapuri", 32, "390001"),
    ("Valsad", "Valsad Central", 33, "396001"),
]

def generate_synthetic_dataset(num_families: int = 150):
    """Generate a realistic synthetic dataset of Gujarat families, memberships, applications, and documents."""
    db: Session = SessionLocal()
    try:
        logger.info(f"Starting synthetic dataset generation for {num_families} families...")
        schemes = db.query(Scheme).all()

        for i in range(num_families):
            d_name, taluka, d_code, pin = random.choice(VILLAGES_TALUKAS)

            # Generate Address
            addr = Address(
                line1=f"House #{random.randint(1, 400)}, Main Road",
                village_or_town=d_name,
                taluka=taluka,
                district_code=d_code,
                pincode=pin,
            )
            db.add(addr)
            db.commit()
            db.refresh(addr)

            # Generate Family ID
            family_id = new_family_id(d_code, 2026)

            ration_type = random.choice([RationCardTypeEnum.PHH, RationCardTypeEnum.AAY, RationCardTypeEnum.NON_NFSA])
            inc_band = random.choice([IncomeBandEnum.LT_1L, IncomeBandEnum.BAND_1L_2_5L, IncomeBandEnum.BAND_2_5L_5L])

            # Create Family Record
            fam = Family(
                family_id=family_id,
                address_id=addr.address_id,
                ration_card_type=ration_type,
                ration_card_number=f"GJ{d_code:02d}{random.randint(10000000, 99999999)}",
                income_band=inc_band,
                land_holding_acres=round(random.uniform(0.0, 8.5), 1),
                house_type=random.choice([HouseTypeEnum.PUCCA, HouseTypeEnum.SEMI_PUCCA, HouseTypeEnum.KUCCHA]),
                house_owned=random.choice([True, True, False]),
                has_lpg_connection=random.choice([True, True, False]),
                primary_occupation=random.choice([OccupationTypeEnum.FARMER, OccupationTypeEnum.LABOUR, OccupationTypeEnum.SALARIED]),
                status=FamilyStatusEnum.VERIFIED,
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 300)),
            )
            db.add(fam)
            db.commit()
            db.refresh(fam)

            head_surname = random.choice(LAST_NAMES)
            head_first = random.choice(FIRST_NAMES_MALE)
            head_name = f"{head_first} {head_surname}"

            # Create Head Person Record
            head_dob = date(random.randint(1965, 1985), random.randint(1, 12), random.randint(1, 28))
            head_person = Person(
                full_name=head_name,
                dob=head_dob,
                gender=GenderEnum.MALE,
                marital_status=MaritalStatusEnum.MARRIED,
                mobile=f"98765{random.randint(10000, 99999)}",
                aadhaar_last4=f"{random.randint(1000, 9999)}",
                verification_status=VerificationStatusEnum.VERIFIED,
                verified_at=datetime.utcnow(),
                social_category=random.choice([SocialCategoryEnum.GENERAL, SocialCategoryEnum.SEBC, SocialCategoryEnum.SC, SocialCategoryEnum.ST]),
                education_level="GRADUATE",
                occupation_type=OccupationTypeEnum.FARMER,
                has_bank_account=True,
            )
            db.add(head_person)
            db.commit()
            db.refresh(head_person)

            # Create Head FamilyMembership Record
            head_mem = FamilyMembership(
                person_id=head_person.person_id,
                family_id=fam.family_id,
                role_in_family=RoleInFamilyEnum.HEAD,
                relation_to_head=RelationToHeadEnum.SELF,
                start_date=date.today() - timedelta(days=365),
                start_reason=MembershipReasonEnum.REGISTRATION,
            )
            db.add(head_mem)

            # Spouse Member
            spouse_name = f"{random.choice(FIRST_NAMES_FEMALE)} {head_surname}"
            spouse_dob = date(random.randint(1968, 1988), random.randint(1, 12), random.randint(1, 28))
            spouse_person = Person(
                full_name=spouse_name,
                dob=spouse_dob,
                gender=GenderEnum.FEMALE,
                marital_status=MaritalStatusEnum.MARRIED,
                mobile=f"98765{random.randint(10000, 99999)}",
                aadhaar_last4=f"{random.randint(1000, 9999)}",
                verification_status=VerificationStatusEnum.VERIFIED,
                verified_at=datetime.utcnow(),
                social_category=head_person.social_category,
                education_level="SECONDARY",
                occupation_type=OccupationTypeEnum.HOMEMAKER,
                has_bank_account=True,
            )
            db.add(spouse_person)
            db.commit()
            db.refresh(spouse_person)

            spouse_mem = FamilyMembership(
                person_id=spouse_person.person_id,
                family_id=fam.family_id,
                role_in_family=RoleInFamilyEnum.ADULT,
                relation_to_head=RelationToHeadEnum.SPOUSE,
                start_date=date.today() - timedelta(days=365),
                start_reason=MembershipReasonEnum.REGISTRATION,
            )
            db.add(spouse_mem)

            db.commit()

            # Add Verified Documents to Vault
            doc_income = Document(
                family_id=fam.family_id,
                document_type=DocumentTypeEnum.INCOME_CERTIFICATE,
                document_number=f"INC-{d_code:02d}-{random.randint(100000, 999999)}",
                issuing_authority="Mamlatdar Office",
                issue_date=datetime.utcnow() - timedelta(days=120),
                status=DocumentStatusEnum.VERIFIED,
                file_path=f"/vault/docs/inc_{fam.family_id}.pdf",
            )
            db.add(doc_income)
            db.commit()

            # Add Applications if schemes available
            if schemes:
                for s in random.sample(schemes, k=min(2, len(schemes))):
                    app_status = random.choice([
                        ApplicationStatusEnum.DISBURSED, ApplicationStatusEnum.APPROVED,
                        ApplicationStatusEnum.UNDER_REVIEW, ApplicationStatusEnum.SUBMITTED
                    ])
                    app = SchemeApplication(
                        family_id=fam.family_id,
                        scheme_id=s.scheme_id,
                        applicant_person_id=head_person.person_id,
                        applicant_token=uuid.uuid4().hex[:16],
                        source_system=s.source_system or "Mock Gujarat Gateway",
                        external_reference=f"REF-{fam.family_id}-{random.randint(1000, 9999)}",
                        official_url=s.official_url or "https://gujarat.gov.in",
                        status=app_status,
                        officer_feedback=f"Synthetic check completed. Status: {app_status.value}",
                        submitted_at=datetime.utcnow() - timedelta(days=random.randint(1, 180)),
                    )
                    db.add(app)
                db.commit()

        logger.info(f"Synthetic dataset generation complete! Seeded {num_families} families.")

    finally:
        db.close()

if __name__ == "__main__":
    generate_synthetic_dataset(150)
