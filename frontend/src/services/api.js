import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 second timeout
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`Making ${config.method?.toUpperCase()} request to ${config.url}`);
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    console.log(`Received response from ${response.config.url}:`, response.status);
    return response;
  },
  (error) => {
    console.error('Response error:', error);

    if (error.response) {
      // Server responded with error status
      const message = error.response.data?.detail ||
                     error.response.data?.message ||
                     'Server error occurred';
      console.error('Server error:', error.response.status, message);
      throw new Error(message);
    } else if (error.request) {
      // Request was made but no response received
      console.error('Network error - no response received');
      throw new Error('Network error. Please check your connection and try again.');
    } else {
      // Something else happened
      console.error('Error:', error.message);
      throw new Error(error.message || 'An unexpected error occurred');
    }
  }
);

// API endpoints
export const salaryApi = {
  // Analyze offer letter
  analyzeOffer: async (formData) => {
    try {
      const response = await api.post('/api/analyze-offer', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      console.error('Error analyzing offer:', error);
      throw error;
    }
  },

  // Contribute salary data
  contributeSalary: async (salaryData) => {
    try {
      const formData = new FormData();

      Object.keys(salaryData).forEach(key => {
        if (Array.isArray(salaryData[key])) {
          formData.append(key, salaryData[key].join(','));
        } else if (typeof salaryData[key] === 'object') {
          formData.append(key, JSON.stringify(salaryData[key]));
        } else {
          formData.append(key, salaryData[key]);
        }
      });

      const response = await api.post('/api/contribute-salary', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      console.error('Error contributing salary data:', error);
      throw error;
    }
  },

  // Health check
  healthCheck: async () => {
    try {
      const response = await api.get('/api/health');
      return response.data;
    } catch (error) {
      console.error('Health check failed:', error);
      throw error;
    }
  },
};

export default api;