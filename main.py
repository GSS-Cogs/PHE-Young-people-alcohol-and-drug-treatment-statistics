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

# # Alcohol and drug treatment data for under-18s from PHE’s national drug treatment monitoring system (NDTMS)

from gssutils import *
scraper = Scraper('https://www.gov.uk/government/statistics/substance-misuse-treatment-for-young-people-statistics-2017-to-2018')
dist = scraper.distribution(title=lambda t: t.startswith('Data tables'))
tabs = {tab.name: tab for tab in dist.as_databaker()}
tabs.keys()


# +
# %%capture

def process_tab(t):
    %run "$t"
    return new_table

observations = pd.concat(process_tab(f"{t[:len('1.1.1')]}.py") for t in tabs.keys() if t != 'Index')
# -

observations['Period'] = observations['Period'].map(
    lambda x: f'gregorian-interval/{str(x)[:4]}-03-31T00:00:00/P1Y')


observations.rename(columns={'Substance': 'Substance type'}, inplace=True)
observations = observations.drop("Clients in treatment", axis=1)

out = Path('out')
out.mkdir(exist_ok=True)
observations.drop_duplicates().to_csv(out / 'observations.csv', index = False)

# +
scraper.dataset.family = 'health'
scraper.dataset.theme = THEME['health-social-care']
with open(out / 'dataset.trig', 'wb') as metadata:
    metadata.write(scraper.generate_trig())

schema = CSVWMetadata('https://gss-cogs.github.io/ref_alcohol/')
schema.create(out / 'observations.csv', out / 'observations.csv-schema.json')
# -


