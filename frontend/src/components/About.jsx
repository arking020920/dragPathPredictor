import { Container, Row, Col, Button } from 'react-bootstrap';
import aboutImg from '../assets/about.jpg';
import data from '../utils/aboutData.json';
import 'aos/dist/aos.css';
import AOS from 'aos';
import '../styles/About.css';

import { useEffect } from 'react';

const About = () => {
    useEffect(() => {
        AOS.init({ duration: 1000, once: true });
    }, []);

    const scrollToSection = (id) => {
        const section = document.getElementById(id);
        if (section) {
            section.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    };

    return (
        <Container fluid className="about-section">
            {/* Hero Section */}
            <div className="hero-section">
                <div className="hero-overlay">
                    <h1 className="hero-title" data-aos="fade-down">{data.intro.title}</h1>
                    <p className="hero-description" data-aos="fade-up">{data.intro.description}</p>
                    <Button variant="light" className="cta-button" data-aos="zoom-in" href="#highlights">Saber m&aacute;s</Button>
                </div>
                <img
                    src={aboutImg}
                    alt="Hero"
                    className="hero-background"
                />
            </div>

            {/* Highlights Section */}
            <section id="highlights" className="highlights-section py-5">
                <h2 className="section-title text-center" data-aos="fade-up"></h2>
                <Row className="gy-4 text-center">
                    {data.sections.map((section, index) => (
                        <Col lg={4} md={6} sm={12} key={index} data-aos="fade-up" data-aos-delay={index * 100}>
                            <div className="highlight-item">
                                <div className="icon-circle">
                                    <i className="bi bi-lightbulb" />
                                </div>
                                <h3 className="highlight-title">{section.title}</h3>
                                <p className="highlight-description">{section.content}</p>
                            </div>
                        </Col>
                    ))}
                </Row>
            </section>

            {/* Team Section */}
            <section className="team-section py-5">
                <h2 className="section-title text-center" data-aos="fade-up">Nuestro Equipo</h2>
                <Row className="gy-4 text-center">
                    {data.team.map((member, index) => (
                        <Col lg={3} md={4} sm={6} key={index} data-aos="fade-up" data-aos-delay={index * 100}>
                            <div className="team-member">
                                <img
                                    src={`/images/${member.image}`}
                                    alt={member.name}
                                    className="team-image rounded-circle"
                                />
                                <h4 className="team-name">{member.name}</h4>
                                <p className="team-position">{member.position}</p>
                            </div>
                        </Col>
                    ))}
                </Row>
            </section>


        </Container>
    );
};

export default About;
