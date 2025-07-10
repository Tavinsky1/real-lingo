import React from 'react';

const Footer: React.FC = () => {
    return (
        <footer style={{ textAlign: 'center', padding: '1rem', background: '#f1f1f1' }}>
            <p>&copy; {new Date().getFullYear()} Lingo Real. All rights reserved.</p>
            <nav>
                <a href="/privacy-policy">Privacy Policy</a> | 
                <a href="/terms-of-service">Terms of Service</a>
            </nav>
        </footer>
    );
};

export default Footer;