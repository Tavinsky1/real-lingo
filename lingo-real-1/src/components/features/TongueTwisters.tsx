import React from 'react';
import tongueTwisters from '../../data/tongueTwisters';
import Card from '../common/Card';

const TongueTwisters: React.FC = () => {
    return (
        <div>
            <h2>Tongue Twisters</h2>
            <div>
                {tongueTwisters.map((twister, index) => (
                    <Card key={index}>
                        <p>{twister}</p>
                    </Card>
                ))}
            </div>
        </div>
    );
};

export default TongueTwisters;