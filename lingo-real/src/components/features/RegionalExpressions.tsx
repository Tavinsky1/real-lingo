import React from 'react';
import regionalExpressionsData from '../../data/regionalExpressions';

const RegionalExpressions: React.FC = () => {
    return (
        <div>
            <h2>Regional Expressions</h2>
            <ul>
                {regionalExpressionsData.map((expression, index) => (
                    <li key={index}>
                        <strong>{expression.phrase}</strong>: {expression.meaning}
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default RegionalExpressions;