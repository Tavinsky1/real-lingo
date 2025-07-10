import React from 'react';
import jokesData from '../../data/jokes';
import Card from '../common/Card';

const Jokes: React.FC = () => {
    return (
        <div>
            <h2>Jokes</h2>
            {jokesData.map((joke, index) => (
                <Card key={index}>
                    <p>{joke}</p>
                </Card>
            ))}
        </div>
    );
};

export default Jokes;