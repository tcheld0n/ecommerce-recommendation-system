import { Link } from 'react-router-dom'
import { Star, ShoppingCart } from 'lucide-react'
import { Book } from '@/types/book'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardFooter } from '@/components/ui/card'
import { useCartStore } from '@/stores/cartStore'
import { useToast } from '@/hooks/use-toast'

interface BookCardProps {
  book: Book
}

export function BookCard({ book }: BookCardProps) {
  const { addToCart } = useCartStore()
  const { toast } = useToast()

  const handleAddToCart = async () => {
    try {
      await addToCart(book.id, 1)
      toast({
        title: "Livro adicionado ao carrinho",
        description: `${book.title} foi adicionado ao seu carrinho.`,
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
        <Star key={i} className="w-4 h-4 fill-yellow-400 text-yellow-400" />
      )
    }

    if (hasHalfStar) {
      stars.push(
        <Star key="half" className="w-4 h-4 fill-yellow-400 text-yellow-400" />
      )
    }

    const emptyStars = 5 - Math.ceil(rating)
    for (let i = 0; i < emptyStars; i++) {
      stars.push(
        <Star key={`empty-${i}`} className="w-4 h-4 text-gray-300" />
      )
    }

    return stars
  }

  return (
    <Card className="group hover:shadow-lg transition-shadow duration-200">
      <Link to={`/books/${book.id}`}>
        <div className="aspect-[3/4] overflow-hidden rounded-t-lg">
          <img
            src={book.cover_image_url || '/placeholder-book.jpg'}
            alt={book.title}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-200"
          />
        </div>
      </Link>
      
      <CardContent className="p-4">
        <Link to={`/books/${book.id}`}>
          <h3 className="font-semibold text-lg mb-2 line-clamp-2 group-hover:text-blue-600 transition-colors">
            {book.title}
          </h3>
        </Link>
        
        <p className="text-gray-600 mb-2 line-clamp-1">{book.author}</p>
        
        <div className="flex items-center mb-2">
          <div className="flex items-center">
            {renderStars(book.average_rating)}
          </div>
          <span className="ml-2 text-sm text-gray-500">
            ({book.total_reviews})
          </span>
        </div>
        
        <div className="flex items-center justify-between">
          <span className="text-xl font-bold text-green-600">
            {formatPrice(book.price)}
          </span>
          <Button
            size="sm"
            onClick={handleAddToCart}
            className="flex items-center space-x-1"
          >
            <ShoppingCart className="w-4 h-4" />
            <span>Adicionar</span>
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
