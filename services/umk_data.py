"""
Indonesian UMK (Upah Minimum Kabupaten/Kota) Data
Source: Kementerian Ketenagakerjaan RI
Year: 2024
"""

UMK_DATA_2024 = {
    # Jabodetabek (DKI Jakarta, Bogor, Depok, Tangerang, Bekasi)
    'jakarta': {
        'kabupaten_kota': 'Jakarta',
        'provinsi': 'DKI Jakarta',
        'umk': 5067823,  # UMR DKI Jakarta 2024
        'region': 'jabodetabek'
    },
    'jakarta pusat': {
        'kabupaten_kota': 'Jakarta Pusat',
        'provinsi': 'DKI Jakarta',
        'umk': 5067823,
        'region': 'jabodetabek'
    },
    'jakarta utara': {
        'kabupaten_kota': 'Jakarta Utara',
        'provinsi': 'DKI Jakarta',
        'umk': 5067823,
        'region': 'jabodetabek'
    },
    'jakarta barat': {
        'kabupaten_kota': 'Jakarta Barat',
        'provinsi': 'DKI Jakarta',
        'umk': 5067823,
        'region': 'jabodetabek'
    },
    'jakarta selatan': {
        'kabupaten_kota': 'Jakarta Selatan',
        'provinsi': 'DKI Jakarta',
        'umk': 5067823,
        'region': 'jabodetabek'
    },
    'jakarta timur': {
        'kabupaten_kota': 'Jakarta Timur',
        'provinsi': 'DKI Jakarta',
        'umk': 5067823,
        'region': 'jabodetabek'
    },
    'bogor': {
        'kabupaten_kota': 'Kota Bogor',
        'provinsi': 'Jawa Barat',
        'umk': 4459693,
        'region': 'jabodetabek'
    },
    'depok': {
        'kabupaten_kota': 'Kota Depok',
        'provinsi': 'Jawa Barat',
        'umk': 4415979,
        'region': 'jabodetabek'
    },
    'tangerang': {
        'kabupaten_kota': 'Kota Tangerang',
        'provinsi': 'Banten',
        'umk': 4350672,
        'region': 'jabodetabek'
    },
    'tangerang selatan': {
        'kabupaten_kota': 'Kota Tangerang Selatan',
        'provinsi': 'Banten',
        'umk': 4350672,
        'region': 'jabodetabek'
    },
    'bekasi': {
        'kabupaten_kota': 'Kota Bekasi',
        'provinsi': 'Jawa Barat',
        'umk': 4781208,
        'region': 'jabodetabek'
    },

    # Jawa Barat
    'bandung': {
        'kabupaten_kota': 'Kota Bandung',
        'provinsi': 'Jawa Barat',
        'umk': 3742275,
        'region': 'jawa_barat'
    },
    'cimahi': {
        'kabupaten_kota': 'Kota Cimahi',
        'provinsi': 'Jawa Barat',
        'umk': 3742275,
        'region': 'jawa_barat'
    },
    'sukabumi': {
        'kabupaten_kota': 'Kota Sukabumi',
        'provinsi': 'Jawa Barat',
        'umk': 2679393,
        'region': 'jawa_barat'
    },
    'cirebon': {
        'kabupaten_kota': 'Kota Cirebon',
        'provinsi': 'Jawa Barat',
        'umk': 2197442,
        'region': 'jawa_barat'
    },

    # Jawa Tengah
    'semarang': {
        'kabupaten_kota': 'Kota Semarang',
        'provinsi': 'Jawa Tengah',
        'umk': 2954326,
        'region': 'jawa_tengah'
    },
    'surakarta': {
        'kabupaten_kota': 'Kota Surakarta',
        'provinsi': 'Jawa Tengah',
        'umk': 2104701,
        'region': 'jawa_tengah'
    },
    'solo': {
        'kabupaten_kota': 'Kota Surakarta',
        'provinsi': 'Jawa Tengah',
        'umk': 2104701,
        'region': 'jawa_tengah'
    },
    'yogyakarta': {
        'kabupaten_kota': 'Yogyakarta',
        'provinsi': 'DI Yogyakarta',
        'umk': 2165830,
        'region': 'yogyakarta'
    },

    # Jawa Timur
    'surabaya': {
        'kabupaten_kota': 'Kota Surabaya',
        'provinsi': 'Jawa Timur',
        'umk': 2430438,
        'region': 'jawa_timur'
    },
    'malang': {
        'kabupaten_kota': 'Kota Malang',
        'provinsi': 'Jawa Timur',
        'umk': 2087093,
        'region': 'jawa_timur'
    },
    'kediri': {
        'kabupaten_kota': 'Kota Kediri',
        'provinsi': 'Jawa Timur',
        'umk': 1997077,
        'region': 'jawa_timur'
    },
    'blitar': {
        'kabupaten_kota': 'Kota Blitar',
        'provinsi': 'Jawa Timur',
        'umk': 2143536,
        'region': 'jawa_timur'
    },

    # Bali
    'denpasar': {
        'kabupaten_kota': 'Kota Denpasar',
        'provinsi': 'Bali',
        'umk': 2636407,
        'region': 'bali'
    },
    'badung': {
        'kabupaten_kota': 'Kabupaten Badung',
        'provinsi': 'Bali',
        'umk': 2636407,
        'region': 'bali'
    },

    # Sumatera
    'medan': {
        'kabupaten_kota': 'Kota Medan',
        'provinsi': 'Sumatera Utara',
        'umk': 3019784,
        'region': 'sumatera'
    },
    'palembang': {
        'kabupaten_kota': 'Kota Palembang',
        'provinsi': 'Sumatera Selatan',
        'umk': 3284052,
        'region': 'sumatera'
    },
    'padang': {
        'kabupaten_kota': 'Kota Padang',
        'provinsi': 'Sumatera Barat',
        'umk': 2600628,
        'region': 'sumatera'
    },
    'pekanbaru': {
        'kabupaten_kota': 'Kota Pekanbaru',
        'provinsi': 'Riau',
        'umk': 3194262,
        'region': 'sumatera'
    },

    # Kalimantan
    'banjarmasin': {
        'kabupaten_kota': 'Kota Banjarmasin',
        'provinsi': 'Kalimantan Selatan',
        'umk': 3034324,
        'region': 'kalimantan'
    },
    'samarinda': {
        'kabupaten_kota': 'Kota Samarinda',
        'provinsi': 'Kalimantan Timur',
        'umk': 3094230,
        'region': 'kalimantan'
    },
    'balikpapan': {
        'kabupaten_kota': 'Kota Balikpapan',
        'provinsi': 'Kalimantan Timur',
        'umk': 3294214,
        'region': 'kalimantan'
    },
    'pontianak': {
        'kabupaten_kota': 'Kota Pontianak',
        'provinsi': 'Kalimantan Barat',
        'umk': 2836287,
        'region': 'kalimantan'
    },

    # Sulawesi
    'makassar': {
        'kabupaten_kota': 'Kota Makassar',
        'provinsi': 'Sulawesi Selatan',
        'umk': 3372930,
        'region': 'sulawesi'
    },
    'manado': {
        'kabupaten_kota': 'Kota Manado',
        'provinsi': 'Sulawesi Utara',
        'umk': 3503965,
        'region': 'sulawesi'
    },

    # Papua
    'jayapura': {
        'kabupaten_kota': 'Kota Jayapura',
        'provinsi': 'Papua',
        'umk': 3611729,
        'region': 'papua'
    }
}

