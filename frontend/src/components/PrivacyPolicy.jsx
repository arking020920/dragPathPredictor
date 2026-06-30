import React from 'react';
import { Container, Row, Col } from 'react-bootstrap';
import '../styles/PrivacyPolicy.css';


const PrivacyPolicy = () => {
    return (
        <section className="privacy-section">
            <Container>
                <Row className="justify-content-center">
                    <Col xs={12} md={10} lg={8}>
                        <div className="privacy-wrapper p-4">
                            <h1 className="section-title text-center mb-4">Política de Privacidad</h1>
                            <p className="privacy-description">
                                Tu privacidad es importante para nosotros. Esta Política de Privacidad describe cómo recopilamos, utilizamos 
                                y protegemos tu información personal.
                            </p>
                            <div className="privacy-content">
                                <h2 className="privacy-heading">1. Información que Recopilamos</h2>
                                <p>
                                    Podemos recopilar información personal, como tu nombre, dirección de correo electrónico y cualquier dato 
                                    proporcionado voluntariamente a través de formularios en nuestro sitio.
                                </p>
                                <h2 className="privacy-heading">2. Uso de la Información</h2>
                                <p>
                                    Utilizamos la información recopilada para:
                                    <ul>
                                        <li>Proporcionar y mejorar nuestros servicios.</li>
                                        <li>Responder a tus consultas y solicitudes.</li>
                                        <li>Enviar comunicaciones relacionadas con nuestro sitio.</li>
                                    </ul>
                                </p>
                                <h2 className="privacy-heading">3. Protección de Datos</h2>
                                <p>
                                    Implementamos medidas de seguridad técnicas y organizativas para proteger tus datos contra el acceso no 
                                    autorizado, la pérdida o el daño.
                                </p>
                                <h2 className="privacy-heading">4. Compartir Información</h2>
                                <p>
                                    No compartimos tu información personal con terceros, excepto cuando sea necesario para cumplir con la ley 
                                    o cuando tú lo autorices explícitamente.
                                </p>
                                <h2 className="privacy-heading">5. Tus Derechos</h2>
                                <p>
                                    Tienes derecho a acceder, corregir o eliminar tu información personal. Si deseas ejercer estos derechos, 
                                    por favor <a href="/contact">contáctanos</a>.
                                </p>
                                <h2 className="privacy-heading">6. Cambios en la Política</h2>
                                <p>
                                    Nos reservamos el derecho de actualizar esta Política de Privacidad. Publicaremos cualquier cambio en esta 
                                    página, y se te notificará si los cambios son significativos.
                                </p>
                            </div>
                        </div>
                    </Col>
                </Row>
            </Container>
        </section>
    );
};

export default PrivacyPolicy;
