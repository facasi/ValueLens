import math
import pandas as pd
import streamlit as st
import yfinance as yf
from valuation import dcf_per_share, score

st.set_page_config(page_title='ValueLens | Value Investing',page_icon='📈',layout='wide')
st.title('📈 ValueLens — Value Investing')
st.caption('Análisis fundamental orientativo. Datos de Yahoo Finance; no constituye asesoramiento financiero.')

def num(obj,key):
    try:
        value=float(obj.get(key))
        return value if math.isfinite(value) else None
    except (ValueError,TypeError):
        return None

def fmt(value,percent=False):
    if value is None: return 'N/D'
    return f'{value:.1%}' if percent else f'{value:,.2f}'

@st.cache_data(ttl=900,show_spinner=False)
def fetch(ticker):
    asset=yf.Ticker(ticker)
    return asset.info

with st.sidebar:
    st.header('Configuración')
    ticker=st.text_input('Ticker',value='GOOGL').strip().upper()
    years=st.slider('Horizonte DCF (años)',3,10,5)
    discount=st.slider('Tasa de descuento (%)',6.0,25.0,11.0,0.5)/100
    terminal_growth=st.slider('Crecimiento perpetuo (%)',0.0,5.0,2.5,0.5)/100
    margin_safety=st.slider('Margen de seguridad (%)',15,40,25)/100
    growth_override=st.number_input('Crecimiento anual FCF estimado (%)',min_value=-30.0,max_value=40.0,value=7.0,step=1.0)/100
    st.caption('Los supuestos de crecimiento son editables y no representan pronósticos verificados.')

if not ticker: st.warning('Introduce un ticker.');st.stop()
try:
    with st.spinner('Consultando datos...'):
        info=fetch(ticker)
except Exception as exc:
    st.error(f'No se pudieron consultar los datos para {ticker}. Inténtalo más tarde. Detalle: {exc}')
    st.stop()
if not info or not info.get('symbol') and not info.get('shortName'):
    st.error('No se encontraron datos para este ticker.');st.stop()

st.subheader(f"{info.get('longName') or info.get('shortName') or ticker} ({ticker})")
price=num(info,'currentPrice') or num(info,'regularMarketPrice')
currency=info.get('currency','USD')
pe=num(info,'trailingPE'); forward_pe=num(info,'forwardPE');roe=num(info,'returnOnEquity')
roic=num(info,'returnOnCapital');fcf=num(info,'freeCashflow');shares=num(info,'sharesOutstanding')
debt=num(info,'totalDebt');cash=num(info,'totalCash');debt_equity=num(info,'debtToEquity')
cols=st.columns(4)
for col,(label,val) in zip(cols,[('Precio',fmt(price)),('P/E',fmt(pe)),('Forward P/E',fmt(forward_pe)),('ROE',fmt(roe,True))]):
    col.metric(label,val)
st.caption(f'Moneda de cotización reportada: {currency}. Algunos indicadores pueden no estar disponibles.')

st.header('Valoración por flujo de caja descontado (DCF)')
if fcf is None or shares is None or shares<=0:
    st.warning('No hay FCF o acciones en circulación suficientes para calcular un DCF confiable. No se inventan datos.')
elif fcf<=0:
    st.warning('El flujo de caja libre es negativo o cero: el DCF simplificado no es adecuado en estas condiciones.')
else:
    net_debt=(debt or 0)-(cash or 0) if debt is not None and cash is not None else 0
    if debt is None or cash is None: st.warning('Deuda o efectivo no disponible; se usa deuda neta 0 como supuesto provisional.')
    scenarios={'Conservador':growth_override-0.04,'Base':growth_override,'Optimista':growth_override+0.04}
    results=[]
    for name,growth in scenarios.items():
        intrinsic=dcf_per_share(fcf,growth,discount,terminal_growth,years,shares,net_debt)
        results.append({'Escenario':name,'Crecimiento FCF':f'{growth:.1%}','Valor intrínseco':round(intrinsic,2) if intrinsic is not None else None,'Precio con margen de seguridad':round(intrinsic*(1-margin_safety),2) if intrinsic is not None else None})
    st.dataframe(pd.DataFrame(results),hide_index=True,use_container_width=True)
    base=results[1]['Valor intrínseco']
    upside=(base/price-1) if base is not None and price and price>0 else None
    st.metric('Potencial estimado (escenario base)',fmt(upside,True))
    st.caption('Modelo simplificado de FCF constante en crecimiento. El resultado es muy sensible a sus supuestos.')

st.header('Indicadores de calidad y puntuación')
margin=(base/price-1) if 'base' in locals() and base is not None and price and price>0 else None
rating,count=score(pe,forward_pe,roe,roic,debt_equity,fcf,margin)
st.metric('ValueLens Score',f'{rating}/100' if rating is not None else 'N/D')
st.caption(f'Indicadores evaluados: {count}/7. La puntuación es una heurística, no una recomendación de compra.')
indicators={'P/E':pe,'Forward P/E':forward_pe,'ROE':roe,'ROIC':roic,'Deuda / patrimonio (Yahoo)':debt_equity,'Free Cash Flow':fcf,'Acciones en circulación':shares,'Deuda total':debt,'Efectivo':cash}
st.dataframe(pd.DataFrame([{'Indicador':k,'Valor':fmt(v, k in ('ROE','ROIC'))} for k,v in indicators.items()]),hide_index=True,use_container_width=True)
st.download_button('Exportar indicadores CSV',pd.DataFrame([{'ticker':ticker,'indicador':k,'valor':v} for k,v in indicators.items()]).to_csv(index=False).encode('utf-8'),file_name=f'{ticker}_valuelens.csv',mime='text/csv')
st.info('Verifica las cifras contra los informes oficiales de la empresa antes de tomar decisiones de inversión.')
