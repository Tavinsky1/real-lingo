import axios from 'axios';

const API_BASE_URL = 'https://api.lingoreal.com';

export const fetchTongueTwisters = async () => {
    const response = await axios.get(`${API_BASE_URL}/tongue-twisters`);
    return response.data;
};

export const fetchFamousQuotes = async () => {
    const response = await axios.get(`${API_BASE_URL}/famous-quotes`);
    return response.data;
};

export const fetchRegionalExpressions = async () => {
    const response = await axios.get(`${API_BASE_URL}/regional-expressions`);
    return response.data;
};

export const fetchJokes = async () => {
    const response = await axios.get(`${API_BASE_URL}/jokes`);
    return response.data;
};

export const fetchInsults = async () => {
    const response = await axios.get(`${API_BASE_URL}/insults`);
    return response.data;
};