def get_umk_for_location(location: str) -> dict:
    """
    Get UMK data for a given location
    """
    if not location:
        return None

    # Normalize location name
    location_lower = location.lower().strip()

    # Remove common prefixes/suffixes
    location_clean = location_lower
    location_clean = location_clean.replace('kota ', '').replace('kabupaten ', '')
    location_clean = location_clean.replace(' daerah istimewa yogyakarta', 'yogyakarta')
    location_clean = location_clean.replace('dki ', '')

    # Direct lookup
    if location_clean in UMK_DATA_2024:
        return UMK_DATA_2024[location_clean]

    # Try to find partial matches
    for key, data in UMK_DATA_2024.items():
        if key in location_clean or location_clean in key:
            return data

    # Try province-level UMK
    province_umk = {
        'bali': 2636407,
        'dki jakarta': 5067823,
        'di yogyakarta': 2165830,
        'yogyakarta': 2165830,
        'jawa barat': 1842589,  # UMP Jawa Barat 2024
        'jawa tengah': 1963008,  # UMP Jawa Tengah 2024
        'jawa timur': 2087170,  # UMP Jawa Timur 2024
    }

    for province, umk in province_umk.items():
        if province in location_lower:
            return {
                'kabupaten_kota': f'Provinsi {province.title()}',
                'provinsi': province.title(),
                'umk': umk,
                'region': 'province'
            }

    return None

def format_umk(umk_amount: int) -> str:
    """
    Format UMK amount to Indonesian Rupiah format
    """
    return f"Rp {umk_amount:,}".replace(',', '.')

def calculate_umk_compliance(base_salary: int, umk_data: dict) -> dict:
    """
    Calculate compliance with UMK
    """
    if not umk_data:
        return {
            'complies': True,
            'percentage_above_umk': None,
            'umk_amount': None,
            'difference': None,
            'message': 'UMK data not available for this location'
        }

    umk_amount = umk_data['umk']

    # Annual salary comparison
    annual_salary = base_salary * 12
    annual_umk = umk_amount * 12

    difference = annual_salary - annual_umk
    percentage_above = (difference / annual_umk) * 100 if annual_umk > 0 else 0

    compliance_status = {
        'complies': annual_salary >= annual_umk,
        'percentage_above_umk': round(percentage_above, 1),
        'umk_amount': umk_amount,
        'umk_amount_formatted': format_umk(umk_amount),
        'annual_umk': annual_umk,
        'annual_umk_formatted': format_umk(annual_umk),
        'difference': difference,
        'difference_formatted': format_umk(difference) if difference > 0 else f"-Rp {abs(difference):,}".replace(',', '.'),
        'monthly_salary': base_salary,
        'monthly_salary_formatted': format_umk(base_salary),
        'annual_salary': annual_salary,
        'annual_salary_formatted': format_umk(annual_salary),
        'message': ''
    }

    if annual_salary < annual_umk:
        compliance_status['message'] = f'WARNING: Offer is {abs(percentage_above):.1f}% below UMK!'
        compliance_status['risk_level'] = 'high'
    elif percentage_above < 20:
        compliance_status['message'] = f'Meets UMK requirement ({percentage_above:.1f} above minimum)'
        compliance_status['risk_level'] = 'low'
    elif percentage_above < 50:
        compliance_status['message'] = f'Above UMK requirement ({percentage_above:.1f} above minimum)'
        compliance_status['risk_level'] = 'low'
    else:
        compliance_status['message'] = f'Significantly above UMK requirement ({percentage_above:.1f} above minimum)'
        compliance_status['risk_level'] = 'none'

    return compliance_status