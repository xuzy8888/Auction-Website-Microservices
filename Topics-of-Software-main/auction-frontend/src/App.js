import React, { useMemo, useState } from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import './static/css/style.css';
import 'bootstrap/dist/js/bootstrap.bundle.min';

import Listings from './components/Home';
import Register from './components/Register';
import Login from "./components/Login";
import Navbar from './components/Navbar';
import Profile from "./components/Profile";
import SubmitListingForm from './components/SubmitListing';
import useLocalStorage from './hooks/useLocalStorage';

function App() {
  const [user, setUser] = useLocalStorage("user",null);
  const isLoggedIn = useMemo(() => !!user, [user]);
  const handleLogin = (userData) => {
    setUser(userData.user);
  };

  const handleLogout = () => {
    setUser(null);
  };


  return (
    <Router>
      <Navbar isLoggedIn={isLoggedIn} user={user} onLogout={handleLogout} />
      <Routes>
        <Route path="/" element={<Listings />} />
        <Route path="/login" element={<Login onLogin={handleLogin} />} />
        <Route path="/register" element={<Register />} />
        <Route path="/profile" element={<Profile user={user} />} />
        <Route path="/submit-listing" element={<SubmitListingForm/>} />
        {/* other routes */}
      </Routes>
    </Router>
  );
}

export default App;
