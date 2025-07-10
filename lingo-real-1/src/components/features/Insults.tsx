import React from 'react';
import insultsData from '../../data/insults';

const Insults: React.FC = () => {
    return (
        <div>
            <h2>Light-hearted Insults</h2>
            <ul>
                {insultsData.map((insult, index) => (
                    <li key={index}>{insult}</li>
                ))}
            </ul>
        </div>
    );
};

export default Insults;