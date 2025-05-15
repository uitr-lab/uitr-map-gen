import os, json, io
import pandas as pd
import geopandas as gpd
from pathlib import Path

# import webbrowser

from contextlib import contextmanager

def generate(config, out='./my-map.html'):
    '''
    Generate a map from config. Save as html
    '''




            
        
    def _generate(config, path='./', out='./out.html'):
        print(config)
        # path=os.path.dirname(config_path)
        input=config['input']
        if not input.startswith('/'):
            input = os.path.join(path, input)

        output=out
        geojson_grid='{}'

        if 'grid' in config:
            if os.path.isdir(config['grid']):
                # Assume shapefile here.
                
                

                shp_files = list(Path(config['grid']).glob("*.shp"))
                print(shp_files)

                
                gdf = gpd.read_file(shp_files[0])
                gdf = gdf.to_crs(epsg=4326)
                geojson_grid = gdf.to_json()
                            


        template = os.path.join(os.getcwd(), 'hexmap.template.html')

        with open(template, "r", encoding="utf-8") as template_file:
                template = template_file.read()  # Reads the entire file

                with csv_string(input) as data:
                
                # with open(input, "r", encoding="utf-8") as csv_file:
                #     data = csv_file.read()  # Reads the entire file

                    for key, value in config['map'].items():
                        
                        key=key.replace('-', '_').upper()
                        print(f"{key}:{value}")
                        if key.endswith('_JSON'):
                            key = key.replace('_JSON', '')
                            value=json.dumps(value)
                            
                        template=template.replace(f"{{{{{key}}}}}", value);

                    template=template.replace("{{DATA}}", data).strip()
                    template=template.replace("{{GRID}}", geojson_grid).strip()
                    with open(output, "w", encoding="utf-8") as hexmap_file:
                        hexmap_file.write(template)

    _generate(config, out=out)






    # # Path to your local HTML file
    # file_path = os.path.abspath(out)  # Replace with your actual file
    # webbrowser.open(f"file://{file_path}")









@contextmanager 
def csv_string(file):
    '''
    Read csv or xlsx, but return csv text
    '''
    if file.lower().endswith('.csv'):
        with open(file, "r", encoding="utf-8") as csv_file:
            yield csv_file.read() 
    
    elif file.lower().endswith('.xlsx'):
        buffer = io.StringIO()
        try:
            df = pd.read_excel(file)
            df.to_csv(buffer, index=False)
            buffer.seek(0)  
            yield buffer.read()
        finally:
            buffer.close()
    else:
        raise Exception(f"Unknown format: {file}")