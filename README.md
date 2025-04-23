PASOS PARA REPRODUCIR LOS DATOS INCLUIDOS EN LA RECLAMACION

Testado en Ubuntu 24.04

1. Instalar dependencias
```
python3 -m venv pdfvenv
source pdfvenv/bin/activate
pip install -r requirements.txt
```
2. Descargar facturas desde google drive
```
bash descargar_facturas.sh
```
3. Extraer datos de consumo de las facturas descargadas a un archivo .csv
```
python extractraer_datos_consumo.py facturas_fenie_energia
```
Este comando generará un archivo `consumo.csv` con los datos del consumo eléctrico correspondientes a cada factura.

4. El notebook `analisis_facturas.ipynb` contiene el código para generar los datos mensuales medios de consumo y gráficas usadas en la reclamación. Puede visualizarse en github directamente abriendo el archivo.Para ejecutar las celdas ábralo con su herramienta preferida o, alternativamente, puede abrirlo en google colab:
https://colab.research.google.com/github/EloyRC/analisis-facturas-reclamacion/blob/main/analisis_facturas.ipynb


