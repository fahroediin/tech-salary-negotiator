#!/usr/bin/env python3
from services.umk_data import UMK_DATA_2024

print(f'Total kota/kabupaten tersedia: {len(UMK_DATA_2024)}')
print('\nCakupan wilayah:')
regions = {}
for data in UMK_DATA_2024.values():
    region = data['region']
    regions[region] = regions.get(region, 0) + 1

for region, count in regions.items():
    print(f'  {region}: {count} kota/kabupaten')

print('\nContoh kota besar yang tersedia'):
major_cities = ['jakarta', 'bandung', 'surabaya', 'medan', 'semarang', 'makassar', 'denpasar']
for city in major_cities:
    if city in UMK_DATA_2024:
        data = UMK_DATA_2024[city]
        print(f'  {data["kabupaten_kota"]}: Rp {data["umk"]:,}'.replace(',', '.'))