from flask import Flask,render_template

import pandas as pd
import numpy as np

from sqlalchemy import create_engine
import pymysql

from bokeh.models import ColumnDataSource
from bokeh.resources import INLINE
from bokeh.embed import components
from bokeh.plotting import figure, output_file, show
from bokeh.layouts import column


app = Flask(__name__)

#df = pd.read_csv('Data_Terminals.csv')

# connect to MySQL database
try:
    db_connection_str = 'mysql+pymysql://root:1qaz!QAZ@localhost/terminals'
    db_connection = create_engine(db_connection_str)
except Exception as e:
    print(e)
    exit()


# insert data into dataframe
df = pd.read_sql('SELECT * FROM terminals.data_terminals', con=db_connection)


def switchFunc(t1,t2,t3,t4,t5):
    switch = None
    # if all values are 0, then terminals connected to switch are not reachable (0)
    if t1 == 0 and t2 == 0 and t3 == 0 and t4 == 0 and t5 == 0:
        switch = 0
    else:
        switch = 1
    return switch


# check row by row
df['switch'] = df.apply(lambda row : switchFunc(row['T1(Terminal 1)'], row['T2(Terminal 2)'],
                                                row['T3(Terminal 3)'],row['T4(Terminal 4)'],
                                                row['T5(Terminal 5)']), axis = 1)

# insert switch (column) into terminals table
try:
    df.to_sql('data_terminals', db_connection, index=False, if_exists='replace')
except Exception as e:
    print("inserting terminals failed")
    print(e)


# convert timestamp to datetime
df['TS(Unix Timestamp)'] = pd.to_datetime(df['TS(Unix Timestamp)'],unit='s')

# group by switches (S1,S2,S3)
df_sw_s1 =df.loc[df['SW(Switch Lable)'] == 'S1']
df_sw_s2 =df.loc[df['SW(Switch Lable)'] == 'S2']
df_sw_s3 =df.loc[df['SW(Switch Lable)'] == 'S3']


def chart(source_data,name):
    source = ColumnDataSource(source_data)
    fig = figure(x_axis_type="datetime", title=name, plot_width=1000, plot_height=300)
    fig.xgrid.grid_line_color = None
    fig.ygrid.grid_line_alpha = 0.5
    fig.xaxis.axis_label = 'Time'
    fig.line('TS(Unix Timestamp)', 'switch', source=source)
    return fig


@app.route('/')
def index():
    s1 = chart(df_sw_s1,"SW-S1 Ping Availability")
    s2 = chart(df_sw_s2, "SW-S2 Ping Availability")
    s3 = chart(df_sw_s3, "SW-S3 Ping Availability")

    script, div = components(column(s1, s2, s3))

    return render_template(
        'index.html',
        plot_script=script,
        plot_div=div,
        js_resources=INLINE.render_js(),
        css_resources=INLINE.render_css(),
    ).encode(encoding='UTF-8')


@app.route('/alert')
def alert():
    df_alert = df[(df["switch"] == 0)]
    df_alert = pd.DataFrame(df_alert, columns=['SW(Switch Lable)',
                                                   'TS(Unix Timestamp)'])
    no = np.arange(df_alert.shape[0])
    df_alert.insert(0, 'No', no)
    df_alert['Alert Type'] = 'Ping Lost'
    df_alert.set_index('No')

    return render_template("alert.html", data=df_alert.to_html())


if __name__=='__main__':
    app.run(debug=True)