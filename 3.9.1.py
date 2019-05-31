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
            HDim(basis,'Basis of treatment',DIRECTLY,LEFT),
            HDim(sex,'Clients in treatment',DIRECTLY, ABOVE),
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

new_table['Clients in treatment'] = new_table['Clients in treatment'].map(
    lambda x: {
        'Female' : 'female',
        'Male' : 'male',
        'Total' : 'total'
        }.get(x, x))

new_table['Basis of treatment'] = new_table['Basis of treatment'].map(
    lambda x: {
        'Engaged with community mental health team or other mental health services':'mental-health-treatment-need/community-or-other-mental-health-servicess',
        'Mental health treatment from GP':'mental-health-treatment-need/gp',
        'NICE recommended mental health treatment':'nice-recommended-mental-health-treatment',
        'Engaged with Improving Access to Psychological Therapies (IAPT)':'mental-health-treatment-need/improving-access-to-psychological-therapies-iapt',
        'Identified space in a health based place of safety for mental health crises':'mental-health-treatment-need/identified-space-in-a-health-based-place-of-safety-for-mental-health-crises',
        'Total individuals receiving any form of mental health treatment':'mental-health-treatment-need/total-individuals-receiving-any-treatment-for-mental-health',
        'Mental health treatment need identified but no treatment received':'mental-health-treatment-need/no-treatment-received-for-a-mental-health-treatment-need',
        'Total individuals with mental health treatment need':'mental-health-treatment-need/total-individuals-receiving-any-treatment-for-mental-health',
}.get(x, x))

new_table['Basis of treatment'] = new_table['Basis of treatment'] + '-' + new_table['Clients in treatment']

new_table['Period'] = '2017-18'
new_table['Substance'] = 'All'
new_table = new_table[['Period','Basis of treatment','Substance','Clients in treatment','Measure Type','Value','Unit']]

new_table


