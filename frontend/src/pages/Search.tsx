import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { useBookStore } from '@/stores/bookStore'
import { BookCard } from '@/components/books/BookCard'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Search as SearchIcon, Filter } from 'lucide-react'
import { Pagination } from '@/components/common/Pagination'

export function Search() {
  const [searchParams, setSearchParams] = useSearchParams()
  const { books, searchBooks, isLoading, categories, getCategories } = useBookStore()
  
  const [query, setQuery] = useState(searchParams.get('q') || '')
  const [filters, setFilters] = useState({
    category_id: searchParams.get('category_id') || '',
    min_price: searchParams.get('min_price') || '',
    max_price: searchParams.get('max_price') || '',
    min_rating: searchParams.get('min_rating') || '',
    sort_by: searchParams.get('sort_by') || 'relevance',
  })
  const limit = 20
  const pageFromURL = parseInt(searchParams.get('page') || '1', 10)
  const [page, setPage] = useState(pageFromURL || 1)
  const [hasNextPage, setHasNextPage] = useState(false)

  useEffect(() => {
    getCategories()
  }, [getCategories])

  // Sincroniza state com URL params e executa busca quando URL muda
  useEffect(() => {
    const searchQuery = searchParams.get('q') || ''
    const pageParam = searchParams.get('page')
    const categoryParam = searchParams.get('category_id') || ''
    const minPriceParam = searchParams.get('min_price') || ''
    const maxPriceParam = searchParams.get('max_price') || ''
    const minRatingParam = searchParams.get('min_rating') || ''
    const sortByParam = searchParams.get('sort_by') || 'relevance'
    
    // Atualiza a página se houver parâmetro na URL
    const pageNum = pageParam ? parseInt(pageParam, 10) : 1
    if (!isNaN(pageNum) && pageNum > 0) {
      setPage(pageNum)
    }
    
    // Sincroniza os filtros com a URL
    setQuery(searchQuery)
    setFilters({
      category_id: categoryParam,
      min_price: minPriceParam,
      max_price: maxPriceParam,
      min_rating: minRatingParam,
      sort_by: sortByParam,
    })
    
    // Executa busca se houver parâmetros de busca na URL
    if (searchQuery || categoryParam || minPriceParam || maxPriceParam || minRatingParam) {
      // Executa busca com os valores da URL diretamente
      const searchData = {
        query: searchQuery || undefined,
        category_id: categoryParam || undefined,
        min_price: minPriceParam ? parseFloat(minPriceParam) : undefined,
        max_price: maxPriceParam ? parseFloat(maxPriceParam) : undefined,
        min_rating: minRatingParam ? parseFloat(minRatingParam) : undefined,
        sort_by: sortByParam as any,
        page: !isNaN(pageNum) && pageNum > 0 ? pageNum : 1,
        limit,
      }
      
      // Pequeno delay para garantir que os states foram atualizados
      setTimeout(() => {
        searchBooks(searchData)
      }, 50)
    }
  }, [searchParams, searchBooks, limit])

  useEffect(() => {
    // Atualiza hasNextPage baseado na quantidade de resultados retornados
    // Se retornou exatamente o limite, provavelmente há mais páginas
    setHasNextPage(books.length === limit)
  }, [books.length, limit])

  const performSearch = () => {
    const searchData = {
      query: query || undefined,
      category_id: filters.category_id || undefined,
      min_price: filters.min_price ? parseFloat(filters.min_price) : undefined,
      max_price: filters.max_price ? parseFloat(filters.max_price) : undefined,
      min_rating: filters.min_rating ? parseFloat(filters.min_rating) : undefined,
      sort_by: filters.sort_by as any,
      page,
      limit,
    }

    searchBooks(searchData)
  }

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    setPage(1)
    updateURL()
    performSearch()
  }

  const updateURL = () => {
    const params = new URLSearchParams()
    if (query) params.set('q', query)
    if (filters.category_id) params.set('category_id', filters.category_id)
    if (filters.min_price) params.set('min_price', filters.min_price)
    if (filters.max_price) params.set('max_price', filters.max_price)
    if (filters.min_rating) params.set('min_rating', filters.min_rating)
    if (filters.sort_by !== 'relevance') params.set('sort_by', filters.sort_by)
    if (page > 1) params.set('page', page.toString())
    
    setSearchParams(params)
  }

  const handlePageChange = (newPage: number) => {
    if (newPage < 1) return
    setPage(newPage)
    updateURL()
    performSearch()
    // Scroll para o topo dos resultados
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const clearFilters = () => {
    setFilters({
      category_id: '',
      min_price: '',
      max_price: '',
      min_rating: '',
      sort_by: 'relevance',
    })
    setQuery('')
    setPage(1)
    setSearchParams({})
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-6">Buscar Livros</h1>
        
        {/* Search Form */}
        <form onSubmit={handleSearch} className="mb-6">
          <div className="flex gap-4">
            <div className="flex-1">
              <Input
                type="text"
                placeholder="Buscar por título, autor, ISBN..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="w-full"
              />
            </div>
            <Button type="submit" className="flex items-center space-x-2">
              <SearchIcon className="w-4 h-4" />
              <span>Buscar</span>
            </Button>
          </div>
        </form>

        {/* Filters */}
        <div className="bg-gray-50 p-4 rounded-lg">
          <div className="flex items-center space-x-2 mb-4">
            <Filter className="w-5 h-5" />
            <span className="font-semibold">Filtros</span>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Categoria</label>
              <Select
                value={filters.category_id}
                onValueChange={(value) =>
                  setFilters({
                    ...filters,
                    category_id: value === "__all__" ? "" : value,
                  })
                }
              >
                <SelectTrigger>
                  <SelectValue placeholder="Todas as categorias" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="__all__">Todas as categorias</SelectItem>
                  {categories.map((category) => (
                    <SelectItem key={category.id} value={category.id}>
                      {category.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Preço Mínimo</label>
              <Input
                type="number"
                placeholder="R$ 0,00"
                value={filters.min_price}
                onChange={(e) => setFilters({ ...filters, min_price: e.target.value })}
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Preço Máximo</label>
              <Input
                type="number"
                placeholder="R$ 100,00"
                value={filters.max_price}
                onChange={(e) => setFilters({ ...filters, max_price: e.target.value })}
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Avaliação Mínima</label>
              <Select
                value={filters.min_rating}
                onValueChange={(value) =>
                  setFilters({ ...filters, min_rating: value === "__any__" ? "" : value })
                }
              >
                <SelectTrigger>
                  <SelectValue placeholder="Qualquer avaliação" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="__any__">Qualquer avaliação</SelectItem>
                  <SelectItem value="4">4+ estrelas</SelectItem>
                  <SelectItem value="3">3+ estrelas</SelectItem>
                  <SelectItem value="2">2+ estrelas</SelectItem>
                  <SelectItem value="1">1+ estrelas</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Ordenar por</label>
              <Select
                value={filters.sort_by}
                onValueChange={(value) => setFilters({ ...filters, sort_by: value })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="relevance">Relevância</SelectItem>
                  <SelectItem value="price_asc">Preço: Menor para Maior</SelectItem>
                  <SelectItem value="price_desc">Preço: Maior para Menor</SelectItem>
                  <SelectItem value="rating">Melhor Avaliados</SelectItem>
                  <SelectItem value="newest">Mais Recentes</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="flex justify-between items-center mt-4">
            <Button variant="outline" onClick={clearFilters}>
              Limpar Filtros
            </Button>
            <Button onClick={() => { 
              setPage(1)
              updateURL()
              performSearch()
            }}>
              Aplicar Filtros
            </Button>
          </div>
        </div>
      </div>

      {/* Results */}
      <div>
        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {Array.from({ length: 8 }).map((_, i) => (
              <div key={i} className="animate-pulse">
                <div className="bg-gray-200 h-64 rounded-lg mb-4"></div>
                <div className="bg-gray-200 h-4 rounded mb-2"></div>
                <div className="bg-gray-200 h-4 rounded w-3/4"></div>
              </div>
            ))}
          </div>
        ) : books.length > 0 ? (
          <>
            <div className="mb-6 flex justify-between items-center">
              <p className="text-gray-600">
                Mostrando {books.length} {books.length === 1 ? 'livro' : 'livros'}
                {page > 1 && ` (Página ${page})`}
              </p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              {books.map((book) => (
                <BookCard key={book.id} book={book} />
              ))}
            </div>
            <Pagination
              currentPage={page}
              hasNextPage={hasNextPage}
              hasPrevPage={page > 1}
              onPageChange={handlePageChange}
              className="mt-8"
            />
          </>
        ) : (
          <div className="text-center py-12">
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              Nenhum livro encontrado
            </h3>
            <p className="text-gray-600 mb-4">
              Tente ajustar seus filtros de busca
            </p>
            <Button onClick={clearFilters}>
              Limpar Filtros
            </Button>
          </div>
        )}
      </div>
    </div>
  )
}
