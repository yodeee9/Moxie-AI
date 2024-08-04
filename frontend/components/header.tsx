import React from 'react';

class Header extends React.Component {
  render() {
    return (
      <div className='header'>
        <div className='header-logo'>
          <img src='open-rabbit-icon.png' alt="Logo" className="logo" />
        </div>
      </div>
    );
  }
}

export default Header;
