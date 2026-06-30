import React, { useState } from 'react';
import { Form, Button, Row, Col, Card } from 'react-bootstrap';
import {MapComponent} from './MapComponent.jsx';

const apiUrl = import.meta.env.VITE_API_URL;

const ToolMap = () => {
  const [kmlContent, setKmlContent] = useState('');
  const token = localStorage.getItem('token');
  const [multiCoords, setMultiCoords] = useState(false);

  //Esto lo que se le pasa el MapComponente para modificar el circulo de coordenadas
  const [circleRadius, setCircleRadius] = useState(5000);
  const [trajectoryCount, setTrajectoryCount] = useState(5);

  const handleSetCoordinates = (latList, lonList) => {
    setMultiCoords(true)
    setFormData(prev => ({
      ...prev,
      lat: latList.join(','),
      lon: lonList.join(','),
    }));
  };


  const [formData, setFormData] = useState({
    obj: '',
    lat: '',
    lon: '',
    startDate: '',
    endDate: '',
    reverse: false,
  });

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    if (name === 'multiCoords') {
      setMultiCoords(checked);
    } else {
      setFormData({
        ...formData,
        [name]: type === 'checkbox' ? checked : value,
      });
    }
  };

  const handleSubmit = async (e) => {
  e.preventDefault();

  let payload;

  if (multiCoords) {
    const latList = formData.lat.split(',').map(v => v.trim());
    const lonList = formData.lon.split(',').map(v => v.trim());

    if (latList.length !== lonList.length) {
      alert('Las listas de latitud y longitud deben tener la misma cantidad de elementos.');
      return;
    }

    payload = latList.map((lat, index) => ({
      obj: formData.obj,
      lat,
      lon: lonList[index],
      startDate: formData.startDate,
      endDate: formData.endDate,
      reverse: formData.reverse,
    }));
  } else {
    payload = formData;
  }

  try {
    const response = await fetch(`${apiUrl}/drog`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(payload),
    });

    if (response.ok) {
      const data = await response.json();

      // Aquí detectamos si el backend devuelve un array o un solo KML
      if (Array.isArray(data.kml_content)) {
        setKmlContent(data.kml_content); // array de KMLs
      } else {
        setKmlContent([data.kml_content]); // lo convertimos en array para consistencia
      }
    } else {
      console.error('Error al obtener el archivo KML');
    }
  } catch (error) {
    console.error('Error en la solicitud:', error);
  }
};

  return (
    <div className="mt-5">
      <Row className="justify-content-center">
        <Col md={2}>
          <Card>
            <Card.Header className="text-center">
              <h3>Inserte los datos</h3>
            </Card.Header>
            <Card.Body>
              <Form onSubmit={handleSubmit}>
                <Form.Group className="mb-3" controlId="selectObj">
                  <Form.Label>Selecciona un objeto:</Form.Label>
                  <Form.Control as="select" name="obj" value={formData.obj} onChange={handleChange}>
                    <option value="">Seleccione objeto</option>
                    <option value="human">Humano</option>
                    <option value="bote">Bote</option>
                    <option value="oil">Petróleo</option>
                    <option value="drog">Droga</option>
                  </Form.Control>
                </Form.Group>

                <Form.Group className="mb-3" controlId="multiCoords">
                  <Form.Check
                    type="checkbox"
                    label="Múltiples coordenadas"
                    name="multiCoords"
                    checked={multiCoords}
                    onChange={handleChange}
                  />
                </Form.Group>

                <Form.Group className="mb-3" controlId="Latitud">
                  <Form.Label>Latitud:</Form.Label>
                  <Form.Control
                    type="text"
                    name="lon"
                    value={formData.lon}
                    onChange={handleChange}
                    placeholder={multiCoords ? "Ej: 25,26,27" : "Coordenadas decimales"}
                  />
                </Form.Group>

                <Form.Group className="mb-3" controlId="Longitud">
                  <Form.Label>Longitud:</Form.Label>
                  <Form.Control
                    type="text"
                    name="lat"
                    value={formData.lat}
                    onChange={handleChange}
                    placeholder={multiCoords ? "Ej: 46,47,49" : "Coordenadas decimales"}
                  />
                </Form.Group>


                <Form.Group className="mb-3" controlId="FechadeInicio">
                  <Form.Label>Fecha de inicio:</Form.Label>
                  <Form.Control
                    type="datetime-local"
                    name="startDate"
                    value={formData.startDate}
                    onChange={handleChange}
                  />
                </Form.Group>

                <Form.Group className="mb-3" controlId="FechadeFin">
                  <Form.Label>Fecha de fin:</Form.Label>
                  <Form.Control
                    type="datetime-local"
                    name="endDate"
                    value={formData.endDate}
                    onChange={handleChange}
                  />
                </Form.Group>

                <Form.Group className="mb-3" controlId="Reverse">
                  <Form.Check
                    type="checkbox"
                    label="Reverse"
                    name="reverse"
                    checked={formData.reverse}
                    onChange={handleChange}
                  />
                </Form.Group>

                <Button variant="primary" type="submit" className="w-100">
                  Generar trayectoria
                </Button>
              </Form>
            </Card.Body>
          </Card>
        </Col>

        <Col md={8}>
              <MapComponent
        kmlContent={kmlContent}
        setLatLon={handleSetCoordinates}
        trajectoryCount={trajectoryCount}
        circleRadius={circleRadius}
        setCircleRadius={setCircleRadius}
        setTrajectoryCount={setTrajectoryCount}
      />

        </Col>
      </Row>
    </div>
  );
};

export default ToolMap;
