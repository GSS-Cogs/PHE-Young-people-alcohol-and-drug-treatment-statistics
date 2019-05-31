# -*- coding: utf-8 -*-
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

# Table 3.5.1: Education and employment status of all young people starting treatment 2017-18

from gssutils import *
scraper = Scraper('https://www.gov.uk/government/statistics/substance-misuse-treatment-for-young-people-statistics-2017-to-2018')
dist = scraper.distribution(title=lambda t: t.startswith('Data tables'))
tabs = {tab.name: tab for tab in dist.as_databaker()}
tab = tabs['3.5.1 Education & Employment']

cell = tab.filter('Education and employment status')
cell.assert_one()
education = cell.fill(DOWN).is_not_blank().is_not_whitespace() 
obs = tab.fill(RIGHT).one_of(['n'])
noobs1 = tab.filter('Missing or inconsistent data').fill(RIGHT)
noobs2 = noobs1.shift(0,-1)
observations = obs.fill(DOWN).is_not_blank().is_not_whitespace().is_number()
observations = observations - noobs1 - noobs2

Dimensions = [
            HDimConst('Substance','All'),
            HDim(education,'Basis of treatment',DIRECTLY,LEFT),
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

new_table['Basis of treatment'] = new_table['Basis of treatment'].str.lower()

new_table['Basis of treatment'] = new_table['Basis of treatment'].map(
    lambda x: {
        'Total' : 'All',
        'mainstream education':'mainstream-education',
        'not in employment or education or training (neet)':'not-in-employment-or-education-or-training-',
        'apprenticeship or training':'apprenticeship-or-training',
        'persistent absentee or excluded':'persistent-absentee-or-excluded',
        'economically inactive – health issue or caring role':'economically-inactive-health-issue-or-caring-role',
        'voluntary work':'voluntary-work',
        ' alternative education':'alternative-education',
        ' total new presentations':'total-new-presentations'}.get(x, x))

new_table['Basis of treatment'] = 'education-and-employment-status/' + new_table['Basis of treatment']

new_table['Clients in treatment'] = 'All young clients'

new_table['Period'] = '2017-18'
new_table = new_table[['Period','Basis of treatment','Substance','Clients in treatment','Measure Type','Value','Unit']]

new_table
