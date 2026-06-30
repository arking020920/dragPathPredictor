import React from 'react';
import { Container, Row, Col } from 'react-bootstrap';
import '../styles/TermsofUse.css';

const TermsOfUse = () => {
    return (
        <section className="terms-section">
            <Container>
                <Row className="justify-content-center">
                    <Col xs={12} md={10} lg={8}>
                        <div className="terms-wrapper p-4">
                            <h1 className="section-title text-center mb-4">Términos de Uso</h1>
                            <p className="terms-description">
                                Bienvenido/a a nuestra plataforma. Al acceder y utilizar este sitio, aceptas los siguientes Términos de Uso. 
                                Por favor, léelos cuidadosamente.
                            </p>
                            <div className="terms-content">
                                <h2 className="terms-heading">1. Uso de la Plataforma</h2>
                                <p>
                                    La plataforma está destinada para fines personales y empresariales internos. No puedes usar el sitio para 
                                    actividades ilegales o no autorizadas.
                                </p>
                                <h2 className="terms-heading">2. Propiedad Intelectual</h2>
                                <p>
                                    Todos los derechos de autor, marcas registradas y otros derechos de propiedad intelectual de los contenidos 
                                    de este sitio pertenecen a nuestra empresa o a sus licenciantes. Está prohibido copiar, reproducir o distribuir 
                                    cualquier contenido sin nuestro consentimiento previo.
                                </p>
                                <h2 className="terms-heading">3. Limitación de Responsabilidad</h2>
                                <p>
                                    No nos hacemos responsables de daños o pérdidas directas, indirectas, incidentales o consecuentes derivadas del 
                                    uso o imposibilidad de uso de la plataforma.
                                </p>
                                <h2 className="terms-heading">4. Modificaciones</h2>
                                <p>
                                    Nos reservamos el derecho de modificar estos Términos de Uso en cualquier momento. Las actualizaciones se 
                                    publicarán en esta misma página.
                                </p>
                                <h2 className="terms-heading">5. Contacto</h2>
                                <p>
                                    Si tienes alguna pregunta sobre estos Términos de Uso, no dudes en <a href="/contact">contactarnos</a>.
                                </p>
                            </div>
                        </div>
                    </Col>
                </Row>
            </Container>
        </section>
    );
};

export default TermsOfUse;

