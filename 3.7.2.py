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

# Table 3.7.2: Individual vulnerabilities identified among all young people starting treatment in 2017-18

from gssutils import *
scraper = Scraper('https://www.gov.uk/government/statistics/substance-misuse-treatment-for-young-people-statistics-2017-to-2018')
dist = scraper.distribution(title=lambda t: t.startswith('Data tables'))
tabs = {tab.name: tab for tab in dist.as_databaker()}
tab = tabs['3.7.2 Vulnerabilities']

cell = tab.filter('Vulnerability')
cell.assert_one()
vulnerability = cell.fill(DOWN).is_not_blank().is_not_whitespace() 
sex = cell.fill(RIGHT).one_of(['Female', 'Male', 'Persons'])
observations = sex.fill(DOWN).is_not_blank().is_not_whitespace().is_number()

Dimensions = [
            HDim(vulnerability,'Vulnerability',DIRECTLY,LEFT),
            HDim(sex,'Sex',CLOSEST,LEFT),
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

new_table['Vulnerability'] = new_table['Vulnerability'].map(
    lambda x: {
        'Female' : 'F', 
        'Male' : 'M',
        'Persons' : 'T'
        }.get(x, x))

new_table['Vulnerability'] = new_table['Vulnerability'].str.lower()

new_table['Vulnerability'] = new_table['Vulnerability'].map(
    lambda x: {
        'early onset of substance misuse':'early-onset-of-substance-misuse',
        'poly drug user':'poly-drug-user',
        'antisocial behaviour':'antisocial-behaviour',
        'mental health treatment need':'mental-health-treatment-need',
        'affected by others substance misuse':'affected-by-others-substance-misuse',
        'affected by domestic abuse':'affected-by-domestic-abuse',
        'looked after child':'looked-after-child',
        'child in need':'child-in-need',
        'child protection plan':'child-protection-plan',
        'sexual exploitation':'sexual-exploitation',
        'high risk alcohol user':'high-risk-alcohol-user',
        'opiate and/or crack use':'opiate-and/or-crack-use',
        'pregnant and/or parent':'pregnant-and/or-parent',
        'housing problem':'housing-problem',
        'injecting':'injecting',
        'total new presentations':'total-new-presentations'}.get(x, x))

new_table['Period'] = '2017-18'
new_table['Substance type'] = 'total'
new_table['Age'] = 'All young clients'
new_table = new_table[['Period','Age','Substance type','Vulnerability','Sex','Measure Type','Value','Unit']]

new_table['Period'] = new_table['Period'].map(
    lambda x: f'gregorian-interval/{str(x)[:4]}-03-31T00:00:00/P1Y')
new_table

# + {"endofcell": "--"}
destinationFolder = Path('out')
destinationFolder.mkdir(exist_ok=True, parents=True)

TAB_NAME = '3.7.2'

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

new_table['Vulnerability'].unique().tolist()


