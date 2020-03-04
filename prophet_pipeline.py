def pull(ticker):
    """Pulls data of stock using ticker"""
    import pandas as pd
    import numpy as np
    import datetime
    from pandas_datareader import data, wb
    import pandas_datareader.data as web

    now = datetime.datetime.now()
    start_year = int(now.strftime('%Y'))-10
    end_year = int(now.strftime('%Y'))
    day = int(now.strftime('%d'))
    month = int(now.strftime('%m'))
    start = datetime.datetime(start_year, month, day)
    end = datetime.datetime(end_year, month, day)

    df = web.DataReader(f'{ticker}', 'yahoo', start, end)
    df['Company']= f'{ticker}'
    return df

def custodian(df):
    """Cleans dataframe created from the pull function in preparation for Prophet Modeling"""
    import pandas as pd
    import datetime

    df = df.drop(columns=['High', 'Low', 'Open', 'Close', 'Volume'])
    df = df.rename(columns={'Adj Close': 'close'})
    df = df.drop(columns='Company')

    now = datetime.datetime.now()
    start_year = int(now.strftime('%Y'))-10
    end_year = int(now.strftime('%Y'))
    day = int(now.strftime('%d'))
    month = int(now.strftime('%m'))
    start = datetime.datetime(start_year, month, day)
    end = datetime.datetime(end_year, month, day)

    idx = pd.date_range(start, end)
    df = df.reindex(idx, method = 'ffill')
    return df

def prophet(data):
    """takes in df and produces df of results"""
    from fbprophet import Prophet

    data= data.reset_index()
    data= data.rename(columns={'index': 'ds', 'close': 'y'})

    prophet = Prophet(interval_width=0.95)
    prophet.fit(data)
    future = prophet.make_future_dataframe(periods=(365), freq='D')
    forecast = prophet.predict(future)

    results_df = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].iloc[-365:]
    results_df.rename(columns = {'ds':'date', 'yhat': 'predicted', 'yhat_lower': 'lower_bound', 'yhat_upper':'upper_bound'}, inplace=True)
    results_df.set_index('date', inplace=True)

    return results_df

def predict_stock_price(ticker):
    import plotly.graph_objects as go 

    df = pull(ticker)
    clean_df = custodian(df)
    results = prophet(clean_df)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
                x=clean_df.index,
                y=clean_df['close'],
                name = 'Actual Price',
                line_color='dimgray',
                opacity=0.8))

    fig.add_trace(go.Scatter(
                x=results.index,
                y=results['predicted'],
                name = 'Predicted Price',
                line_color='gold',
                opacity=0.8))

    fig.update_layout(title_text="Stock Price", plot_bgcolor='white')
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
    fig.show()

    return results
