import os, json, io
import pandas as pd
import geopandas as gpd
from pathlib import Path
from pyproj import Transformer


# import webbrowser

from contextlib import contextmanager

def generate(config, out='./my-map.html'):
    '''
    Generate a map from config. Save as html
    '''




            
        
    def _generate(config, path='./', out='./out.html'):
        print(config)
        
        from importlib.metadata import version 
        print(version("uitr-map-gen"))
        
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
                            
        from importlib.resources import files

        template = files("uitr_map_gen").joinpath("hexmap.template.html")
        template = template.read_text(encoding="utf-8")
        # template = os.path.join(os.path.dirname(__file__), 'hexmap.template.html')

        # with open(template, "r", encoding="utf-8") as template_file:
        #         template = template_file.read()  # Reads the entire file

        with csv_string(input) as data:
            
            
            if "fields" in config:
                config['map']['options-json']['fields']=config['fields']
                
                
                if 'crs' in config['fields']:
                    
                    df = pd.read_csv(io.StringIO(data))
            
                    # print(df.iloc[0])
                   
                    transformer = Transformer.from_crs(config['fields']['crs'], "EPSG:4326", always_xy=True)
                    source = config['fields']['source']
                    df[[source['x'], source['y']]] = df.apply(lambda row: pd.Series(transformer.transform(row[source['x']], row[source['y']])), axis=1)
                    dest = config['fields']['dest']
                    df[[dest['x'], dest['y']]] = df.apply(lambda row: pd.Series(transformer.transform(row[dest['x']], row[dest['y']])), axis=1)

                    csv_buffer = io.StringIO()
                    df.to_csv(csv_buffer, index=False)

                    data = csv_buffer.getvalue()
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
            
            
            
            
            js = files("uitr_map_gen").joinpath("form.js")
            js = js.read_text(encoding="utf-8")
            
            style = files("uitr_map_gen").joinpath("style.css")
            style = style.read_text(encoding="utf-8")
            
            template=template.replace("{{STYLE}}", style).strip()
            template=template.replace("{{SCRIPT}}", js).strip()
            
            
            
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
    if not os.path.exists(file):
        file=os.path.realpath(file)
        raise Exception(f"File Not Found: {file}")
    
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