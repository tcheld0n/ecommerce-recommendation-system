import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { useBookStore } from '@/stores/bookStore'
import { useCartStore } from '@/stores/cartStore'
import { useToast } from '@/hooks/use-toast'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Star, ShoppingCart, Heart } from 'lucide-react'
import { BookCard } from '@/components/books/BookCard'
import { BookRecommendation } from '@/types/recommendation'
import { recommendationService } from '@/services/recommendationService'

export function BookDetails() {
  const { id } = useParams<{ id: string }>()
  const { currentBook, getBook, isLoading } = useBookStore()
  const { addToCart } = useCartStore()
  const { toast } = useToast()
  const [similarBooks, setSimilarBooks] = useState<BookRecommendation[]>([])
  const [quantity, setQuantity] = useState(1)

  useEffect(() => {
    if (id) {
      getBook(id)
    }
  }, [id, getBook])

  useEffect(() => {
    if (id) {
      const fetchSimilarBooks = async () => {
        try {
          const books = await recommendationService.getSimilarBooks(id, 4)
          setSimilarBooks(books)
        } catch (error) {
          console.error('Error fetching similar books:', error)
        }
      }
      fetchSimilarBooks()
    }
  }, [id])

  const handleAddToCart = async () => {
    if (!currentBook) return

    try {
      await addToCart(currentBook.id, quantity)
      toast({
        title: "Livro adicionado ao carrinho",
        description: `${currentBook.title} foi adicionado ao seu carrinho.`,
      })
    } catch (error) {
      toast({
        title: "Erro",
        description: "Não foi possível adicionar o livro ao carrinho.",
        variant: "destructive",
      })
    }
  }

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(price)
  }

  const renderStars = (rating: number) => {
    const stars = []
    const fullStars = Math.floor(rating)
    const hasHalfStar = rating % 1 !== 0

    for (let i = 0; i < fullStars; i++) {
      stars.push(
        <Star key={i} className="w-5 h-5 fill-yellow-400 text-yellow-400" />
      )
    }

    if (hasHalfStar) {
      stars.push(
        <Star key="half" className="w-5 h-5 fill-yellow-400 text-yellow-400" />
      )
    }

    const emptyStars = 5 - Math.ceil(rating)
    for (let i = 0; i < emptyStars; i++) {
      stars.push(
        <Star key={`empty-${i}`} className="w-5 h-5 text-gray-300" />
      )
    }

    return stars
  }

  if (isLoading) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="animate-pulse">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div className="bg-gray-200 h-96 rounded-lg"></div>
            <div className="space-y-4">
              <div className="bg-gray-200 h-8 rounded"></div>
              <div className="bg-gray-200 h-6 rounded w-3/4"></div>
              <div className="bg-gray-200 h-4 rounded w-1/2"></div>
              <div className="bg-gray-200 h-32 rounded"></div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (!currentBook) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Livro não encontrado</h1>
          <p className="text-gray-600">O livro que você está procurando não existe.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Book Image */}
        <div className="aspect-[3/4] overflow-hidden rounded-lg">
          <img
            src={currentBook.cover_image_url || '/placeholder-book.jpg'}
            alt={currentBook.title}
            className="w-full h-full object-cover"
          />
        </div>

        {/* Book Details */}
        <div className="space-y-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">{currentBook.title}</h1>
            <p className="text-xl text-gray-600 mb-4">por {currentBook.author}</p>
            
            <div className="flex items-center mb-4">
              <div className="flex items-center">
                {renderStars(currentBook.average_rating)}
              </div>
              <span className="ml-2 text-sm text-gray-500">
                {currentBook.average_rating.toFixed(1)} ({currentBook.total_reviews} avaliações)
              </span>
            </div>

            <div className="text-3xl font-bold text-green-600 mb-6">
              {formatPrice(currentBook.price)}
            </div>
          </div>

          {/* Description */}
          {currentBook.description && (
            <div>
              <h3 className="text-lg font-semibold mb-2">Sinopse</h3>
              <p className="text-gray-700 leading-relaxed">{currentBook.description}</p>
            </div>
          )}

          {/* Book Info */}
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="font-semibold">Editora:</span>
              <p className="text-gray-600">{currentBook.publisher}</p>
            </div>
            <div>
              <span className="font-semibold">Ano:</span>
              <p className="text-gray-600">{currentBook.published_year}</p>
            </div>
            <div>
              <span className="font-semibold">ISBN:</span>
              <p className="text-gray-600">{currentBook.isbn}</p>
            </div>
            <div>
              <span className="font-semibold">Estoque:</span>
              <p className="text-gray-600">{currentBook.stock_quantity} unidades</p>
            </div>
          </div>

          {/* Add to Cart */}
          <Card>
            <CardHeader>
              <CardTitle>Comprar</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center space-x-4">
                <label htmlFor="quantity" className="font-semibold">
                  Quantidade:
                </label>
                <select
                  id="quantity"
                  value={quantity}
                  onChange={(e) => setQuantity(parseInt(e.target.value))}
                  className="border rounded px-3 py-1"
                >
                  {Array.from({ length: Math.min(10, currentBook.stock_quantity) }, (_, i) => (
                    <option key={i + 1} value={i + 1}>
                      {i + 1}
                    </option>
                  ))}
                </select>
              </div>

              <div className="flex space-x-4">
                <Button
                  onClick={handleAddToCart}
                  className="flex-1 flex items-center space-x-2"
                  disabled={currentBook.stock_quantity === 0}
                >
                  <ShoppingCart className="w-4 h-4" />
                  <span>Adicionar ao Carrinho</span>
                </Button>
                <Button variant="outline" className="flex items-center space-x-2">
                  <Heart className="w-4 h-4" />
                  <span>Favoritar</span>
                </Button>
              </div>

              {currentBook.stock_quantity === 0 && (
                <p className="text-red-600 text-sm">Produto fora de estoque</p>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Similar Books */}
      {similarBooks.length > 0 && (
        <div className="mt-12">
          <h2 className="text-2xl font-bold mb-6">Livros Similares</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {similarBooks.map((rec) => (
              <BookCard key={rec.book_id} book={rec.book!} />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
