# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.4'
#       jupytext_version: 1.1.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# Table 4.2.2: Interventions received by young people in treatment in 2017-18 (post November 2013 dataset change interventions)

from gssutils import *
scraper = Scraper('https://www.gov.uk/government/statistics/substance-misuse-treatment-for-young-people-statistics-2017-to-2018')
dist = scraper.distribution(title=lambda t: t.startswith('Data tables'))
tabs = {tab.name: tab for tab in dist.as_databaker()}
tab = tabs['4.2.2 Interventions']

cell = tab.filter('Setting')
cell.assert_one()
setting = cell.fill(DOWN).is_not_blank().is_not_whitespace() 
obs = tab.one_of(['Psychosocial (n)', 'Harm reduction (n)', 'Pharmacological (n)', 'Total individuals with this setting1'])
noobs = tab.one_of(['% of total individuals with this intervention']).fill(RIGHT)
observations = obs.fill(DOWN).is_not_blank().is_not_whitespace().is_number() - noobs

Dimensions = [
            HDim(obs,'Intervention type',DIRECTLY,ABOVE),
            HDim(setting,'Intervention setting',DIRECTLY, LEFT),
            HDimConst('Measure Type','Count'),
            HDimConst('Unit','People')            
            ]
c1 = ConversionSegment(observations, Dimensions, processTIMEUNIT=True)
new_table = c1.topandas()

import numpy as np
new_table['OBS'].replace('', np.nan, inplace=True)
new_table.dropna(subset=['OBS'], inplace=True)
new_table.rename(columns={'OBS': 'Value'}, inplace=True)
new_table['Value'] = new_table['Value'].astype(int)

new_table['Intervention setting'] = new_table['Intervention setting'].str.rstrip('2')

new_table['Intervention type'] = new_table['Intervention type'].str.rstrip('(n)1')

new_table['Intervention type'] = new_table['Intervention type'].map(
    lambda x: {
        'Psychosocial ' : 'psychosocial', 
        'Harm reduction ' : 'harm-reduction', 
        'Pharmacological ' : 'pharmacological',
       'Total individuals with this setting'  : 'all'        
        }.get(x, x))

new_table['Intervention setting'] = new_table['Intervention setting'].map(
    lambda x: {
        'Community' : 'community',
        'Home'  : 'home',
        'YP Residential unit' : 'yp-residential-unit',
        'Adult setting' : 'adult-setting',
        'YP Inpatient unit' : 'yp-inpatient-unit',
        'No setting recorded' : 'no-setting-recorded'}.get(x, x))

# +
#new_table['Basis of treatment'] =  'setting/' + new_table['Basis of treatment'] + '-' + new_table['Clients in treatment']
# -

new_table['Period'] = '2017-18'
new_table['Substance type'] = 'All'
new_table['Age'] = 'all young clients'
new_table = new_table[['Period','Age','Substance type','Intervention setting','Intervention type','Measure Type','Value','Unit']]

new_table

# + {"endofcell": "--"}
destinationFolder = Path('out')
destinationFolder.mkdir(exist_ok=True, parents=True)

TAB_NAME = '4.2.2 Interventions'

new_table.drop_duplicates().to_csv(destinationFolder / f'{TAB_NAME}.csv', index = False)

# # +
from gssutils.metadata import THEME

scraper.dataset.family = 'health'
scraper.dataset.theme = THEME['health-social-care']
#scraper.set_base_uri('http://gss-data.org.uk')
#scraper.set_dataset_id(f'health/PHE-Young-people-alcohol-and-drug-treatment-statistics/{TAB_NAME}')
with open(destinationFolder / f'{TAB_NAME}.csv-metadata.trig', 'wb') as metadata:
    metadata.write(scraper.generate_trig())
# -

schema = CSVWMetadata('https://gss-cogs.github.io/ref_alcohol/')
schema.create(destinationFolder / f'{TAB_NAME}.csv', destinationFolder / f'{TAB_NAME}.csv-schema.json')

new_table
# --


