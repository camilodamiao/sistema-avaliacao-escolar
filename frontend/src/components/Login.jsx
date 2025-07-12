// src/components/Login.jsx
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

function Login() {
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [senha, setSenha] = useState('')
  const [erro, setErro] = useState('')
  const [carregando, setCarregando] = useState(false)

  const handleLogin = async (e) => {
    e.preventDefault()
    setErro('')
    setCarregando(true)

    try {
      // Por enquanto, vamos simular o login
      // Depois conectamos com a API real
      
      // Simulação de validação
      if (email === 'michelle.vilas@solare.edu.br' && senha === '123456') {
        // Salvar dados do usuário (temporário)
        localStorage.setItem('usuario', JSON.stringify({
          nome: 'Michelle Vilas Boas',
          email: email,
          tipo: 'professor'
        }))
        navigate('/')
      } else if (email === 'marcia.mello@solare.edu.br' && senha === '123456') {
        localStorage.setItem('usuario', JSON.stringify({
          nome: 'Márcia Mello',
          email: email,
          tipo: 'coordenador'
        }))
        navigate('/')
      } else {
        setErro('Email ou senha incorretos')
      }
    } catch (error) {
      setErro('Erro ao fazer login')
    } finally {
      setCarregando(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 to-yellow-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-xl p-8 w-full max-w-md">
        {/* Logo e Título */}
        <div className="text-center mb-8">
          <img 
            src="public/images/Logo Colegio Solare.png"
            alt="Colégio Solare" 
            className="h-20 w-auto mx-auto mb-4"
          />
          <h1 className="text-2xl font-bold text-gray-800">
            Sistema de Avaliação
          </h1>
          <p className="text-gray-600 mt-2">
            Faça login para continuar
          </p>
        </div>

        {/* Formulário */}
        <form onSubmit={handleLogin} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Email
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
              placeholder="seu.email@solare.edu.br"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Senha
            </label>
            <input
              type="password"
              value={senha}
              onChange={(e) => setSenha(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
              placeholder="Digite sua senha"
              required
            />
          </div>

          {erro && (
            <div className="bg-red-50 text-red-600 p-3 rounded-lg text-sm">
              {erro}
            </div>
          )}

          <button
            type="submit"
            disabled={carregando}
            className="w-full bg-orange-500 hover:bg-orange-600 text-white font-medium py-3 rounded-lg transition-colors disabled:opacity-50"
          >
            {carregando ? 'Entrando...' : 'Entrar'}
          </button>
        </form>

        {/* Dica temporária */}
        <div className="mt-6 p-4 bg-gray-50 rounded-lg text-sm text-gray-600">
          <p className="font-semibold mb-1">Credenciais de teste:</p>
          <p>Professor: michelle.vilas@solare.edu.br</p>
          <p>Coordenador: marcia.mello@solare.edu.br</p>
          <p>Senha: 123456</p>
        </div>
      </div>
    </div>
  )
}

export default Login