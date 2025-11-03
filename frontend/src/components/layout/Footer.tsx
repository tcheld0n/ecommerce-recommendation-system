import { Link } from 'react-router-dom'
import { useEffect } from 'react'
import { useFeaturesStore } from '@/stores/features'

export function Footer() {
  const { flags, load, loaded } = useFeaturesStore()
  useEffect(() => { if (!loaded) { load() } }, [loaded, load])
  return (
    <footer className="bg-gray-900 text-white">
      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Logo and Description */}
          <div className="col-span-1 md:col-span-2">
            <div className="flex items-center space-x-2 mb-4">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-lg">B</span>
              </div>
              <span className="text-xl font-bold">Bookstore</span>
            </div>
            <p className="text-gray-300 mb-4">
              Sua livraria online com sistema de recomendação inteligente. 
              Descubra seus próximos livros favoritos.
            </p>
          </div>

          {/* Quick Links */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Links Rápidos</h3>
            <ul className="space-y-2">
              <li>
                <Link to="/" className="text-gray-300 hover:text-white transition">Início</Link>
              </li>
              <li>
                {flags.catalog && (
                  <Link to="/search" className="text-gray-300 hover:text-white transition">Buscar Livros</Link>
                )}
              </li>
              <li>
                {flags.orders && (
                  <Link to="/orders" className="text-gray-300 hover:text-white transition">Meus pedidos</Link>
                )}
              </li>
              <li>
                <Link to="/config" className="text-gray-300 hover:text-white transition">Configuração</Link>
              </li>
              <li>
                {flags.catalog && (
                  <Link to="/categories" className="text-gray-300 hover:text-white transition">Categorias</Link>
                )}
              </li>
            </ul>
          </div>

          {/* Support */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Suporte</h3>
            <ul className="space-y-2">
              <li>
                <Link to="/help" className="text-gray-300 hover:text-white transition">Ajuda</Link>
              </li>
              <li>
                <Link to="/contact" className="text-gray-300 hover:text-white transition">Contato</Link>
              </li>
              <li>
                {flags.shipping && (
                  <Link to="/shipping" className="text-gray-300 hover:text-white transition">Envio</Link>
                )}
              </li>
            </ul>
          </div>
        </div>

        <div className="border-t border-gray-800 mt-8 pt-8 text-center">
          <p className="text-gray-300">
            © 2024 Bookstore. Todos os direitos reservados.
          </p>
        </div>
      </div>
    </footer>
  )
}
