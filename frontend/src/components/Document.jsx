import React from 'react';
import { Container, Row, Col, Card, Accordion, Button } from 'react-bootstrap';
import '../styles/Document.css';
import aboutImg from '../assets/about.jpg';

const Document = () => {
    return (
        <Container fluid>
            {/* Hero Section */}
            <div className="hero-section mb-5">
                <div className="hero-overlay">
                    <h1 className="hero-title" data-aos="fade-down">Langrangian Leeway Documentation</h1>
                    <p className="hero-description" data-aos="fade-up">Welcome to the comprehensive documentation for Langrangian Leeway. Here, you'll find everything you need to get started and make the most of our predictive modeling tool.</p>
                </div>
                <img
                    src={aboutImg}
                    alt="Hero"
                    className="hero-background"
                />
            </div>

        {/* Installation Guide Section */}
        <Row className="mb-5">
            <Col>
            <Card>
                <Card.Header>
                <h2>Installation Guide</h2>
                </Card.Header>
                <Card.Body>
                <h4>Requirements</h4>
                <ul>
                    <li>Python 3.9 or higher</li>
                    <li>Flask</li>
                    <li>React</li>
                    <li>Node.js</li>
                </ul>
                <h4>Steps</h4>
                <ol>
                    <li>Clone the repository: <code>git clone https://github.com/your-repo/langrangian-leeway.git</code></li>
                    <li>Navigate to the project directory: <code>cd langrangian-leeway</code></li>
                    <li>Install backend dependencies: <code>pip install -r requirements.txt</code></li>
                    <li>Install frontend dependencies: <code>npm install</code></li>
                    <li>Run the backend server: <code>flask run</code></li>
                    <li>Run the frontend server: <code>npm start</code></li>
                </ol>
                </Card.Body>
            </Card>
            </Col>
        </Row>

        {/* Usage Examples Section */}
        <Row className="mb-5">
            <Col>
            <Card>
                <Card.Header>
                <h2>Usage Examples</h2>
                </Card.Header>
                <Card.Body>
                <h4>Example 1: Basic Usage</h4>
                <p>
                    To predict the trajectory of an object, simply fill in the required fields on the toolmap page and click "Generate Trajectory".
                </p>
                <h4>Example 2: Advanced Configuration</h4>
                <p>
                    For advanced users, you can customize the parameters such as the starting coordinates, date, and duration of the prediction.
                </p>
                <h4>Example 3: API Integration</h4>
                <p>
                    You can also integrate our API into your own applications. Here's a sample request to get you started:
                </p>
                <pre>
                    <code>
                    {`POST http://localhost:5000/api/drog
    Content-Type: application/json
    Authorization: Bearer your_token

    {
    "obj": "human",
    "lat": "40.7128",
    "lon": "-74.0060",
    "startDate": "2023-07-10",
    "hours": "24",
    "reverse": false
    }`}
                    </code>
                </pre>
                </Card.Body>
            </Card>
            </Col>
        </Row>

        {/* FAQ Section */}
        <Row>
            <Col>
            <Card>
                <Card.Header>
                <h2>Frequently Asked Questions (FAQ)</h2>
                </Card.Header>
                <Card.Body>
                <Accordion>
                    <Accordion.Item eventKey="0">
                    <Accordion.Header>What is Langrangian Leeway?</Accordion.Header>
                    <Accordion.Body>
                        Langrangian Leeway is a predictive modeling tool that uses the Lagrangian model to forecast trajectories of various objects in different environments.
                    </Accordion.Body>
                    </Accordion.Item>
                    <Accordion.Item eventKey="1">
                    <Accordion.Header>How do I get an API token?</Accordion.Header>
                    <Accordion.Body>
                        You can get an API token by registering on our website and logging in to your account. The token will be provided upon successful login.
                    </Accordion.Body>
                    </Accordion.Item>
                    <Accordion.Item eventKey="2">
                    <Accordion.Header>Can I integrate Langrangian Leeway with other applications?</Accordion.Header>
                    <Accordion.Body>
                        Yes, you can integrate our API with your own applications to utilize the predictive modeling capabilities.
                    </Accordion.Body>
                    </Accordion.Item>
                    <Accordion.Item eventKey="3">
                    <Accordion.Header>Is there a limit to the number of predictions I can make?</Accordion.Header>
                    <Accordion.Body>
                        There is no limit for now, but excessive use may be subject to rate limiting to ensure fair usage for all users.
                    </Accordion.Body>
                    </Accordion.Item>
                </Accordion>
                </Card.Body>
            </Card>
            </Col>
        </Row>
        </Container>
    );
};

export default Document;
