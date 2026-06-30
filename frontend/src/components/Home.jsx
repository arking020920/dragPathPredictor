import { Container, Row, Col, Button } from 'react-bootstrap';
import landingImg from '../assets/landing.jpg'; // Imagen de fondo
import data from '../utils/landingData.json'; // Datos de la landing page
import 'aos/dist/aos.css';
import AOS from 'aos';
import '../styles/HomePage.css';

import { useEffect } from 'react';

const HomePage = () => {
    useEffect(() => {
        AOS.init({ duration: 1000, once: true });
    }, []);

    return (
        <Container fluid className="landing-page">
            {/* Hero Section */}
            <div className="hero-section">
                <div className="hero-overlay">
                    <h1 className="hero-title" data-aos="fade-down">{data.intro.title}</h1>
                    <p className="hero-description" data-aos="fade-up">{data.intro.description}</p>
                    <Button variant="light" className="cta-button" data-aos="zoom-in" href="#features">Learn More</Button>
                </div>
                <img
                    src={landingImg}
                    alt="Hero"
                    className="hero-background"
                />
            </div>

            {/* Features Section */}
            <section id="features" className="features-section py-5">
                <h2 className="section-title text-center" data-aos="fade-up">Características Destacadas</h2>
                <Row className="gy-4 text-center">
                    {data.features.map((feature, index) => (
                        <Col lg={4} md={6} sm={12} key={index} data-aos="fade-up" data-aos-delay={index * 100}>
                            <div className="feature-item">
                                <div className="icon-circle">
                                    <i className={`bi ${feature.icon}`} />
                                </div>
                                <h3 className="feature-title">{feature.title}</h3>
                                <p className="feature-description">{feature.description}</p>
                            </div>
                        </Col>
                    ))}
                </Row>
            </section>

            {/* Testimonials Section */}
            <section id="testimonials" className="testimonials-section py-5">
                <h2 className="section-title text-center" data-aos="fade-up">Lo que Dicen Nuestros Clientes</h2>
                <Row className="gy-4">
                    {data.testimonials.map((testimonial, index) => (
                        <Col lg={4} md={6} sm={12} key={index} data-aos="fade-up" data-aos-delay={index * 100}>
                            <div className="testimonial-item">
                                <p className="testimonial-text">{testimonial.quote}</p>
                                <h5 className="testimonial-author">{testimonial.name}</h5>
                                <p className="testimonial-position">{testimonial.position}</p>
                            </div>
                        </Col>
                    ))}
                </Row>
            </section>

            {/* Call to Action Section */}
            <section className="cta-section py-5 mt-3 text-center" data-aos="fade-up">
                <h2 className="cta-title">¿Listo para comenzar?</h2>
                <p className="cta-description">Únete a nosotros y lleva tu investigaci&oacute;n al siguiente nivel.</p>
                <Button variant="primary" href="/contact">Contáctanos</Button>
            </section>
        </Container>
    );
};

export default HomePage;
