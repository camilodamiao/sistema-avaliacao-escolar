// src/components/Layout.jsx
import { Outlet, useNavigate } from 'react-router-dom'

function Layout() {
  const navigate = useNavigate()
  const usuario = JSON.parse(localStorage.getItem('usuario') || '{}')
  
  const handleLogout = () => {
    localStorage.removeItem('usuario')
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-orange-50">
      {/* Header fixo */}
      <header className="bg-white shadow-md border-b-4 border-orange-500">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <img 
                src="public/images/Logo Colegio Solare.png"
                alt="Colégio Solare" 
                className="h-12 w-auto"
              />
              <div>
                <h1 className="text-2xl font-bold text-gray-800">
                  Sistema de Avaliação
                </h1>
                <p className="text-orange-600 text-sm">Colégio Solare</p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-gray-600 font-medium">{usuario.nome || 'Usuário'}</p>
              <p className="text-sm text-gray-500 capitalize">{usuario.tipo || 'professor'}</p>
              <button 
                onClick={handleLogout}
                className="text-sm text-orange-600 hover:text-orange-800 mt-1"
              >
                Sair
              </button>
            </div>
          </div>
        </div>
      </header>
      
      {/* Outlet renderiza o componente da rota */}
      <main className="container mx-auto py-8">
        <Outlet />
      </main>
    </div>
  )
}

export default Layout