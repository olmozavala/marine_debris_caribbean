import json
from os.path import join
import collections

caribbean_countries = {
    'AIA':'Anguilla',
    'ATG':'Antigua and Barbuda',
    'ABW':'Aruba',
    'BHS':'Bahamas',
    'BRB':'Barbados',
    'BLZ':'Belize',
    'BES':'Bonaire', # 'Bonaire, Saint Eustatius and Saba',
    'VGB':'British Virgin Islands',
    'GTM':'Guatemala',
    'GLP':'Guadeloupe',
    'GUY':'Guyana',
    'GUF':'French Guiana',
    'CYM':'Cayman Islands',
    'COL':'Colombia',
    'CRI':'Costa Rica',
    'CUB':'Cuba',
    'CUW':'Curaçao',
    'DMA':'Dominica',
    'DOM':'Dominican Republic',
    'GRD':'Grenada',
    'HTI':'Haiti',
    'HND':'Honduras',
    'JAM':'Jamaica',
    'MTQ':'Martinique',
    'MEX':'Mexico',
    'MSR':'Montserrat',
    'NIC':'Nicaragua',
    'PAN':'Panama',
    'PRI':'Puerto Rico',
    'BLM':'Saint-Barthélemy',
    'MAF':'Saint-Martin',
    'KNA':'Saint Kitts and Nevis',
    'LCA':'Saint Lucia',
    'VCT':'Saint Vincent and the Grenadines',
    'SUR':'Suriname',
    'TCA':'Turks and Caicos Islands',
    'TTO':'Trinidad and Tobago',
    'USA':'United States',
    'VIR':'Virgin Islands',
    'VEN':'Venezuela',
}

tables_folder = "/data/COAPS_Net/work/ozavala/CARIBBEAN_marine_debris/statistics/"
global_json = join(tables_folder,"ReachedTablesData.json")
f = open(global_json)
global_data = json.load(f)
f.close()

regional_data = {}
missing_countries = []

def jsonToCSV(json_object, file_name):
    print("Converting JSON to CSV")
    new_country = "Country Name, Tons Exported, Ends in the Ocean, Ends in the beach, Ends in a Caribbean beach \n"
    json_object = collections.OrderedDict(sorted(json_object.items()))
    csv_file = ""
    for country_name in json_object:
        country = json_object[country_name]

        try:
            country_txt = "\n" + new_country
            country_txt += F"{country_name.capitalize()}"
            # Adding the from countries
            from_data = []
            to_data = []
            if 'from' in country:
                country_txt += F", {country['from']['tot_tons']}, {country['from']['ocean_tons']}," \
                               F" {country['from']['beach_tons']}, {country['from']['beach_tons_caribbean']} \n"
                if 'from' in country['from']:
                    for from_country in country['from']['from']:
                        from_data.append(F"Tons to {from_country['name']}, {from_country['tons']},")

            if 'to' in country:
                # Adding the to countries
                for to_country in country['to']['to']:
                    to_data.append(F"Tons from {to_country['name']}, {to_country['tons']},")

            rows = max(len(from_data), len(to_data))
            for i in range(rows):
                c_row = ",,,,,"
                if i < len(from_data):
                    c_row += from_data[i]
                else:
                    c_row += ",,"

                if i < len(to_data):
                    c_row += to_data[i]

                country_txt += c_row + "\n"

            csv_file += country_txt

        except Exception as e:
            print(F"Failed for {country_name}: {e}")

    f = open(file_name, 'w')
    f.write(csv_file)

    print("Done!")


def add_stat_by_type(c_name, g_country, carib_c_country, c_type):
    if c_type in g_country[c_type]:
        tot_carib_tons = 0
        new_from_countries = []
        # Add the countries that come from the caribbean
        for c_country_from in g_country[c_type][c_type]:
            c_name_from = c_country_from['name']
            if c_name_from in caribbean_countries.values():
                tot_carib_tons += c_country_from['tons']
                if c_country_from['tons'] > 0:
                    new_from = {
                        'name': c_name_from,
                        'tons': c_country_from['tons'],
                        'perc': -1
                    }
                    new_from_countries.append(new_from)

        # Recompute the percentage of beached
        for carib_country in new_from_countries:
            carib_country['perc'] = carib_country['tons'] / tot_carib_tons
        # Finalize this country
        carib_c_country[c_type]['beach_tons_caribbean'] = tot_carib_tons
        carib_c_country[c_type][c_type] = new_from_countries
    return carib_c_country

if __name__ == "__main__":
    for key, c_name in caribbean_countries.items():
        print(F"Analyzing country {c_name}")
        if c_name in global_data:
            g_country = global_data.get(c_name)
            # It shouldn't be like this, but the first from is for 'general' data.
            carib_c_country = {}
            if 'from' in g_country:
                carib_c_country = {'from':{
                    'name':c_name,
                    'tot_tons':  int(g_country['from']['tot_tons']),
                    'ocean_tons':int(g_country['from']['ocean_tons']),
                    'ocean_perc':int(g_country['from']['ocean_perc']),
                    'beach_tons':int(g_country['from']['beach_tons']),
                    'beach_perc':int(g_country['from']['beach_perc']),
                    }
                }
                carib_c_country = add_stat_by_type(c_name, g_country, carib_c_country, 'from')
            if 'to' in g_country:
                carib_c_country['to'] ={
                    'name':c_name,
                    'tot_tons':int(g_country['to']['tot_tons']),
                    }
                carib_c_country = add_stat_by_type(c_name, g_country, carib_c_country, 'to')
            regional_data[c_name] = carib_c_country
        else:
            missing_countries.append(c_name)


json_txt = json.dumps(dict(sorted(regional_data.items())))
output_file = join(tables_folder, 'ReachedTablesDataCaribbean.json')
output_file_csv = join(tables_folder, 'ReachedTablesDataCaribbean.csv')
print(F"Missing countries: {missing_countries}")
jsonToCSV(regional_data, output_file_csv)
f = open(output_file, "w+")
f.write(json_txt)