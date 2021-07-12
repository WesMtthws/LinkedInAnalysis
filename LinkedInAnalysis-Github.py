#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#imports modules used in this project

import pandas as pd
import altair as alt
import datapane as dp
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
dp.login(token='')


# In[ ]:


network = pd.read_csv('Connections.csv')


# In[ ]:


network_head = network.head(10)
network_head


# In[ ]:


figs = []

figs.append(dp.Markdown('# LinkedIn Network'))
figs.append(dp.Table(network.head(10)))


# In[ ]:


network.info()


# In[ ]:


network_description = network.describe()


# In[ ]:


network['Last Name'] = 'Redacted'
redacted_head = network.head(10)
redacted_head


# In[ ]:


#Converts the date format provided by LinkedIn to a Year-Month format

from datetime import datetime

def convert(date):
    return datetime.strptime(date, "%d-%b-%y").strftime("%Y-%m")

network["Connected On"] = network["Connected On"].apply(convert)


# In[ ]:


#Regroups dataframe by Company
company_groupby = network.groupby(by='Company').count().reset_index().sort_values(by='First Name', ascending=False).reset_index(drop=True)
company_groupby


# In[ ]:


#Regroups dataframe by Date Connected On
date_groupby = network.groupby(by='Connected On').count().reset_index().reset_index(drop=True)
date_groupby = date_groupby.rename(columns={'Position' : 'New Connections'})
date_groupby


# In[ ]:


#Creates chart by New Connections by Date
chart_connected_by_month = alt.Chart(date_groupby).mark_line(color="green", point=True).encode(
    x=alt.X('Connected On', axis=alt.Axis(tickCount=0, grid=False, labelOverlap=True)),
    y=alt.Y('Company'),
    tooltip=['New Connections', 'Connected On']
).interactive()

chart_connected_by_month.encoding.y.title = 'New Connections'

chart_connected_by_month


# In[ ]:


#Reformats the New Connections by Date into a running total sum of connections
date_groupby['c_sum'] = date_groupby['First Name'].cumsum()
print(date_groupby)


# In[ ]:


#Creates Chart of Running Total Sum of Connections
cumsum = alt.Chart(date_groupby).mark_line(color="green", point=True).encode(
    x=alt.X('Connected On', axis=alt.Axis(tickCount=0, grid=False, labelOverlap=True)),
    y='c_sum',
    tooltip=['c_sum', 'Connected On']
).interactive()

cumsum.encoding.y.title = 'Running Total'

cumsum


# In[ ]:


#Creates Chart of Most Represented Companies
network['Company'].value_counts()

company_barchart = px.bar(network.groupby(by='Company').count().sort_values(by='First Name', ascending=False)[:10].reset_index(),
       x='Company',
       y='First Name',
       labels={'First Name': 'Number'},
        title= 'Top Represented Companies in my LinkedIn Network'
      )

company_barchart.update_layout(margin=dict(l=0, r=0, t=35, b=0))
company_barchart.show()


# In[ ]:


#Creates Chart of Most Held Positions
network['Position'].value_counts()

position_barchart = px.bar(network.groupby(by='Position').count().sort_values(by='First Name', ascending=False)[:10].reset_index(),
       x='Position',
       y='First Name',
       labels={'First Name': 'Number'},
        title= 'Most Frequently Held Positions in my LinkedIn Network'
      )

position_barchart.show()


# In[ ]:


#Imports Module for Word cloud and creates function needed to create chart by frequency of terms found in Position Column

positions = ' '.join(network[~network.Position.isnull()].Position.unique())

from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import matplotlib.pyplot as plt
get_ipython().run_line_magic('matplotlib', 'inline')


def make_wordcloud(new_text):
    ''''function to make wordcloud'''
    
    wordcloud = WordCloud(width = 800, height = 800, 
                min_font_size = 10,
                background_color='black', 
                colormap='Set2', 
                collocations=False).generate(new_text) 
    
    #wordcloud.recolor(color_func = grey_color_func)

    
    fig = plt.figure(figsize = (8, 8), facecolor = None) 
    plt.imshow(wordcloud, interpolation='bilinear') 
    plt.axis("off") 
    plt.tight_layout(pad = 0) 

    plt.show() 
    
    return fig


# In[ ]:


#Creates wordcloud from terms found in the "Positions" column
wordcloud = make_wordcloud(positions)
wordcloud


# In[ ]:


#Finds inferred gender by first name
first_names = network['First Name'][0:100]
first_names
listgender = (Genderize().get(first_names))


# In[ ]:


#creates chart based on percentage gender breakdown by month

x = df['Connected On']
y1 = df['pct_female']
y2 = df['pct_male']

fig, ax = plt.subplots(figsize=(25, 6))

ax.set_ylim([0, 100])

plt.xticks(rotation=45)
ax.set_yticks([10, 30, 50, 70, 90], minor=True)

    
plt.plot(x, y1,"-r", label="pct_female")
plt.plot(x, y2,"-b", label="pct_male")

plt.grid(b=True, which='both', color='0.65', linestyle='-')

n = 4  # Keeps every 7th label
[l.set_visible(False) for (i,l) in enumerate(ax.xaxis.get_ticklabels()) if i % n != 0]
        
plt.legend(prop={'size': 20})
plt.rcParams.update({'font.size': 20})

plt.plot

fig


# In[ ]:


#Used in interactivity of Company Treemap - Creates new column of first names by company

company_groupby
for company_index, company_row in company_groupby.iterrows():
    company_connections = []
    for index, row in network.iterrows():
        if (row["Company"]) == company_row["Company"]:
            company_connections.append(row["First Name"])
    print(company_connections)
    company_groupby.at[company_index,'Company Connections'] = company_connections


# In[ ]:


company_groupby


# In[ ]:


#Reformats column of first names to be usable by interactive treemap
i = 6

for company_index, company_row in company_groupby.iterrows():
    while i < len(company_row['Company Connections']):
        company_row['Company Connections'].insert(i, '<br>')
        i += 7
    i = 6

print(company_groupby)

company_groupby['Company Connections'] = company_groupby['Company Connections'].str.join(", ")
company_groupby


# In[ ]:


#Creates treemap by frequency of company
company_treemap = px.treemap(company_groupby[:-1], path=['Company', 'Position'],
          values='First Name',
          labels={'First Name': 'Number'},
                hover_data=company_groupby.columns)

company_treemap.update_layout(margin=dict(l=0, r=0, t=0, b=0))

company_treemap


# In[ ]:


#Creates Datapane Report
report = dp.Report(
  dp.DataTable(redacted_head, caption='Dataset for LinkedIn Network', name='redacted-head'),
    dp.DataTable(network_description, caption='A Description of Data Found', name='network-description'),
    dp.Plot(chart_connected_by_month, name='connected-month'),
    #dp.Plot(chart_connected_by_month2, name='connected-month2'),
    dp.Plot(cumsum, name='cumsum'),
    dp.Plot(company_barchart, name='company-barchart'),
    dp.Plot(company_treemap, name="treemap"),
    dp.Plot(position_barchart, name='position-barchart'),
    dp.File(wordcloud, name='wordcloud'),
    dp.Plot(fig, name='gender'),
    type=dp.ReportType.ARTICLE
)

report.preview()


# In[ ]:


#Publishes report to Datapane
report.publish(name='linkedin_network', open=True, visibility=dp.Visibility.PUBLIC)

