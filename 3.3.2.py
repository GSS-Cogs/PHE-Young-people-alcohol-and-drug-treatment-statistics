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

# Table 3.3.2: Substance use (primary and adjunctive combined) by age of all young people in treatment 2017-18 

from gssutils import *
scraper = Scraper('https://www.gov.uk/government/statistics/substance-misuse-treatment-for-young-people-statistics-2017-to-2018')
dist = scraper.distribution(title=lambda t: t.startswith('Data tables'))
tabs = {tab.name: tab for tab in dist.as_databaker()}
tab = tabs['3.3.2 Age and Substance Use']

cell = tab.filter('Substance')
cell.assert_one()
substance = cell.fill(DOWN).is_not_blank().is_not_whitespace() 
age = cell.fill(RIGHT).is_not_blank().is_not_whitespace()
obs = tab.fill(RIGHT).one_of(['n'])
observations = obs.fill(DOWN).is_not_blank().is_not_whitespace().is_number()

Dimensions = [
            HDim(substance,'Substance',DIRECTLY,LEFT),
            HDim(age,'Basis of treatment',CLOSEST,LEFT),
            HDimConst('Measure Type', 'Count'),
            HDimConst('Unit','People')            
            ]
c1 = ConversionSegment(observations, Dimensions, processTIMEUNIT=True)
new_table = c1.topandas()

import numpy as np
new_table['OBS'].replace('', np.nan, inplace=True)
new_table.dropna(subset=['OBS'], inplace=True)
new_table.rename(columns={'OBS': 'Value'}, inplace=True)
new_table['Value'] = new_table['Value'].astype(int)

new_table['Basis of treatment'] = new_table['Basis of treatment'].map(
    lambda x: {
        'Under 13 2' : 'under-13' 
        }.get(x, x))

new_table['Basis of treatment'] = 'age/' + new_table['Basis of treatment']

new_table['Clients in treatment'] = 'Primary and adjunctive combined'

new_table['Basis of treatment'] = new_table['Basis of treatment'].str.rstrip('2')
new_table['Substance'] = new_table['Substance'].str.rstrip('234')

new_table['Substance'] = new_table['Substance'].str.lower()

new_table['Substance'] = new_table['Substance'].map(
    lambda x: {
        'new psychoactive substances' : 'new-psychoactive-substances', 
        }.get(x, x))

new_table['Period'] = '2017-18'
new_table = new_table[['Period','Basis of treatment','Substance','Clients in treatment','Measure Type','Value','Unit']]

new_table


