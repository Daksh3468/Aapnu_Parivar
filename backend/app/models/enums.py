import enum


class GenderEnum(str, enum.Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"


class MaritalStatusEnum(str, enum.Enum):
    UNMARRIED = "UNMARRIED"
    MARRIED = "MARRIED"
    WIDOWED = "WIDOWED"
    DIVORCED = "DIVORCED"
    SEPARATED = "SEPARATED"


class VerificationStatusEnum(str, enum.Enum):
    UNVERIFIED = "UNVERIFIED"
    VERIFIED = "VERIFIED"
    FAILED = "FAILED"


class SocialCategoryEnum(str, enum.Enum):
    GENERAL = "GENERAL"
    SC = "SC"
    ST = "ST"
    SEBC = "SEBC"
    OBC = "OBC"
    EWS = "EWS"


class EducationLevelEnum(str, enum.Enum):
    NONE = "NONE"
    PRIMARY = "PRIMARY"
    SECONDARY = "SECONDARY"
    HIGHER_SECONDARY = "HIGHER_SECONDARY"
    GRADUATE = "GRADUATE"
    POST_GRADUATE = "POST_GRADUATE"
    DIPLOMA_ITI = "DIPLOMA_ITI"


class OccupationTypeEnum(str, enum.Enum):
    FARMER = "FARMER"
    LABOUR = "LABOUR"
    ARTISAN = "ARTISAN"
    SELF_EMPLOYED = "SELF_EMPLOYED"
    SALARIED = "SALARIED"
    HOMEMAKER = "HOMEMAKER"
    UNEMPLOYED = "UNEMPLOYED"
    RETIRED = "RETIRED"
    OTHER = "OTHER"


class FamilyStatusEnum(str, enum.Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    VERIFIED = "VERIFIED"
    NEEDS_CORRECTION = "NEEDS_CORRECTION"
    SUSPENDED = "SUSPENDED"
    CLOSED = "CLOSED"


class RationCardTypeEnum(str, enum.Enum):
    AAY = "AAY"  # Antyodaya Anna Yojana
    PHH = "PHH"  # Priority Household
    NON_NFSA = "NON_NFSA"
    NONE = "NONE"


class IncomeBandEnum(str, enum.Enum):
    LT_1L = "LT_1L"          # Less than ₹1 Lakh
    BAND_1L_2_5L = "1L_2_5L"  # ₹1L - ₹2.5L
    BAND_2_5L_5L = "2_5L_5L"  # ₹2.5L - ₹5L
    BAND_5L_8L = "5L_8L text"  # ₹5L - ₹8L
    GT_8L = "GT_8L"          # Greater than ₹8L


class HouseTypeEnum(str, enum.Enum):
    KUCCHA = "KUCCHA"
    SEMI_PUCCA = "SEMI_PUCCA"
    PUCCA = "PUCCA"
    NONE = "NONE"


class RoleInFamilyEnum(str, enum.Enum):
    HEAD = "HEAD"
    ADULT = "ADULT"
    DEPENDENT = "DEPENDENT"


class RelationToHeadEnum(str, enum.Enum):
    SELF = "SELF"
    SPOUSE = "SPOUSE"
    SON = "SON"
    DAUGHTER = "DAUGHTER"
    FATHER = "FATHER"
    MOTHER = "MOTHER"
    BROTHER = "BROTHER"
    SISTER = "SISTER"
    DAUGHTER_IN_LAW = "DAUGHTER_IN_LAW"
    SON_IN_LAW = "SON_IN_LAW"
    GRANDCHILD = "GRANDCHILD"
    OTHER = "OTHER"


class MembershipReasonEnum(str, enum.Enum):
    REGISTRATION = "REGISTRATION"
    BIRTH = "BIRTH"
    MARRIAGE = "MARRIAGE"
    SPLIT = "SPLIT"
    MERGE = "MERGE"
    MIGRATION = "MIGRATION"
    JOIN_APPROVED = "JOIN_APPROVED"
    DEATH = "DEATH"
    CORRECTION = "CORRECTION"


class RegisteredByEnum(str, enum.Enum):
    SELF = "SELF"
    OFFICER = "OFFICER"


class UserRoleEnum(str, enum.Enum):
    CITIZEN_HEAD = "CITIZEN_HEAD"
    CITIZEN_MEMBER = "CITIZEN_MEMBER"
    FIELD_OFFICER = "FIELD_OFFICER"
    DISTRICT_OFFICER = "DISTRICT_OFFICER"
    STATE_ADMIN = "STATE_ADMIN"
    AUDITOR = "AUDITOR"


class UserAccountStatusEnum(str, enum.Enum):
    ACTIVE = "ACTIVE"
    LOCKED = "LOCKED"
    DISABLED = "DISABLED"
    PENDING_CLAIM = "PENDING_CLAIM"


class JurisdictionScopeEnum(str, enum.Enum):
    STATE = "STATE"
    DISTRICT = "DISTRICT"
    PINCODE = "PINCODE"


class DocumentTypeEnum(str, enum.Enum):
    INCOME_CERTIFICATE = "INCOME_CERTIFICATE"
    CASTE_CERTIFICATE = "CASTE_CERTIFICATE"
    LAND_RECORD = "LAND_RECORD"
    DISABILITY_CERTIFICATE = "DISABILITY_CERTIFICATE"
    RATION_CARD = "RATION_CARD"
    DOMICILE_CERTIFICATE = "DOMICILE_CERTIFICATE"
    AADHAAR_CARD = "AADHAAR_CARD"
    OTHER = "OTHER"


class DocumentStatusEnum(str, enum.Enum):
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class EligibilityStatusEnum(str, enum.Enum):
    AUTO_ELIGIBLE = "AUTO_ELIGIBLE"
    AUTO_INELIGIBLE = "AUTO_INELIGIBLE"
    DOCS_NEEDED = "DOCS_NEEDED"
    OFFICER_APPROVED = "OFFICER_APPROVED"
    OFFICER_REJECTED = "OFFICER_REJECTED"


class ApplicationStatusEnum(str, enum.Enum):
    SUBMITTED = "SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED = "APPROVED"
    DISBURSED = "DISBURSED"
    REJECTED = "REJECTED"


class LifeEventTypeEnum(str, enum.Enum):
    BIRTH = "BIRTH"
    DEATH = "DEATH"
    MARRIAGE_OUT = "MARRIAGE_OUT"
    MARRIAGE_IN = "MARRIAGE_IN"
    HOUSEHOLD_SPLIT = "HOUSEHOLD_SPLIT"
    ADDRESS_CHANGE = "ADDRESS_CHANGE"


class SplitStatusEnum(str, enum.Enum):
    AUTOMATICALLY_APPROVED = "AUTOMATICALLY_APPROVED"
    PENDING_OFFICER_REVIEW = "PENDING_OFFICER_REVIEW"
    OFFICER_APPROVED = "OFFICER_APPROVED"
    OFFICER_REJECTED = "OFFICER_REJECTED"

