import React from 'react';

class Header extends React.Component {
  render() {
    return (
      <div className='header'>
        <div className='header-logo'>
          <img src='moxie_logo.png' alt="Logo" className="logo" />
        </div>
        <div className='header-title'>
          <h1>Moxie</h1>
        </div>
      </div>
    );
  }
}

export default Header;