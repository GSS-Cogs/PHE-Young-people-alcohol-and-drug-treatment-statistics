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
            HDimConst('Clients in treatment','All young clients'),
            HDim(substance,'Substance',DIRECTLY,LEFT),
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

new_table['Basis of treatment'] =  'Treatment by primary substance' 

new_table['Substance'] = new_table['Substance'].str.rstrip('12')

new_table = new_table[['Period','Basis of treatment','Substance','Clients in treatment','Measure Type','Value','Unit']]

new_table


