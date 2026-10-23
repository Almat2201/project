"""Execute mapping, proximity, dashboard callback and predictive-model checks."""
from pathlib import Path
from math import radians,sin,cos,sqrt,atan2
import json
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import folium
from folium.plugins import MarkerCluster,MousePosition
from sklearn.model_selection import train_test_split,GridSearchCV
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import ConfusionMatrixDisplay,confusion_matrix
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import interactive_dashboard as dashboard

root=Path(__file__).resolve().parent
geo=pd.read_csv(root/'spacex_launch_geo.csv')
site_map=folium.Map(location=[29.5,-95],zoom_start=4)
sites=geo.groupby('Launch Site')[['Lat','Long']].first()
for name,row in sites.iterrows():
    folium.Circle([row.Lat,row.Long],radius=1000,color='#24528c',fill=True,popup=name).add_to(site_map)
    folium.Marker([row.Lat,row.Long],tooltip=name).add_to(site_map)
cluster=MarkerCluster(name='Launch outcomes').add_to(site_map)
for _,row in geo.iterrows():
    folium.Marker([row.Lat,row.Long],popup=f"{row['Launch Site']}: {'Success' if row['class']==1 else 'Failure'}",
                  icon=folium.Icon(color='green' if row['class']==1 else 'red')).add_to(cluster)
MousePosition().add_to(site_map)
coast=[28.56367,-80.57163]  # Coastline reference explicitly supplied in course notebook.
site=sites.loc['CCAFS LC-40']
lat1,lon1,lat2,lon2=map(radians,[site.Lat,site.Long,*coast])
a=sin((lat2-lat1)/2)**2+cos(lat1)*cos(lat2)*sin((lon2-lon1)/2)**2
distance=6373*2*atan2(sqrt(a),sqrt(1-a))
folium.Marker(coast,popup=f'Course coastline reference: {distance:.3f} km from CCAFS LC-40',
              icon=folium.Icon(color='blue')).add_to(site_map)
folium.PolyLine([[site.Lat,site.Long],coast],weight=3,tooltip=f'{distance:.3f} km').add_to(site_map)
site_map.save(root/'launch_map.html')

for site_name in ['ALL',*dashboard.data['Launch Site'].unique()]:
    assert len(dashboard.get_pie_chart(site_name).data)>0
    scatter=dashboard.get_scatter_chart(site_name,[0,10000])
    assert len(scatter.data)>0
    restricted=dashboard.get_scatter_chart(site_name,[2000,5000])
    for trace in restricted.data:
        assert all(2000<=v<=5000 for v in trace.x)

X=pd.read_csv(root/'features.csv')
y=pd.read_csv(root/'dataset_part_2.csv')['Class']
X_train,X_test,y_train,y_test=train_test_split(X,y,test_size=.2,random_state=2)
model_specs={
    'Logistic Regression':(LogisticRegression(max_iter=2000),{'logisticregression__C':[.01,.1,1,10]}),
    'SVM':(SVC(),{'svc__C':[.1,1,10],'svc__kernel':['linear','rbf']}),
    'Decision Tree':(DecisionTreeClassifier(random_state=2),{'decisiontreeclassifier__max_depth':[2,4,8,None]}),
    'KNN':(KNeighborsClassifier(),{'kneighborsclassifier__n_neighbors':[3,5,7]})}
scores={}
fig,axes=plt.subplots(2,2,figsize=(10,8))
for ax,(name,(model,grid)) in zip(axes.flat,model_specs.items()):
    search=GridSearchCV(make_pipeline(StandardScaler(),model),grid,scoring='accuracy',cv=5)
    search.fit(X_train,y_train)
    scores[name]={'cv_accuracy':float(search.best_score_),'test_accuracy':float(search.score(X_test,y_test)),
                  'best_parameters':search.best_params_, 'confusion_matrix':confusion_matrix(y_test,search.predict(X_test)).tolist()}
    ConfusionMatrixDisplay.from_estimator(search,X_test,y_test,ax=ax,colorbar=False)
    ax.set_title(name)
fig.tight_layout();fig.savefig(root/'model_confusion_matrices.png',dpi=130);plt.close(fig)
summary={'launch_sites':len(sites),'launch_markers':len(geo),'coastline_distance_km':distance,
         'dashboard_callbacks':'All four sites and ALL tested, including payload filtering',
         'train_shape':list(X_train.shape),'test_shape':list(X_test.shape),'models':scores,
         'launch_site_summary':dashboard.data.groupby('Launch Site')['class'].agg(['sum','count','mean']).to_dict('index')}
(root/'remaining_verification.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps(summary,indent=2))
