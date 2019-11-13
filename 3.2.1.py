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

# Table 3.2.1: Ethnicity of all young people in treatment 2017-18

from gssutils import *
scraper = Scraper('https://www.gov.uk/government/statistics/substance-misuse-treatment-for-young-people-statistics-2017-to-2018')
dist = scraper.distribution(title=lambda t: t.startswith('Data tables'))
tabs = {tab.name: tab for tab in dist.as_databaker()}
tab = tabs['3.2.1 Ethnicity']

cell = tab.filter('Ethnicity')
cell.assert_one()
ethnicity = cell.fill(DOWN).is_not_blank().is_not_whitespace() 
obs = cell.fill(RIGHT).one_of(['n'])
noobs1 = tab.filter('Missing or inconsistent data').fill(RIGHT)
noobs2 = noobs1.shift(0,-1)
observations = obs.fill(DOWN).is_not_blank().is_not_whitespace().is_number()
observations = observations - noobs1 - noobs2

Dimensions = [
            HDim(ethnicity,'Ethnicity',DIRECTLY,LEFT),
            HDimConst('Age','All young clients'),
            HDimConst('Measure Type', 'Count'),
            HDimConst('Unit','People')            
            ]
c1 = ConversionSegment(observations, Dimensions, processTIMEUNIT=True)
new_table = c1.topandas()
savepreviewhtml(c1, fname="Preview.html")

import numpy as np
new_table['OBS'].replace('', np.nan, inplace=True)
new_table.dropna(subset=['OBS'], inplace=True)
new_table.rename(columns={'OBS': 'Value'}, inplace=True)
new_table['Value'] = new_table['Value'].astype(int)

new_table['Ethnicity'] = new_table['Ethnicity'].map(
    lambda x: {
        'Ethnicity':'ethnicity',
        'White British':'white-british',
        'Other White':'other-white',
        'Not Stated':'not-stated',
        'White Irish':'white-irish',
        'Indian':'indian',
        'Caribbean':'caribbean',
        'White and black Caribbean':'white-and-black-caribbean',
        'Pakistani':'pakistani',
        'Other Asian':'other-asian',
        'Other':'other',
        'Other black':'other-black',
        'African':'african',
        'Other Mixed':'other-mixed',
        'Bangladeshi':'bangladeshi',
        'White and Asian':'white-and-asian',
        'White and black African':'white-and-black-african',
        'Chinese':'chinese',
        'Unknown':'unknown',
        'Inconsistent/missing':'inconsistent/missing',
        'Total':'all'        
        }.get(x, x))

new_table['Period'] = '2017-18'
new_table['Substance type'] = 'All'
new_table = new_table[['Period','Age','Substance type','Ethnicity','Measure Type','Value','Unit']]

new_table

# + {"endofcell": "--"}
destinationFolder = Path('out')
destinationFolder.mkdir(exist_ok=True, parents=True)

TAB_NAME = '3.2.1 Ethnicity'

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
