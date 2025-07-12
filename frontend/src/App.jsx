// src/App.jsx
import Dashboard from './components/Dashboard'

function App() {
  return (
    <div className="min-h-screen bg-orange-50">
      {/* Header com estilo Solare */}
      <header className="bg-white shadow-md border-b-4 border-orange-500">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              {/* Tente diferentes caminhos para o logo */}
              <img 
                src="/images/Logo Colegio Solare.png"  // Se for PNG
                // src="/images/logo.jpg"  // Se for JPG
                // src="/images/logo.svg"  // Se for SVG
                // src="/logo.png"  // Se estiver direto em public
                alt="Colégio Solare" 
                className="h-12 w-auto"
                onError={(e) => {
                  // Se não carregar, mostra texto
                  e.target.style.display = 'none';
                }}
              />
              {/* Texto alternativo caso o logo não carregue */}
              <div className="flex items-center">
                <div className="w-12 h-12 bg-orange-500 rounded-full flex items-center justify-center text-white font-bold text-xl mr-3">
                  S
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-gray-800">
                    Sistema de Avaliação
                  </h1>
                  <p className="text-orange-600 text-sm">Colégio Solare</p>
                </div>
              </div>
            </div>
            <div className="text-right">
              <p className="text-gray-600 font-medium">Olá, Professor(a)</p>
              <p className="text-sm text-gray-500">Manhã - Infantil</p>
            </div>
          </div>
        </div>
      </header>
      
      {/* Main Content */}
      <main className="container mx-auto py-8">
        <Dashboard />
      </main>
    </div>
  )
}

export default App