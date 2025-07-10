import React from 'react';
import TongueTwisters from './features/TongueTwisters';
import FamousQuotes from './features/FamousQuotes';
import RegionalExpressions from './features/RegionalExpressions';
import Jokes from './features/Jokes';
import Insults from './features/Insults';

const Dashboard: React.FC = () => {
    return (
        <div>
            <h1>Lingo Real Dashboard</h1>
            <TongueTwisters />
            <FamousQuotes />
            <RegionalExpressions />
            <Jokes />
            <Insults />
        </div>
    );
};

export default Dashboard;