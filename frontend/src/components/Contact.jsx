import React, { useState } from 'react';
import { Form, Button, Container, Row, Col, Toast } from 'react-bootstrap';
import axios from 'axios';
import '../styles/Contact.css';
import aboutImg from '../assets/about.jpg';

const Contact = () => {
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        message: '',
    });

    const [touchedFields, setTouchedFields] = useState({
        name: false,
        email: false,
        message: false,
    });

    const [errors, setErrors] = useState({});
    const [showToast, setShowToast] = useState(false);
    const [responseMessage, setResponseMessage] = useState('');

    const validateField = (name, value) => {
        switch (name) {
            case 'name':
                return value ? '' : 'El nombre es obligatorio.';
            case 'email':
                if (!value) return 'El email es obligatorio.';
                return /\S+@\S+\.\S+/.test(value) ? '' : 'El email no es válido.';
            case 'message':
                return value ? '' : 'El mensaje es obligatorio.';
            default:
                return '';
        }
    };

    const handleBlur = (e) => {
        const { name, value } = e.target;
        setTouchedFields({ ...touchedFields, [name]: true });
        setErrors({ ...errors, [name]: validateField(name, value) });
    };

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData({ ...formData, [name]: value });

        if (touchedFields[name]) {
            setErrors({ ...errors, [name]: validateField(name, value) });
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        const newErrors = Object.keys(formData).reduce((acc, field) => {
            const error = validateField(field, formData[field]);
            if (error) acc[field] = error;
            return acc;
        }, {});

        if (Object.keys(newErrors).length > 0) {
            setErrors(newErrors);
            setTouchedFields({ name: true, email: true, message: true });
            return;
        }

        try {
            const response = await axios.post('http://localhost:5000/api/contact', formData);
            if (response.status === 200) {
                setResponseMessage('Tu mensaje ha sido enviado con éxito.');
                setShowToast(true);
                setFormData({ name: '', email: '', message: '' });
                setTouchedFields({ name: false, email: false, message: false });
            } else {
                throw new Error();
            }
        } catch {
            setResponseMessage('Hubo un error al enviar tu mensaje.');
            setShowToast(true);
        }
    };

    return (
        <>
        <Container fluid>
            {/* Hero Section */}
            <div className="hero-section-contact justify-content-center vh-100 align-items-center">
                <div className="col-md-5 hero-overlay m-3">
                    <h1 className="hero-title" data-aos="fade-down">Informaci&oacute;n de contacto</h1>
                    <p className="hero-description" data-aos="fade-up">Estamos aquí para ayudarte. Por favor, llena el formulario y nos pondremos en contacto.</p>
                </div>
                <div className="contact-form-wrapper col-md-5 p-4">
                    <h1 className="section-title text-center">Contáctanos</h1>
                    <p className="contact-description text-center">
                        Facebook
                    </p>
                    <Form onSubmit={handleSubmit} noValidate className='text-start'>
                        <Form.Group controlId="formName" className="mb-3">
                            <Form.Label>Nombre</Form.Label>
                            <Form.Control
                                type="text"
                                name="name"
                                value={formData.name}
                                onChange={handleChange}
                                onBlur={handleBlur}
                                placeholder="Ingresa tu nombre"
                                isInvalid={touchedFields.name && !!errors.name}
                            />
                            <Form.Control.Feedback type="invalid">{errors.name}</Form.Control.Feedback>
                        </Form.Group>
                        <Form.Group controlId="formEmail" className="mb-3">
                            <Form.Label>Email</Form.Label>
                            <Form.Control
                                type="email"
                                name="email"
                                value={formData.email}
                                onChange={handleChange}
                                onBlur={handleBlur}
                                placeholder="Ingresa tu email"
                                isInvalid={touchedFields.email && !!errors.email}
                            />
                            <Form.Control.Feedback type="invalid">{errors.email}</Form.Control.Feedback>
                        </Form.Group>
                        <Form.Group controlId="formMessage" className="mb-4">
                            <Form.Label>Mensaje</Form.Label>
                            <Form.Control
                                as="textarea"
                                name="message"
                                value={formData.message}
                                onChange={handleChange}
                                onBlur={handleBlur}
                                placeholder="Escribe tu mensaje"
                                rows={5}
                                isInvalid={touchedFields.message && !!errors.message}
                            />
                            <Form.Control.Feedback type="invalid">{errors.message}</Form.Control.Feedback>
                        </Form.Group>
                        <Button
                            type="submit"
                            variant="primary"
                            className="w-100"
                            disabled={
                                !formData.name || !formData.email || !formData.message || Object.keys(errors).some((key) => errors[key])
                            }
                        >
                            Enviar Mensaje
                        </Button>
                    </Form>
                </div>

            {/* Toast de respuesta */}
            <Toast
                className="position-fixed bottom-0 end-0 m-3"
                show={showToast}
                onClose={() => setShowToast(false)}
                delay={3000}
                autohide
            >
                <Toast.Body>{responseMessage}</Toast.Body>
            </Toast>
                <img
                    src={aboutImg}
                    alt="Hero"
                    className="hero-background"
                />
            </div>
        </Container>
        </>
    );
};

export default Contact;
