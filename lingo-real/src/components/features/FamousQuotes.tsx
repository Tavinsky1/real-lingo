import React from 'react';
import famousQuotes from '../../data/famousQuotes';
import Card from '../common/Card';

const FamousQuotes: React.FC = () => {
    return (
        <div>
            <h2>Famous Quotes</h2>
            {famousQuotes.map((quote, index) => (
                <Card key={index}>
                    <blockquote>
                        <p>{quote.text}</p>
                        <footer>- {quote.author}</footer>
                    </blockquote>
                </Card>
            ))}
        </div>
    );
};

export default FamousQuotes;