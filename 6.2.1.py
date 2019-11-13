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

# Table 6.2.1: Number of young people in treatment by primary substance (2005-06 to 2017-18)

from gssutils import *
scraper = Scraper('https://www.gov.uk/government/statistics/substance-misuse-treatment-for-young-people-statistics-2017-to-2018')
dist = scraper.distribution(title=lambda t: t.startswith('Data tables'))
tabs = {tab.name: tab for tab in dist.as_databaker()}
tab = tabs['6.2.1 Primary Substance Trends']

cell = tab.filter('Substance')
cell.assert_one()
substance = cell.fill(DOWN).is_not_blank().is_not_whitespace() 
period = cell.fill(RIGHT).is_not_blank().is_not_whitespace()
obs = tab.filter('n')
observations = obs.fill(DOWN).is_not_blank().is_not_whitespace().is_number()

Dimensions = [
            HDimConst('Measure Type','Count'),
            HDimConst('Age','all young clients'),
            HDim(substance,'Substance type',DIRECTLY,LEFT),
            HDim(period,'Period',CLOSEST,LEFT),
            HDimConst('Unit','People')            
            ]
c1 = ConversionSegment(observations, Dimensions, processTIMEUNIT=True)
new_table = c1.topandas()

import numpy as np
new_table['OBS'].replace('', np.nan, inplace=True)
new_table.dropna(subset=['OBS'], inplace=True)
new_table.rename(columns={'OBS': 'Value'}, inplace=True)
new_table['Value'] = new_table['Value'].astype(int)

new_table['Substance type'] = new_table['Substance type'].str.rstrip('12')

new_table['Substance type'] = new_table['Substance type'].str.lower()

new_table = new_table[['Period','Age','Substance type','Measure Type','Value','Unit']]

new_table

# + {"endofcell": "--"}
destinationFolder = Path('out')
destinationFolder.mkdir(exist_ok=True, parents=True)

TAB_NAME = '6.2.1 Primary Substance Trends'

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


