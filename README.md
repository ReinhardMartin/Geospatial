# Geospatial
This project investigates how spatial accessibility to university hubs affects apartment prices for students in Turin, Italy. Using spatial econometric techniques it integrates public GTFS transit data, housing listings, and university location data to assess both direct and spillover effects of housing attributes and connection to academic centers. FULL REPORT: [Data File](./geospatial.pdf)

It may be required to first run `pip install -r requirements.txt`

## Data References (present in this repo)
- https://openmobilitydata-data.s3-us-west-1.amazonaws.com/public/feeds/gruppo-torinese-trasporti/51/20210707/gtfs.zip
- https://download.bbbike.org/osm/bbbike/Turin/Turin.osm.pbf
- http://www.cittametropolitana.torino.it/cms/risorse/territorio/dwd/pianificazione-territoriale/ptc2/shape_tavole/tav21/facolta.zip
- http://www.comune.torino.it/opendata/geodata/quartieri.zip
