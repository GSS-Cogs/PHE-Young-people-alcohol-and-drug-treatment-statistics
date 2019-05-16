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

# Table 4.2.2: Interventions received by young people in treatment in 2017-18 (post November 2013 dataset change interventions)

from gssutils import *
scraper = Scraper('https://www.gov.uk/government/statistics/substance-misuse-treatment-for-young-people-statistics-2017-to-2018')
dist = scraper.distribution(title=lambda t: t.startswith('Data tables'))
tabs = {tab.name: tab for tab in dist.as_databaker()}
tab = tabs['4.2.2 Interventions']

cell = tab.filter('Setting')
cell.assert_one()
setting = cell.fill(DOWN).is_not_blank().is_not_whitespace() 
obs = tab.one_of(['Psychosocial (n)', 'Harm reduction (n)', 'Pharmacological (n)', 'Total individuals with this setting1'])
noobs = tab.one_of(['% of total individuals with this intervention']).fill(RIGHT)
observations = obs.fill(DOWN).is_not_blank().is_not_whitespace().is_number() - noobs

Dimensions = [
            HDim(obs,'Clients in treatment',DIRECTLY,ABOVE),
            HDim(setting,'Basis of treatment',DIRECTLY, LEFT),
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

new_table['Basis of treatment'] =  'Setting/' + new_table['Basis of treatment'] 

new_table['Basis of treatment'] = new_table['Basis of treatment'].str.rstrip('2')

new_table['Clients in treatment'] = new_table['Clients in treatment'].str.rstrip('(n)1')

new_table['Period'] = '2017-18'
new_table['Substance'] = 'All'
new_table = new_table[['Period','Basis of treatment','Substance','Clients in treatment','Measure Type','Value','Unit']]

new_table


