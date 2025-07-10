import React from 'react';

interface CardProps {
    title: string;
    content: React.ReactNode;
    footer?: React.ReactNode;
}

const Card: React.FC<CardProps> = ({ title, content, footer }) => {
    return (
        <div className="card">
            <h2 className="card-title">{title}</h2>
            <div className="card-content">{content}</div>
            {footer && <div className="card-footer">{footer}</div>}
        </div>
    );
};

export default Card;