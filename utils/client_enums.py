from enum import Enum
import hashlib
import colorsys
class Company(Enum):
    ATD = "American Tire Distributors Inc"
    VERTISYSTEMS = "Vertisystem Inc"
    NAT_GRID = "National Grid USA Service Company Inc"
    SOUL_CYCLE = "SoulCycle Inc"
    TRINET = "TriNet USA Inc"
    HFT = "Harbor Freight Tools USA Inc"
    ICON = "Citizens Icon Holdings LLC"
    LAZARD = "Lazard Freres & Co LLC"
    VERTEXONE = "VERTEXONE SOFTWARE LLC"
    YMCA = "National Council of Young Men's Christian Association of the USA of America"
    EBOS = "Symbion Pty Ltd (EBOS)"
    HARRIS_FARM = "Harris Farm Markets Pty Ltd"
    GLOBUS = "Globus Medical Inc"
    DELOITTE = "Deloitte Consulting India Private Limited"
    FREEMAN = "Freeman Corporation"
    SWIFT = "Swift Beef Company"
    GCG = "Goddard Catering Group"
    SEPHORA = "Sephora"
    DEVFI = "Devfi Inc"
    LACTALIS = "LACTALIS AUSTRALIA PTY LTD"
    ENERSYS = "EnerSys Delaware Inc"
    LENOVO = "Lenovo PC HK LTD"
    HUMMING_BIRD = "Humming Bird Education Limited"
    CHEP = "CHEP USA Inc"
    LEASELOCK = "LeaseLock Inc"
    MOURITECH = "MOURI Tech Limited"
    MOURITECH_LLC ="MOURI Tech LLC" 
    ILC_DOVER = "ILC Dover"
    NWN = "NWN Corporation"
    RITCHIE = "Ritchie Bros. Auctioneers Inc"
    INGERSOLL_RAND = "Ingersoll Rand"
    BINGO = "Bingo Industries"
    ESTABLISHMENT_LABS = "Establishment Labs SA"
    ONESTREAM = "OneStream Software LLC"
    EQUINOX = "Equinox Holdings Inc"
    HUDSON = "Hudson Advisors L.P"
    STRADA = "Strada U.S. Payroll LLC"
    SIPEF = "SIPEF Singapore Pte Ltd"
    SVI = "Storage Vault Canada Inc"
    SUNTEX = "Suntex Marinas LLC"
    SAMSARA = "Samsara Inc"
    SIGNIA = "Signia Aerospace"
    ATNI = "ATN International Services LLC"
    ANICA = "Anica Inc"
    ELF = "ELF Cosmetics Inc"
    TOYOTA = "Toyota Canada Inc"
    REGAL = "Regal Rexnord Corporation"
    UWF = "University of Wisconsin Foundation"
    DELEK = "Delek US Holdings Inc"


PALETTE = [
    "#9FB7E5",
    "#8FC9C2",
    "#E0AFC7",
    "#E5B18A",
    "#B8A9DE",
    "#D6A3A3",
    "#E0A07A",
    "#C8D48A",
    "#E2A18F",
    "#8FAADC",
    "#7F9CCB",
    "#9FBF8F",
    "#8FB8A1",
    "#7FBDB8",
    "#8CBFCF",
    "#A79BCF",
    "#9B8EC2",
    "#C2A27F",
    "#B89B7A",
    "#B0B0B0",
    "#9E9E9E",
    "#C97A7A",
    "#D9A36A",
    "#E0B07A",
    "#7FAF8F",
    "#7A95C7",
    "#6F8FBE",
    "#9A8BC7",
    "#8F82BE",
    "#CFAF6E",
    "#B7A86A",
    "#AFC38A",
    "#8FB28F",
    "#C38FA3",
    "#B58FAF",
    "#AFA38F",
    "#C1B39A",
    "#9CA7B8",
    "#C6A38F",
    "#BFA08C",
    "#A8B88F",
    "#9FB29F",
    "#C28F7A",
    "#B98C78",
]

def generate_unique_colors(enum_cls):
    color_map = {}

    for company in enum_cls:
        digest = int(
            hashlib.sha256(company.name.encode()).hexdigest(),
            16,
        )
        color = PALETTE[digest % len(PALETTE)]
        color_map[company] = color

    return color_map
