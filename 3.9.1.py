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

# Table 3.9.1: Mental health treatment need of young people starting treatment in 2017-18 broken down by gender

from gssutils import *
scraper = Scraper('https://www.gov.uk/government/statistics/substance-misuse-treatment-for-young-people-statistics-2017-to-2018')
dist = scraper.distribution(title=lambda t: t.startswith('Data tables'))
tabs = {tab.name: tab for tab in dist.as_databaker()}
tab = tabs['3.9.1 Mental health treatment']

cell = tab.filter('Mental health treatment need')
cell.assert_one()
basis = cell.fill(DOWN).is_not_blank().is_not_whitespace() 
obs = tab.filter('n')
noobs = tab.one_of(['Total', 'Missing', 'Total number of new presentation']).fill(RIGHT)
observations = obs.fill(DOWN).is_not_blank().is_not_whitespace().is_number() - noobs
sex = obs.shift(0,-1)

Dimensions = [
            HDim(basis,'Mental health treatment need',DIRECTLY,LEFT),
            HDim(sex,'Sex',DIRECTLY, ABOVE),
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

new_table['Sex'] = new_table['Sex'].map(
    lambda x: {
        'Female' : 'F',
        'Male' : 'M',
        'Total' : 'T'
        }.get(x, x))

new_table['Mental health treatment need'] = new_table['Mental health treatment need'].map(
    lambda x: {
        'Engaged with community mental health team or other mental health services':'community-or-other-mental-health-servicess',
        'Mental health treatment from GP':'gp',
        'NICE recommended mental health treatment':'nice-recommended-mental-health-treatment',
        'Engaged with Improving Access to Psychological Therapies (IAPT)':'improving-access-to-psychological-therapies-iapt',
        'Identified space in a health based place of safety for mental health crises':'identified-space-in-a-health-based-place-of-safety-for-mental-health-crises',
        'Total individuals receiving any form of mental health treatment':'total-individuals-receiving-any-treatment-for-mental-health',
        'Mental health treatment need identified but no treatment received':'no-treatment-received-for-a-mental-health-treatment-need',
        'Total individuals with mental health treatment need':'total-individuals-needing-mental-health-treatment',
}.get(x, x))

new_table['Period'] = '2017-18'
new_table['Substance type'] = 'All'
new_table['Age'] = 'all young clients'
new_table = new_table[['Period','Age','Substance type','Mental health treatment need','Sex','Measure Type','Value','Unit']]

new_table['Period'] = new_table['Period'].map(
    lambda x: f'gregorian-interval/{str(x)[:4]}-03-31T00:00:00/P1Y')
new_table

# + {"endofcell": "--"}
destinationFolder = Path('out')
destinationFolder.mkdir(exist_ok=True, parents=True)

TAB_NAME = '3.9.1'

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

new_table['Mental health treatment need'].unique().tolist()


