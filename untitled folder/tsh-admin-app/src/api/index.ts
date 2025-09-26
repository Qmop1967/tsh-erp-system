import axios from 'axios';

const API_BASE_URL = 'https://your-tsh-erp-api-url.com/api'; // Replace with your actual API base URL

export const fetchData = async (endpoint: string) => {
    try {
        const response = await axios.get(`${API_BASE_URL}/${endpoint}`);
        return response.data;
    } catch (error) {
        throw new Error(`Error fetching data: ${error.message}`);
    }
};

export const postData = async (endpoint: string, data: any) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/${endpoint}`, data);
        return response.data;
    } catch (error) {
        throw new Error(`Error posting data: ${error.message}`);
    }
};

export const updateData = async (endpoint: string, data: any) => {
    try {
        const response = await axios.put(`${API_BASE_URL}/${endpoint}`, data);
        return response.data;
    } catch (error) {
        throw new Error(`Error updating data: ${error.message}`);
    }
};