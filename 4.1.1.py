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

# Table 4.1.1: Waiting times: first and subsequent interventions 2017-18

from gssutils import *
scraper = Scraper('https://www.gov.uk/government/statistics/substance-misuse-treatment-for-young-people-statistics-2017-to-2018')
dist = scraper.distribution(title=lambda t: t.startswith('Data tables'))
tabs = {tab.name: tab for tab in dist.as_databaker()}
tab = tabs['4.1.1 Waiting Times']

cell = tab.filter('Intervention')
cell.assert_one()
basis = cell.fill(DOWN).is_not_blank().is_not_whitespace() 
obs = tab.filter('n')
observations = obs.fill(DOWN).is_not_blank().is_not_whitespace().is_number() 
wt = obs.shift(0,-1)

Dimensions = [
            HDim(basis,'Intervention',DIRECTLY,LEFT),
            HDim(wt,'Waiting time',CLOSEST, LEFT),
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

new_table['Waiting time'] = new_table['Waiting time'].map(
    lambda x: {
        'Total' : 'all',
        '3 weeks or under' : '3-weeks-or-under',
        'Over 3 weeks' : 'over-3-weeks'
        }.get(x, x))

new_table['Intervention'] = new_table['Intervention'].map(
    lambda x: {
        'First Intervention' : 'first-intervention' , 
        'Subsequent Intervention' : 'subsequent-intervention',
        'Total Interventions' : 'total-interventions'
        }.get(x, x))

new_table['Period'] = '2017-18'
new_table['Substance type'] = 'total'
new_table['Age'] = 'all young clients'
new_table = new_table[['Period','Age','Substance type','Waiting time','Intervention','Measure Type','Value','Unit']]

new_table['Period'] = new_table['Period'].map(
    lambda x: f'gregorian-interval/{str(x)[:4]}-03-31T00:00:00/P1Y')
new_table

# + {"endofcell": "--"}
destinationFolder = Path('out')
destinationFolder.mkdir(exist_ok=True, parents=True)

TAB_NAME = '4.1.1 Waiting Times'

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




