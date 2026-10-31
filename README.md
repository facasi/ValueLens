# ValueLens

Aplicación de análisis value investing con Streamlit.

## En tu computadora

```bash
python3 -m pip install -r requirements.txt
python3 -m streamlit run app.py
```

## Publicar en navegador

1. Crea un repositorio en GitHub y sube `app.py`, `valuation.py` y `requirements.txt` a la raíz.
2. Accede a https://share.streamlit.io/ e inicia sesión con GitHub.
3. Pulsa **Create app** y selecciona el repositorio, rama principal y archivo `app.py`.
4. Publica la aplicación y utiliza la URL que Streamlit te asigne.

Necesita conexión a Internet. Yahoo Finance puede limitar o alterar sus datos; algunos indicadores pueden faltar. El cálculo DCF utiliza supuestos ajustables y no es una recomendación de inversión.
