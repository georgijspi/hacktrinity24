import React from 'react';
import { Link } from 'react-router-dom';

function Navbar() {
  return (
    <nav>
      <ul style={{ listStyleType: 'none', padding: 0 }}>
        <li style={{ display: 'inline', marginRight: '10px' }}>
          <Link to="/">Home</Link>
        </li>
        <li style={{ display: 'inline', marginRight: '10px' }}>
          <Link to="/login">Login</Link>
        </li>
        <li style={{ display: 'inline', marginRight: '10px' }}>
          <Link to="/signup">Signup</Link>
        </li>
        <li style={{ display: 'inline', marginRight: '10px' }}>
          <Link to="/dashboard">Dashboard</Link>
        </li>
        {/* You can add more links or conditional rendering based on authentication status */}
      </ul>
    </nav>
  );
}

export default Navbar;
