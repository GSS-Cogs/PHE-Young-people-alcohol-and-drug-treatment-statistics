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
            HDim(basis,'Clients in treatment',DIRECTLY,LEFT),
            HDim(wt,'Basis of treatment',CLOSEST, LEFT),
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

new_table['Basis of treatment'] = new_table['Basis of treatment'].map(
    lambda x: {
        'Total' : 'All weeks'
        }.get(x, x))

new_table['Basis of treatment'] =  'Waiting times/' + new_table['Basis of treatment'] 

new_table['Period'] = '2017-18'
new_table['Substance'] = 'All'
new_table = new_table[['Period','Basis of treatment','Substance','Clients in treatment','Measure Type','Value','Unit']]

new_table.tail()


