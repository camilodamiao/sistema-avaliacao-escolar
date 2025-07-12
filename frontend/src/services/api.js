// src/services/api.js
import axios from 'axios'

// Cria uma instância do axios com a URL base do seu backend
const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  }
})

// Interceptor para log de erros (útil para debug)
api.interceptors.response.use(
  response => response,
  error => {
    console.error('Erro na API:', error)
    return Promise.reject(error)
  }
)

export default api