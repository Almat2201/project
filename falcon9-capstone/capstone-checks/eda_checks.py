"""Execute EDA, feature engineering, and SQL-extension checkpoint operations."""
from pathlib import Path
import json
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from IPython.core.interactiveshell import InteractiveShell

root=Path(__file__).resolve().parent
data=pd.read_csv(root/'dataset_part_2.csv')
fig,axes=plt.subplots(2,2,figsize=(14,10))
for ax,(x,y) in zip(axes.flat,[('FlightNumber','LaunchSite'),('PayloadMass','LaunchSite'),('FlightNumber','Orbit'),('PayloadMass','Orbit')]):
    sns.scatterplot(data=data,x=x,y=y,hue='Class',palette={0:'#b94735',1:'#18857c'},ax=ax)
    ax.set_title(f'{x} and {y}, by landing outcome')
fig.tight_layout(); fig.savefig(root/'parameter_relationships.png',dpi=130); plt.close(fig)
data['Year']=pd.to_datetime(data.Date).dt.year
annual=data.groupby('Year').Class.mean()
ax=annual.plot(marker='o',title='Falcon 9 Yearly Landing Success Rate',ylim=(0,1.05),ylabel='Success rate')
ax.figure.tight_layout(); ax.figure.savefig(root/'annual_success.png',dpi=140); plt.close(ax.figure)
features=data[['FlightNumber','PayloadMass','Orbit','LaunchSite','Flights','GridFins','Reused','Legs','LandingPad','Block','ReusedCount','Serial']]
features=pd.get_dummies(features,columns=['Orbit','LaunchSite','LandingPad','Serial']).astype(float)
features.to_csv(root/'features.csv',index=False)

# Use the actual IPython SQL extension, SQLite connection and SQL magic.
shell=InteractiveShell.instance()
shell.run_line_magic('load_ext','sql')
shell.run_line_magic('sql',f'sqlite:///{(root/"spacex.db").as_posix()}')
shell.run_line_magic('config',"SqlMagic.style = 'DEFAULT'")
query_results={}
for name,query in {
    'unique_sites':'SELECT DISTINCT Launch_Site FROM SPACEXTBL',
    'sample_cca':"SELECT * FROM SPACEXTBL WHERE Launch_Site LIKE 'CCA%' LIMIT 5",
    'total_payload':'SELECT SUM(PAYLOAD_MASS__KG_) AS Total_Payload_Mass FROM SPACEXTBL',
    'minimum_payload':'SELECT MIN(PAYLOAD_MASS__KG_) FROM SPACEXTBL',
    'mission_counts':'SELECT Launch_Site,COUNT(Mission_Outcome) FROM SPACEXTBL GROUP BY Launch_Site'
}.items():
    rows=shell.run_line_magic('sql',query)
    query_results[name]=[list(row) for row in rows]
(root/'eda_verification.json').write_text(json.dumps({'feature_shape':list(features.shape),'annual_success':annual.to_dict(),'sql_magic_results':query_results},indent=2),encoding='utf-8')
print('Completed: SQL extension and queries; four relationship plots; annual success trend; categorical dummy features',features.shape)
