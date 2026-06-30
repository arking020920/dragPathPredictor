import React, { useState, useEffect } from 'react';
import './App.css'
import { BrowserRouter as Router, Route, Switch, Redirect } from 'react-router-dom';
import CustomNavbar from './components/Navbar';
import Home from './components/Home';
import About from './components/About';
import Contact from './components/Contact';
import Document from './components/Document';
import ToolMap from './components/ToolMap';
import Login from './components/Login';
import ProtectedRoute from './components/ProtectedRoute';
import Footer from './components/Footer';
import Faqs from './components/Faqs';
import TermsofUse from './components/TermsofUse'
import PrivacyPolicy from './components/PrivacyPolicy'

const App = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    const auth = localStorage.getItem('isAuthenticated');
    setIsAuthenticated(auth === 'true');
  }, []);

  const handleLogin = () => {
    setIsAuthenticated(true);
    localStorage.setItem('isAuthenticated', 'true');
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    localStorage.removeItem('isAuthenticated');
  };

  return (
    <div className="body">
      <Router>
        <CustomNavbar isAuthenticated={isAuthenticated} onLogout={handleLogout} />
        <Switch>
          <Route path="/login">
            <Login onLogin={handleLogin} />
          </Route>
          <Route path="/about">
            <About />
          </Route>
          <Route path="/contact">
            <Contact />
          </Route>
          <Route path="/home">
            <Home />
          </Route>
          <Route path="/faqs">
            <Faqs />
          </Route>
          <Route path="/termsofuse">
            <TermsofUse />
          </Route>
          <Route path="/privacypolicy">
            <PrivacyPolicy />
          </Route>
          <ProtectedRoute path="/document" component={Document} isAuthenticated={isAuthenticated} />
          <ProtectedRoute path="/toolmap" component={ToolMap} isAuthenticated={true} />
          <Redirect from="/" to="/home" />
        </Switch>
        <Footer/>
      </Router>
    </div>
  );
};

export default App;
