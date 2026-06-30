import React, { useEffect, useRef, useState } from 'react';
import 'ol/ol.css';
import Map from 'ol/Map';
import View from 'ol/View';
import TileLayer from 'ol/layer/Tile';
import VectorLayer from 'ol/layer/Vector';
import VectorSource from 'ol/source/Vector';
import OSM from 'ol/source/OSM';
import { fromLonLat, toLonLat } from 'ol/proj';
import { Style, Icon, Fill, Stroke } from 'ol/style';
import { Point, Circle as OL_Circle, Polygon } from 'ol/geom';
import KML from 'ol/format/KML';
import Feature from 'ol/Feature';
import * as turf from '@turf/turf';
import Overlay from 'ol/Overlay';
import '../styles/MapComponent.css';


export function MapComponent({ kmlContent }){
  const mapElement = useRef(null);
  const mapRef = useRef(null);
  const overlayRef = useRef(null);
  const vectorLayersRef = useRef([]);
  const [features, setFeatures] = useState([]);
  const [circleFeature, setCircleFeature] = useState(null);
  const [circleRadius, setCircleRadius] = useState(5000);
  const [coordenate, setCoordenate] = useState([]);
  const [layerLimit, setLayerLimit] = useState(1)  

  useEffect(() => {
    if (mapRef.current) return;

    mapRef.current = new Map({
      target: mapElement.current,
      layers: [
        new TileLayer({
          source: new OSM(),
        }),
      ],
      view: new View({
        center: fromLonLat([-77.781167, 21.521757]),
        zoom: 6,
      }),
    });

    const overlayElement = document.createElement('div');
    overlayElement.className = 'coordinate-overlay';
    overlayElement.style.position = 'absolute';
    overlayElement.style.backgroundColor = 'rgba(0, 0, 0, 0.7)';
    overlayElement.style.color = '#fff';
    overlayElement.style.padding = '5px';
    overlayElement.style.borderRadius = '5px';
    overlayElement.style.whiteSpace = 'nowrap';
    overlayRef.current = new Overlay({
      element: overlayElement,
      offset: [10, 10],
      positioning: 'bottom-left',
    });
    mapRef.current.addOverlay(overlayRef.current);

    mapRef.current.on('pointermove', handlePointerMove);
    mapRef.current.on('click', handleMapClick);
  }, []);

  useEffect(() => {
  if (!kmlContent) return;

  const contents = Array.isArray(kmlContent) ? kmlContent : [kmlContent];

  contents.forEach(content => {
    const vectorSource = new VectorSource({
      format: new KML(),
      url: `data:text/xml;charset=utf-8,${encodeURIComponent(content)}`,
    });

    const newVectorLayer = new VectorLayer({
      source: vectorSource,
      style: feature => {
        if (feature.getGeometry() instanceof Point) {
          return new Style({
            image: new Icon({
              src: 'http://maps.google.com/mapfiles/kml/pal3/icon56.png',
              scale: 0.5,
            }),
          });
        }
        return null;
      },
    });

    if (vectorLayersRef.current.length >= layerLimit) {
      const oldestLayer = vectorLayersRef.current.shift();
      mapRef.current.removeLayer(oldestLayer);
    }

    mapRef.current.addLayer(newVectorLayer);
    vectorLayersRef.current.push(newVectorLayer);

    vectorSource.once('change', () => {
      if (vectorSource.getState() === 'ready') {
        mapRef.current.getView().fit(vectorSource.getExtent(), { padding: [50, 50, 50, 50] });
      }
    });

    vectorSource.once('change', () => {
      const loadedFeatures = vectorSource.getFeatures();
      const pointFeatures = loadedFeatures.filter(feature => feature.getGeometry() instanceof Point);
      setFeatures(prev => [...prev, ...pointFeatures]);
    });
  });
}, [kmlContent]);


  const handleMapClick = (event) => {
    const coordinate = event.coordinate;

    if (circleFeature) {
      mapRef.current.removeLayer(circleFeature.get('layer'));
    }

    const circleGeometry = new OL_Circle(coordinate, circleRadius);
    const circleFeatureNew = new Feature({ geometry: circleGeometry });

    const circleStyle = new Style({
      stroke: new Stroke({ color: '#ff0000', width: 2 }),
      fill: new Fill({ color: 'rgba(255, 0, 0, 0.3)' }),
    });

    const circleSource = new VectorSource({ features: [circleFeatureNew] });
    const circleLayer = new VectorLayer({ source: circleSource, style: circleStyle });

    circleFeatureNew.set('layer', circleLayer);
    mapRef.current.addLayer(circleLayer);
    setCircleFeature(circleFeatureNew);

    const circleCenter = toLonLat(coordinate);
    const circlePolygon = turf.circle(circleCenter, circleRadius / 1000, { steps: 64, units: 'kilometers' });

    const pointsInside = features.filter(feature => {
      const pointCoords = toLonLat(feature.getGeometry().getCoordinates());
      const point = turf.point(pointCoords);
      return turf.booleanPointInPolygon(point, circlePolygon);
    });

    pointsInside.forEach(feature => {
      const coords = toLonLat(feature.getGeometry().getCoordinates());
      console.log('Point inside circle:', coords);
    });
  };

  const handlePointerMove = (event) => {
    const feature = mapRef.current.forEachFeatureAtPixel(event.pixel, f => f);
    const overlayElement = overlayRef.current.getElement();
    if (feature && feature.getGeometry() instanceof Point) {
      const coords = toLonLat(feature.getGeometry().getCoordinates());
      const [lon, lat] = coords.map(coord => coord.toFixed(6));
      overlayElement.innerHTML = `Lon: ${lon}, Lat: ${lat}`;
      overlayRef.current.setPosition(event.coordinate);
      overlayElement.style.display = 'block';
    } else {
      overlayElement.style.display = 'none';
    }
  };

  const handleLogCircleCoordinates = () => {
    if (!circleFeature) return;

    const circleGeometry = circleFeature.getGeometry();
    const circleCenter = toLonLat(circleGeometry.getCenter());
    const circleRadiusMeters = circleGeometry.getRadius();
    const circlePolygon = turf.circle(circleCenter, circleRadiusMeters / 1000, { steps: 64, units: 'kilometers' });

    const circlePoints = circlePolygon.geometry.coordinates[0];
    setCoordenate(circlePoints);
    circlePoints.forEach((point, index) => {
      console.log(`Circle Point ${index + 1}: Lon: ${point[0].toFixed(6)}, Lat: ${point[1].toFixed(6)}`);
    });
  };

  const handleDownload = () => {
    const format = new KML();
    const exportFeatures = [...features];

    if (circleFeature) {
      const circleGeometry = circleFeature.getGeometry();
      const circleCenter = toLonLat(circleGeometry.getCenter());
      const circleRadiusKm = circleGeometry.getRadius() / 1000;
      const circlePolygon = turf.circle(circleCenter, circleRadiusKm, { steps: 64, units: 'kilometers' });

      const polygonCoordinates = circlePolygon.geometry.coordinates;
      const olPolygon = new Polygon(polygonCoordinates.map(ring => ring.map(coord => fromLonLat(coord))));
      const polygonFeature = new Feature({ geometry: olPolygon });
      exportFeatures.push(polygonFeature);
    }

    const vectorSource = new VectorSource({ features: exportFeatures });
    const kmlData = format.writeFeatures(vectorSource.getFeatures(), {
      featureProjection: mapRef.current.getView().getProjection(),
    });

    const blob = new Blob([kmlData], { type: 'application/vnd.google-earth.kml+xml' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'map_with_circle.kml';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const handleClear = () => {
    vectorLayersRef.current.forEach(layer => {
      mapRef.current.removeLayer(layer);
    });
    vectorLayersRef.current = [];
    setFeatures([]);
    setCircleFeature(null);
  };

  return (
  <div>
    <div ref={mapElement} style={{ width: '100%', height: '80vh' }}></div>
    <div className="text-center mb-5">
      <button className='btn btn-info mt-3' style={{marginRight:'6px'}}>Máx. Trayectorias Visibles: {layerLimit}</button>
      <button className='btn btn-primary mt-3 me-2'  onClick={() => setLayerLimit(prev => prev + 1)}>+</button>
      <button className='btn btn-primary mt-3 me-2'  onClick={() => setLayerLimit(prev => Math.max(1, prev - 1))}>-</button>
      <button className='btn btn-primary mt-3 me-2' onClick={handleDownload}>Descargar KML</button>
      <button className='btn btn-secondary mt-3 me-2' onClick={handleClear}>Borrar Mapa</button>
      <button className='btn btn-info mt-3' onClick={handleLogCircleCoordinates}>Coordenadas</button>
      <div className='mt-3'>
        <ul>
          {coordenate.map((item, index) => (
            <li key={index}>{`${item[0].toFixed(6)}, ${item[1].toFixed(6)}`}</li>
          ))}
        </ul>
      </div>
    </div>
  </div>
);
}