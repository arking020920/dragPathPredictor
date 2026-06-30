import React from 'react';
import { Container, Row, Col, Card, Accordion } from 'react-bootstrap';
import faqData from '../utils/faqData.json'
import '../styles/About.css';
import aboutImg from '../assets/about.jpg';
import 'aos/dist/aos.css';
import AOS from 'aos';

const Faqs = () => {
    
    return (
        <>
        <Container fluid>
            {/* Hero Section */}
            <div className="hero-section">
                <div className="hero-overlay">
                    <h1 className="hero-title" data-aos="fade-down">Frequently Asked Questions (FAQs)</h1>
                    <p className="hero-description" data-aos="fade-up">Find answers to the most commonly asked questions about Langrangian Leeway.</p>
                </div>
                <img
                    src={aboutImg}
                    alt="Hero"
                    className="hero-background"
                />
            </div>
        </Container>
        <Container className="my-5">
            <Row>
                <Col>
                    <Card>
                        <Card.Header>
                            <h2>General Questions</h2>
                        </Card.Header>
                        <Card.Body>
                            <Accordion>
                                {faqData.general.map((item, index) => (
                                    <Accordion.Item eventKey={index.toString()} key={index}>
                                        <Accordion.Header>{item.question}</Accordion.Header>
                                        <Accordion.Body>{item.answer}</Accordion.Body>
                                    </Accordion.Item>
                                ))}
                            </Accordion>
                        </Card.Body>
                    </Card>
                </Col>
            </Row>

            <Row className="mt-5">
                <Col>
                    <Card>
                        <Card.Header>
                            <h2>Technical Questions</h2>
                        </Card.Header>
                        <Card.Body>
                            <Accordion>
                                {faqData.technical.map((item, index) => (
                                    <Accordion.Item eventKey={(index + faqData.general.length).toString()} key={index}>
                                        <Accordion.Header>{item.question}</Accordion.Header>
                                        <Accordion.Body>{item.answer}</Accordion.Body>
                                    </Accordion.Item>
                                ))}
                            </Accordion>
                        </Card.Body>
                    </Card>
                </Col>
            </Row>
        </Container>
        </>
    );
};

export default Faqs;

