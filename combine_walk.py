import os
import pathlib
import sys
import numpy as np
import pandas as pd


def output_gpx(points, output_filename):
    """
    Output a GPX file with latitude and longitude from the points DataFrame.
    """
    from xml.dom.minidom import getDOMImplementation, parse
    xmlns = 'http://www.topografix.com/GPX/1/0'
    
    def append_trkpt(pt, trkseg, doc):
        trkpt = doc.createElement('trkpt')
        trkpt.setAttribute('lat', '%.10f' % (pt['lat']))
        trkpt.setAttribute('lon', '%.10f' % (pt['lon']))
        time = doc.createElement('time')
        time.appendChild(doc.createTextNode(pt['datetime'].strftime("%Y-%m-%dT%H:%M:%SZ")))
        trkpt.appendChild(time)
        trkseg.appendChild(trkpt)

    doc = getDOMImplementation().createDocument(None, 'gpx', None)
    trk = doc.createElement('trk')
    doc.documentElement.appendChild(trk)
    trkseg = doc.createElement('trkseg')
    trk.appendChild(trkseg)

    points.apply(append_trkpt, axis=1, trkseg=trkseg, doc=doc)

    doc.documentElement.setAttribute('xmlns', xmlns)

    with open(output_filename, 'w') as fh:
        fh.write(doc.toprettyxml(indent='  '))


def get_data(input_gpx):
    """
    Get the gpx data and put it into a DataFrame   
    This function is adapted from the get_data() function in Exercise 3
    """
    import xml.etree.ElementTree as ET
    tree = ET.parse(input_gpx)
    
    datetime = np.array([], dtype=np.str_)#, dtype=np.string)
    lat = np.array([], dtype=np.float64)
    lon = np.array([], dtype=np.float64)
    
    for g in tree.iter('{http://www.topografix.com/GPX/1/0}trkpt'):
        latitude = g.get('lat')
        longitude = g.get('lon')
        time = g[1].text
        datetime = np.append(datetime, time)
        lat = np.append(lat, float(latitude))
        lon = np.append(lon, float(longitude))
    
    df = pd.DataFrame({'datetime':datetime,
                       'lat':lat,
                       'lon':lon})
    df['datetime'] = pd.to_datetime(df['datetime'], utc=True)
    
    return df


def main():
    input_directory = pathlib.Path(sys.argv[1])
    output_directory = pathlib.Path(sys.argv[2])
        
    accl = pd.read_json(input_directory / 'accl.ndjson.gz', lines=True, convert_dates=['timestamp'])[['timestamp', 'x']]
    gps = get_data(input_directory / 'gopro.gpx')
    phone = pd.read_csv(input_directory / 'phone.csv.gz')[['time', 'gFx', 'Bx', 'By']]
    
    first_time = accl['timestamp'].min()
    
    accl['timestamp'] = accl['timestamp'].dt.round('4S')
    gps['datetime'] = gps['datetime'].dt.round('4S')
    
    accl = accl.groupby(['timestamp']).mean()
    gps = gps.groupby(['datetime']).mean()  
    
    
    # Create "combined" as described in the exercise
    # Cross-Correlation Calculation
    best_offset = 0
    mincc = -999999
    
    
    for offset in np.linspace(-5.0, 5.0, 101):
        # Create a timestamp in the phone data
        phoneGrouped = phone.copy()
        phoneGrouped['timestamp'] = first_time + pd.to_timedelta(phoneGrouped['time'] + offset, unit='sec')
        
        # Round to nearest 4 seconds
        phoneGrouped['timestamp'] = phoneGrouped['timestamp'].dt.round('4S')
    
        # Group and aggregate by the timestamp
        phoneGrouped = phoneGrouped.groupby(['timestamp']).mean()
    
        prod = phoneGrouped['gFx'] * accl['x']
        cc = prod.sum()
        
        if cc > mincc:
            best_offset = offset
            mincc = cc
        
    # Create combined data
    phone['timestamp'] = first_time + pd.to_timedelta(phone['time'] + best_offset, unit='sec')
    phone['timestamp'] = phone['timestamp'].dt.round('4S')   
    phone = phone.groupby(['timestamp']).mean()
    
    combined = gps.join(phone, how='inner')
    combined.reset_index(names='datetime', inplace=True)

    
    print(f'Best time offset: {best_offset:.1f}')
    os.makedirs(output_directory, exist_ok=True)
    output_gpx(combined[['datetime', 'lat', 'lon']], output_directory / 'walk.gpx')
    combined[['datetime', 'Bx', 'By']].to_csv(output_directory / 'walk.csv', index=False)


main()
