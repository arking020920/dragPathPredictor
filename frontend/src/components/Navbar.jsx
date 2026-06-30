import React from 'react';
import { Link } from 'react-router-dom';
import { Navbar, Nav, Container, NavDropdown } from 'react-bootstrap';
import logoutImg from '../assets/logout.svg';
import loginImg from '../assets/login.svg';
import navLinks from '../utils/navLinks.json'; // Importa el archivo JSON

const CustomNavbar = ({ isAuthenticated, onLogout }) => {
  // Filtra los enlaces del dropdown
  const dropdownLinks = navLinks.filter(link => link.dropdown);

  return (
    <Navbar bg="dark" variant="dark" expand="lg">
      <Container>
        <Navbar.Brand as={Link} to="/home">Langrangian Leeway</Navbar.Brand>
        <Navbar.Toggle aria-controls="navbarNav" />
        <Navbar.Collapse id="navbarNav">
          <Nav className="mx-auto">
            {navLinks.map((link, index) => {
              // Si el enlace requiere autenticación, verifica si el usuario está autenticado
              if (link.auth && !isAuthenticated) {
                return null;
              }
              // Ignora los enlaces del dropdown en la navegación principal
              if (link.dropdown) {
                return null;
              }
              return (
                <Nav.Link as={Link} to={link.path} key={index}>
                  {link.name}
                </Nav.Link>
              );
            })}
            {dropdownLinks.length > 0 && (
              <NavDropdown title="Más" id="basic-nav-dropdown">
                {dropdownLinks.map((link, index) => (
                  <NavDropdown.Item as={Link} to={link.path} key={index}>
                    {link.name}
                  </NavDropdown.Item>
                ))}
              </NavDropdown>
            )}
          </Nav>
          <Nav>
            {isAuthenticated ? (
              <Nav.Link onClick={onLogout}>
                <img src={logoutImg} alt="Logout"/>
              </Nav.Link>
            ) : (
              <Nav.Link as={Link} to="/login">
                <img src={loginImg} alt="Login"/>
              </Nav.Link>
            )}
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
};

export default CustomNavbar;




