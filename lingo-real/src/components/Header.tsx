import React from 'react';
import { Link } from 'react-router-dom';

const Header: React.FC = () => {
    return (
        <header>
            <h1>Lingo Real</h1>
            <nav>
                <ul>
                    <li><Link to="/">Dashboard</Link></li>
                    <li><Link to="/tongue-twisters">Tongue Twisters</Link></li>
                    <li><Link to="/famous-quotes">Famous Quotes</Link></li>
                    <li><Link to="/regional-expressions">Regional Expressions</Link></li>
                    <li><Link to="/jokes">Jokes</Link></li>
                    <li><Link to="/insults">Insults</Link></li>
                </ul>
            </nav>
        </header>
    );
};

export default Header;