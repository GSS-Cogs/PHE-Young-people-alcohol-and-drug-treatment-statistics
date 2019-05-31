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
            HDim(age,'Clients in treatment',DIRECTLY, LEFT),
            HDimConst('Measure Type','Count'),
            HDim(sex,'sex',CLOSEST,LEFT),
            HDimConst('Unit','People')            
            ]
c1 = ConversionSegment(observations, Dimensions, processTIMEUNIT=True)
new_table = c1.topandas()

import numpy as np
new_table['OBS'].replace('', np.nan, inplace=True)
new_table.dropna(subset=['OBS'], inplace=True)
new_table.rename(columns={'OBS': 'Value'}, inplace=True)
new_table['Value'] = new_table['Value'].astype(int)

new_table['Clients in treatment'] = new_table['Clients in treatment'].map(
    lambda x: {
        'Total new presentations' : 'all-years',
        'Under 141' : 'under-14'
        }.get(x, x))

new_table['Basis of treatment'] = new_table['Basis of treatment'].map(
    lambda x: {
        'Total new presentations' : 'total-new-presentations',
        'Sexual exploitation' : 'sexual-exploitation'
        }.get(x, x))

new_table['Clients in treatment'] = new_table['Clients in treatment'].str.rstrip('1')

new_table['Clients in treatment'] =  'age-' + new_table['Clients in treatment']

new_table['Basis of treatment'] = new_table['Basis of treatment'] + '/' + new_table['sex']

new_table['Basis of treatment'] = new_table['Basis of treatment'] + '-' + new_table['Clients in treatment']

new_table['Basis of treatment'] = new_table['Basis of treatment'].str.lower()
new_table['Clients in treatment'] = new_table['Clients in treatment'].str.lower()

new_table['Period'] = '2017-18'
new_table['Substance'] = 'All'
new_table = new_table[['Period','Basis of treatment','Substance','Clients in treatment','Measure Type','Value','Unit']]

new_table


