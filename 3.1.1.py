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

# Table 3.1.1: Age and Gender of all young people in treatment 2017-18

from gssutils import *
scraper = Scraper('https://www.gov.uk/government/statistics/substance-misuse-treatment-for-young-people-statistics-2017-to-2018')
dist = scraper.distribution(title=lambda t: t.startswith('Data tables'))
tabs = {tab.name: tab for tab in dist.as_databaker()}
tab = tabs['3.1.1 Age and Gender']

cell = tab.filter('Age')
cell.assert_one()
age = cell.fill(DOWN).is_not_blank().is_not_whitespace() 
sex = cell.fill(RIGHT).one_of(['Female', 'Male', 'Total'])
observations = sex.fill(DOWN).is_not_blank().is_not_whitespace().is_number()

Dimensions = [
            HDim(age,'Age',DIRECTLY,LEFT),
            HDim(sex,'Sex',CLOSEST,LEFT),
            HDimConst('Measure Type','Count'),
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

new_table['Sex'] = new_table['Sex'].str.lower()

new_table['Age'] = new_table['Age'].map(
    lambda x: {
        'Total clients' : 'all-years',
        'Under 12' : 'under-12'
        }.get(x, x))

# +
#new_table['Basis of treatment'] = 'age/' + new_table['Basis of treatment']

# +
#new_table['Age'] = new_table['Age'] + '-' + new_table['Clients in treatment']
# -

new_table['Period'] = '2017-18'
new_table['Substance type'] = 'All'
new_table = new_table[['Period','Age','Substance type','Sex','Measure Type','Value','Unit']]

new_table

# + {"endofcell": "--"}
destinationFolder = Path('out')
destinationFolder.mkdir(exist_ok=True, parents=True)

TAB_NAME = '3.1.1'

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


