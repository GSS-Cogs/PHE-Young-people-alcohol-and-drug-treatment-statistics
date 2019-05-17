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

# Table 3.2.1: Ethnicity of all young people in treatment 2017-18

from gssutils import *
scraper = Scraper('https://www.gov.uk/government/statistics/substance-misuse-treatment-for-young-people-statistics-2017-to-2018')
dist = scraper.distribution(title=lambda t: t.startswith('Data tables'))
tabs = {tab.name: tab for tab in dist.as_databaker()}
tab = tabs['3.2.1 Ethnicity']

cell = tab.filter('Ethnicity')
cell.assert_one()
ethnicity = cell.fill(DOWN).is_not_blank().is_not_whitespace() 
obs = cell.fill(RIGHT).one_of(['n'])
noobs1 = tab.filter('Missing or inconsistent data').fill(RIGHT)
noobs2 = noobs1.shift(0,-1)
observations = obs.fill(DOWN).is_not_blank().is_not_whitespace().is_number()
observations = observations - noobs1 - noobs2

Dimensions = [
            HDim(ethnicity,'Basis of treatment',DIRECTLY,LEFT),
            HDimConst('Clients in treatment','All young clients'),
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
        'Ethnicity':'ethnicity',
        'White British':'ethnicity/white-british',
        'Other White':'ethnicity/other-white',
        'Not Stated':'ethnicity/not-stated',
        'White Irish':'ethnicity/white-irish',
        'Indian':'ethnicity/indian',
        'Caribbean':'ethnicity/caribbean',
        'White and black Caribbean':'ethnicity/white-and-black-caribbean',
        'Pakistani':'ethnicity/pakistani',
        'Other Asian':'ethnicity/other-asian',
        'Other':'ethnicity/other',
        'Other black':'ethnicity/other-black',
        'African':'ethnicity/african',
        'Other Mixed':'ethnicity/other-mixed',
        'Bangladeshi':'ethnicity/bangladeshi',
        'White and Asian':'ethnicity/white-and-asian',
        'White and black African':'ethnicity/white-and-black-african',
        'Chinese':'ethnicity/chinese',
        'Unknown':'ethnicity/unknown',
        'Inconsistent/missing':'ethnicity/inconsistent/missing',
        'Total':'ethnicity/total'        
        }.get(x, x))

new_table['Period'] = '2017-18'
new_table['Substance'] = 'All'
new_table = new_table[['Period','Basis of treatment','Substance','Clients in treatment','Measure Type','Value','Unit']]

new_table


