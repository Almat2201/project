"""Reproducible computations supporting the Capstone intermediate checks."""
from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parent
raw = pd.json_normalize(json.loads((ROOT/'api-snapshot.json').read_text()))
reference = pd.read_csv(ROOT/'dataset_part_1.csv')
# The live metadata endpoint currently returns non-JSON. Use the course's
# published Falcon 9 reference dataset to identify its rocket id by launch date.
dates = pd.to_datetime(raw['date_utc']).dt.date
known_f9_dates = set(pd.to_datetime(reference['Date']).dt.date)
rocket_ids = raw.loc[dates.isin(known_f9_dates), 'rocket'].unique()
assert len(rocket_ids) == 1
falcon9 = raw.loc[raw['rocket'].eq(rocket_ids[0]) & raw['cores'].map(len).eq(1)
                 & raw['payloads'].map(len).eq(1)
                 & dates.le(pd.Timestamp('2020-11-13').date())].copy()
assert len(falcon9) == len(reference)
landing_pads = falcon9['cores'].map(lambda values: values[0]['landpad'])
data = reference.copy()
data['PayloadMass'] = data['PayloadMass'].fillna(data['PayloadMass'].mean())
data['Class'] = data['Outcome'].str.startswith('True').astype(int)
data.to_csv(ROOT/'dataset_part_2.csv',index=False)
report = {
    'first_static_fire_year': int(pd.to_datetime(raw.static_fire_date_utc.iloc[0]).year),
    'falcon9_launches': len(falcon9),
    'missing_landing_pads': int(landing_pads.isna().sum()),
    'launches_per_site': data.LaunchSite.value_counts().to_dict(),
    'launches_per_orbit': data.Orbit.value_counts().to_dict(),
    'outcomes_per_orbit': {f'{orbit} | {outcome}': int(count)
                           for (orbit,outcome),count in data.groupby(['Orbit','Outcome']).size().items()},
    'landing_outcomes': data.Outcome.value_counts().to_dict(),
    'landing_successes': int(data.Class.sum()),
    'landing_success_rate': float(data.Class.mean()),
    'payload_missing_after_imputation': int(data.PayloadMass.isna().sum()),
    'metadata_note': 'Rocket id identified using launch dates from the official course Falcon 9 reference CSV; live metadata endpoint returned non-JSON.'
}
(ROOT/'verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
