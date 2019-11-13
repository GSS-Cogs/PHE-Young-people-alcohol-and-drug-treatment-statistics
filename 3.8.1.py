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

# Table 3.8.1: Age and gender breakdown of young people starting treatment in 2017-18 and reported sexual exploitation

from gssutils import *
scraper = Scraper('https://www.gov.uk/government/statistics/substance-misuse-treatment-for-young-people-statistics-2017-to-2018')
dist = scraper.distribution(title=lambda t: t.startswith('Data tables'))
tabs = {tab.name: tab for tab in dist.as_databaker()}
tab = tabs['3.8.1 Sexual exploitation']

cell = tab.filter('Age')
cell.assert_one()
age = cell.fill(DOWN).is_not_blank().is_not_whitespace() 
obs = tab.filter('n')
observations = obs.fill(DOWN).is_not_blank().is_not_whitespace().is_number()
sex = obs.shift(0,-1)
basis = obs.shift(0,-2).is_not_whitespace().is_not_blank()

Dimensions = [
            HDim(basis,'Basis of treatment',CLOSEST,LEFT),
            HDim(age,'Age',DIRECTLY, LEFT),
            HDimConst('Measure Type','Count'),
            HDim(sex,'Sex',CLOSEST,LEFT),
            HDimConst('Unit','People')            
            ]
c1 = ConversionSegment(observations, Dimensions, processTIMEUNIT=True)
new_table = c1.topandas()

import numpy as np
new_table['OBS'].replace('', np.nan, inplace=True)
new_table.dropna(subset=['OBS'], inplace=True)
new_table.rename(columns={'OBS': 'Value'}, inplace=True)
new_table['Value'] = new_table['Value'].astype(int)

new_table['Age'] = new_table['Age'].map(
    lambda x: {
        'Total new presentations' : 'All young clients',
        'Under 141' : 'under-14'
        }.get(x, x))

new_table['Basis of treatment'] = new_table['Basis of treatment'].map(
    lambda x: {
        'Total new presentations' : 'total-new-presentations',
        'Sexual exploitation' : 'sexual-exploitation'
        }.get(x, x))

new_table['Age'] = new_table['Age'].str.rstrip('1')

new_table['Basis of treatment'] = new_table['Basis of treatment'].str.lower()
new_table['Age'] = new_table['Age'].str.lower()

new_table['Period'] = '2017-18'
new_table['Substance type'] = 'All'
new_table = new_table[['Period','Age','Substance type','Basis of treatment','Sex','Measure Type','Value','Unit']]

new_table['Period'] = new_table['Period'].map(
    lambda x: f'gregorian-interval/{str(x)[:4]}-03-31T00:00:00/P1Y')
new_table['Sex'] = new_table['Sex'].map(
    lambda x: 'F' if x == 'female' else ('M' if x == 'male' else 'T'))
new_table

# + {"endofcell": "--"}
destinationFolder = Path('out')
destinationFolder.mkdir(exist_ok=True, parents=True)

TAB_NAME = '3.8.1'

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


