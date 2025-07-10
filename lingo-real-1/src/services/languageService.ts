import { TongueTwister } from '../models/content';
import tongueTwistersData from '../data/tongueTwisters';
import famousQuotesData from '../data/famousQuotes';
import regionalExpressionsData from '../data/regionalExpressions';
import jokesData from '../data/jokes';
import insultsData from '../data/insults';

export const getTongueTwisters = (): TongueTwister[] => {
    return tongueTwistersData;
};

export const getFamousQuotes = (): string[] => {
    return famousQuotesData;
};

export const getRegionalExpressions = (): string[] => {
    return regionalExpressionsData;
};

export const getJokes = (): string[] => {
    return jokesData;
};

export const getInsults = (): string[] => {
    return insultsData;
};