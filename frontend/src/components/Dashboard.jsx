// src/components/Dashboard.jsx
import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../services/api'

function Dashboard() {
  const navigate = useNavigate()
  const [turmas, setTurmas] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  
  // Pegar dados do usuário do localStorage
  const usuario = JSON.parse(localStorage.getItem('usuario') || '{}')

  useEffect(() => {
    // Se não tem usuário logado, redireciona para login
    if (!usuario.email) {
      navigate('/login')
      return
    }
    
    buscarTurmas()
  }, [])

  const buscarTurmas = async () => {
    try {
      setLoading(true)
      
      // Por enquanto, passar tipo de usuário como query param
      const response = await api.get('/turmas', {
        params: {
          usuario_tipo: usuario.tipo,
        }
      })
      
      setTurmas(response.data)
      setError(null)
    } catch (err) {
      setError('Erro ao carregar turmas')
      console.error('Erro:', err)
    } finally {
      setLoading(false)
    }
  }

  // Se está carregando, mostra loading
  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-orange-500">
          <svg className="animate-spin h-12 w-12" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"/>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
          </svg>
          <p className="mt-4 text-gray-600">Carregando turmas...</p>
        </div>
      </div>
    )
  }

  // Se tem erro, mostra mensagem
  if (error) {
    return (
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg">
        <p className="font-bold">Ops! Algo deu errado</p>
        <p>{error}</p>
        <button 
          onClick={buscarTurmas}
          className="mt-2 bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
        >
          Tentar novamente
        </button>
      </div>
    )
  }

  return (
    <div className="p-4">
      {/* Header com informações do usuário */}
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-800 mb-2">
          {usuario.tipo === 'coordenador' ? 'Turmas Supervisionadas' : 'Minhas Turmas'}
        </h2>
        <p className="text-gray-600">
          {usuario.tipo === 'coordenador' 
            ? 'Visualize as turmas dos professores que você coordena'
            : 'Selecione uma turma para iniciar as avaliações do dia'
          }
        </p>
      </div>
      
      {/* Grid de turmas */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {turmas.map(turma => (
          <div 
            key={turma.id}
            onClick={() => navigate(`/turma/${turma.id}`)}
            className="bg-white rounded-xl shadow-md hover:shadow-xl transition-all duration-300 overflow-hidden group cursor-pointer"
          >
            {/* Cabeçalho colorido do card */}
            <div className={`p-4 ${
              turma.nivel === 'infantil' 
                ? 'bg-gradient-to-r from-orange-400 to-yellow-400' 
                : 'bg-gradient-to-r from-orange-500 to-red-400'
            }`}>
              <h3 className="text-xl font-bold text-white">
                {turma.serie} {turma.turma}
              </h3>
            </div>
            
            {/* Corpo do card */}
            <div className="p-6">
              {/* Mostrar professor se tiver */}
              {turma.professor_nome && (
                <div className="mb-4 text-sm text-gray-600">
                  <p className="font-semibold">Professor(a):</p>
                  <p>{turma.professor_nome}</p>
                </div>
              )}
              
              <div className="flex items-center justify-between mb-4">
                <div>
                  <p className="text-3xl font-bold text-orange-600">
                    {turma.quantidade_atual || 0}
                  </p>
                  <p className="text-gray-600 text-sm">alunos</p>
                </div>
                <div className="text-orange-400">
                  <svg className="w-12 h-12" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3zM6 8a2 2 0 11-4 0 2 2 0 014 0zM16 18v-3a5.972 5.972 0 00-.75-2.906A3.005 3.005 0 0119 15v3h-3zM4.75 12.094A5.973 5.973 0 004 15v3H1v-3a3 3 0 013.75-2.906z"/>
                  </svg>
                </div>
              </div>
              
              <div className="space-y-2 text-sm text-gray-600 mb-4">
                <p>📅 Ano: {turma.ano_letivo}</p>
                <p>🕐 Período: {turma.periodo}</p>
              </div>
              
              <button className="w-full bg-orange-500 hover:bg-orange-600 text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200 group-hover:scale-105 transform">
                Acessar Turma →
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Card de resumo */}
      {turmas.length > 0 && (
        <div className="mt-8 bg-gradient-to-r from-orange-100 to-yellow-100 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-2">
            📊 Resumo do Dia
          </h3>
          <p className="text-gray-600">
            Você tem <span className="font-bold text-orange-600">{turmas.length} turmas</span> com 
            <span className="font-bold text-orange-600"> {turmas.reduce((total, turma) => total + (turma.quantidade_atual || 0), 0)} alunos</span> no total para avaliar hoje.
          </p>
        </div>
      )}
    </div>
  )
}

export default Dashboard