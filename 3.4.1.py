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

# Table 3.4.1: Source of referral of all treatment episodes 2017-18

from gssutils import *
scraper = Scraper('https://www.gov.uk/government/statistics/substance-misuse-treatment-for-young-people-statistics-2017-to-2018')
dist = scraper.distribution(title=lambda t: t.startswith('Data tables'))
tabs = {tab.name: tab for tab in dist.as_databaker()}
tab = tabs['3.4.1 Referral Source']

cell = tab.filter('Referral Source')
cell.assert_one()
referral = cell.fill(DOWN).is_not_blank().is_not_whitespace() 
obs = tab.fill(RIGHT).one_of(['n'])
noobs1 = tab.filter('Missing or inconsistent data').fill(RIGHT)
noobs2 = noobs1.shift(0,-1)
observations = obs.fill(DOWN).is_not_blank().is_not_whitespace().is_number()
observations = observations - noobs1 - noobs2

Dimensions = [
            HDimConst('Substance','All'),
            HDim(referral,'Basis of treatment',DIRECTLY,LEFT),
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

new_table['Basis of treatment'] = new_table['Basis of treatment'].str.lower()

new_table['Basis of treatment'] = new_table['Basis of treatment'].map(
    lambda x: {
        'total (episodes)' : 'all',
         'a&e' : 'a-and-e',
        'youth / criminal justice total' : 'youth-criminal-justice-total',        
        'relative, family, friend or concerned other' : 'relative-family-friend-or-concerned-other' ,
       'self, family & friends total' : 'self-family-and-friends-total', 
        'mainstream education' : 'mainstream-education', 
        'alternative education':'alternative-education',
        'education service and other':'education-service-and-other',
        'yp secure estate':'yp-secure-estate',
        'children and family services':'children-and-family-services',
        'social services':'social-services',
        'relative-family-friend-or-concerned-other':'relative-family-friend-or-concerned-other',
        'self-family-and-friends-total':'self-family-and-friends-total',
        'school nurse':'school-nurse',
        'yp housing':'yp-housing',
        'education total':'education-total',
        'other':'other',
        'looked after child services':'looked-after-child-services',
        'social care total':'social-care-total',
        'substance misuse total':'substance-misuse-total',
        'health total':'health-total'}.get(x, x))

new_table['Basis of treatment'] = 'referral-source/' + new_table['Basis of treatment']

new_table['Clients in treatment'] = 'All young clients'

new_table['Period'] = '2017-18'
new_table = new_table[['Period','Basis of treatment','Substance','Clients in treatment','Measure Type','Value','Unit']]

new_table


