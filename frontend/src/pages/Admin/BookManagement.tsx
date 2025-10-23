import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Plus, Search, Edit, Trash2 } from 'lucide-react'

export function BookManagement() {
  const [searchQuery, setSearchQuery] = useState('')
  // TODO: Implement real data fetching and management

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold">Gestão de Livros</h1>
          <p className="text-gray-600">Gerencie o catálogo de livros</p>
        </div>
        <Button>
          <Plus className="w-4 h-4 mr-2" />
          Adicionar Livro
        </Button>
      </div>

      {/* Search and Filters */}
      <Card className="mb-6">
        <CardContent className="p-6">
          <div className="flex gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <Input
                  placeholder="Buscar livros..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <Button variant="outline">Filtros</Button>
          </div>
        </CardContent>
      </Card>

      {/* Books Table */}
      <Card>
        <CardHeader>
          <CardTitle>Lista de Livros</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-gray-500">
            Tabela de livros será implementada aqui
            <br />
            <small>Incluirá: título, autor, preço, estoque, ações</small>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
