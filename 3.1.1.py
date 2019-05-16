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
            HDim(age,'Basis of treatment',DIRECTLY,LEFT),
            HDim(sex,'Clients in treatment',CLOSEST,LEFT),
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

new_table['Basis of treatment'] = 'Ag/' + new_table['Basis of treatment']

new_table['Basis of treatment'] = new_table['Basis of treatment'].map(
    lambda x: {
        'Ag/Total clients' : 'Ag/All years' 
        }.get(x, x))

new_table['Clients in treatment'] = new_table['Clients in treatment'].map(
    lambda x: {
        'Female' : 'F', 
        'Male' : 'M',
        'Total' : 'T'
        }.get(x, x))

new_table['Period'] = '2017-18'
new_table['Substance'] = 'All'
new_table = new_table[['Period','Basis of treatment','Substance','Clients in treatment','Measure Type','Value','Unit']]

new_table


