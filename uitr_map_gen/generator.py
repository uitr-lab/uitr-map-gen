import os, json, io
import pandas as pd
import geopandas as gpd
from pathlib import Path
from pyproj import Transformer
import zipfile
import numpy as np

# import webbrowser

from contextlib import contextmanager

def generate(config, out='./my-map.html'):
    '''
    Generate a map from config. Save as html
    '''




            
        
    def _generate(config, path='./', out='./out.html'):
        print(config)
        
        from importlib.metadata import version 
        print(f'Version: {version("uitr-map-gen")}')
        
        # path=os.path.dirname(config_path)
        input=None
        if 'input' in config:
            input=config['input']
            if isinstance(input, str) and not input.startswith('/'):
                input = os.path.join(path, input)

        output=out
        csv_data='';
        geojson_grid='{}';

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

        if input is not None:
            with csv_string(input) as data:
                
                csv_data=data
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

                        csv_data = csv_buffer.getvalue()
                        # with open(input, "r", encoding="utf-8") as csv_file:
                        #     data = csv_file.read()  # Reads the entire file
    
        for key, value in config['map'].items():
            
            key=key.replace('-', '_').upper()
            print(f"{key}:{value}")
            if key.endswith('_JSON'):
                key = key.replace('_JSON', '')
                value=json.dumps(value)    
            template=template.replace(f"{{{{{key}}}}}", value);


        template=template.replace("{{DATA}}", csv_data).strip()
        template=template.replace("{{GRID}}", geojson_grid).strip()
        
        
        
        geojson_list=[]
        if isinstance(config['base-layers'], dict):
            pass
        if isinstance(config['base-layers'], list):
            for kmz_path in config['base-layers']:
                
                if isinstance(kmz_path, list):
                    sub_list=[]
                    for p in kmz_path:
                        sub_list.append(read_spatial_file(p))
                        
                    geojson_list.append(sub_list)
                    print(f'Append geojson list: ')
                else:
                
                    print(f'{kmz_path}') 
                    geojson_list.append(read_spatial_file(kmz_path))
                    print(f'Append geojson: ')
                    
        
    
        geojson_base = json.dumps(geojson_list, indent=3)
                
        template=template.replace("{{BASE}}", geojson_base).strip()      
        
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




def read_spatial_file(spatial_file_path:str):
    
    if spatial_file_path.lower().endswith('shp'):
                
        gdf = gpd.read_file(spatial_file_path)
        gdf = gdf.to_crs(epsg=4326)
        return json.loads(gdf.to_json())
    
    
    if spatial_file_path.lower().endswith('gpx'):
        gdf = gpd.read_file(spatial_file_path, driver="GPX", layer='track_points')
        gdf = gdf.to_crs(epsg=4326)
        
        for col in gdf.columns:
            print(f"{col} {gdf[col].dtype}")
            if pd.api.types.is_datetime64_any_dtype(gdf[col]):
                # convert to ISO8601 string (preserves timezone info)
                gdf[col] = gdf[col].astype(str)
                
                
                
        from shapely.geometry import mapping, LineString

        # Assuming gdf is the track_points layer
        lines = []
        for (track_id, seg_id), group in gdf.groupby(["track_fid", "track_seg_id"]):
            # Sort points by their index in the segment
            group = group.sort_values("track_seg_point_id")
            
            # Build coordinates
            coords = [(pt.x, pt.y) for pt in group.geometry]
            
            # Make LineString
            line = LineString(coords)
            
            # Optional: add properties (track ID, segment ID, type, name, etc.)
            props = {
                "track_fid": int(track_id),
                "track_seg_id": int(seg_id),
                "name": group["name"].iloc[0] if "name" in group.columns else None,
                "type": group["type"].iloc[0] if "type" in group.columns else None
            }
            
            lines.append({
                "type": "Feature",
                "geometry": mapping(line),
                "properties": props
            })

        json_gpx = {"type": "FeatureCollection", "features": lines}

        # gdf['time']= gdf['time'].dt.strftime('%m/%d/%Y %H:%M:%S')
        # json_gpx = json.loads(gdf.to_json())
            
        with open(spatial_file_path.replace('.gpx', '.json'), "w") as f:
            json.dump(json_gpx, f)
        
        return json_gpx
        
    
    kml_path = "default.kml"

    with zipfile.ZipFile(spatial_file_path, 'r') as kmz:
        # KMZ usually contains a single KML file
        for name in kmz.namelist():
            if name.endswith(".kml"):
                kmz.extract(name, ".")
                kml_path = name
                print(f'{kml_path}') 
                break

    # Read KML into GeoDataFrame
    gdf = gpd.read_file(kml_path, driver='KML')

    # Export to GeoJSON
    gdf = gdf.to_crs(epsg=4326)
    return json.loads(gdf.to_json())




@contextmanager 
def csv_string(file):
    '''
    Read csv or xlsx, but return csv text
    '''
    
    if isinstance(file, pd.DataFrame):
        buffer = io.StringIO()
        try:
            df =file
            df.to_csv(buffer, index=False)
            buffer.seek(0)  
            yield buffer.read()
        finally:
            buffer.close()
        
        return
    
    
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