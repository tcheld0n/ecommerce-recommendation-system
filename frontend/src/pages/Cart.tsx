import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useCartStore } from '@/stores/cartStore'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Trash2, Plus, Minus, ShoppingBag } from 'lucide-react'
import { recommendationService } from '@/services/recommendationService'
import { useFeaturesStore } from '@/stores/features'
import { BookCard } from '@/components/books/BookCard'
import { BookRecommendation } from '@/types/recommendation'

export function Cart() {
  const { cart, getCart, updateCartItem, removeFromCart, clearCart, isLoading, error } = useCartStore()
  const [recommendations, setRecommendations] = useState<BookRecommendation[]>([])
  const [loadingRecommendations, setLoadingRecommendations] = useState(false)
  const { flags, load: loadFlags, loaded: flagsLoaded } = useFeaturesStore()
  const navigate = useNavigate()

  useEffect(() => {
    getCart()
  }, [getCart])

  useEffect(() => {
    if (error) {
      console.error('Cart error:', error)
    }
  }, [error])

  // Garantir que flags estejam carregadas
  useEffect(() => { if (!flagsLoaded) { loadFlags() } }, [flagsLoaded, loadFlags])

  // Carregar recomendações baseadas nas categorias do carrinho (respeitando feature flags)
  useEffect(() => {
    const loadRecommendations = async () => {
      if (!flagsLoaded) return
      if (cart && cart.items.length > 0) {
        try {
          setLoadingRecommendations(true)
          
          const firstBookId = cart.items[0].book_id
          if (firstBookId && flags.similarInCart) {
            const similarBooks = await recommendationService.getSimilarBooks(firstBookId, 8)
            setRecommendations(similarBooks)
          }
        } catch (err) {
          console.error('Erro ao carregar recomendações:', err)
          if (flags.recommendation) {
            try {
              const result = await recommendationService.getPersonalizedRecommendations(8, 'hybrid')
              if (result.recommendations) {
                setRecommendations(result.recommendations)
              }
            } catch (fallbackErr) {
              console.error('Erro ao carregar recomendações personalizadas:', fallbackErr)
            }
          }
        } finally {
          setLoadingRecommendations(false)
        }
      }
    }

    loadRecommendations()
  }, [cart?.items, flagsLoaded, flags.similarInCart, flags.recommendation])

  const handleQuantityChange = async (itemId: string, newQuantity: number) => {
    if (newQuantity <= 0) {
      await removeFromCart(itemId)
    } else {
      await updateCartItem(itemId, newQuantity)
    }
  }

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(price)
  }

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded mb-6"></div>
          <div className="space-y-4">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="bg-gray-200 h-32 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  if (error && !cart) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="text-center">
          <p className="text-red-600 mb-4">Erro ao carregar carrinho: {error}</p>
          <Button onClick={() => getCart()}>Tentar novamente</Button>
        </div>
      </div>
    )
  }

  if (!cart || cart.items.length === 0) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="text-center">
          <ShoppingBag className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Seu carrinho está vazio</h1>
          <p className="text-gray-600 mb-6">Adicione alguns livros para começar</p>
          <Button asChild>
            <Link to="/">Continuar Comprando</Link>
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      {error && (
        <div className="mb-4 p-4 bg-yellow-100 border border-yellow-400 text-yellow-800 rounded">
          <p className="text-sm">{error}</p>
          <Button size="sm" variant="outline" onClick={() => getCart()} className="mt-2">
            Tentar novamente
          </Button>
        </div>
      )}
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Carrinho de Compras</h1>
        <Button variant="outline" onClick={clearCart}>
          Limpar Carrinho
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Cart Items */}
        <div className="lg:col-span-2 space-y-4">
          {cart.items.map((item) => (
            <Card key={item.id}>
              <CardContent className="p-4">
                <div className="flex items-center space-x-4">
                  <Link to={`/books/${item.book_id}`}>
                    <img
                      src={item.book?.cover_image_url || '/placeholder-book.svg'}
                      alt={item.book?.title}
                      className="w-20 h-28 object-cover rounded"
                    />
                  </Link>
                  
                  <div className="flex-1">
                    <Link to={`/books/${item.book_id}`}>
                      <h3 className="font-semibold text-lg hover:text-blue-600">
                        {item.book?.title}
                      </h3>
                    </Link>
                    <p className="text-gray-600">{item.book?.author}</p>
                    <p className="text-green-600 font-semibold">
                      {formatPrice(item.unit_price || 0)}
                    </p>
                  </div>

                  <div className="flex items-center space-x-2">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleQuantityChange(item.id, item.quantity - 1)}
                    >
                      <Minus className="w-4 h-4" />
                    </Button>
                    <span className="w-8 text-center">{item.quantity}</span>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleQuantityChange(item.id, item.quantity + 1)}
                    >
                      <Plus className="w-4 h-4" />
                    </Button>
                  </div>

                  <div className="text-right">
                    <p className="font-semibold text-lg">
                      {formatPrice(item.subtotal || 0)}
                    </p>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => removeFromCart(item.id)}
                      className="mt-2 text-red-600 hover:text-red-700"
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Order Summary */}
        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle>Resumo do Pedido</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex justify-between">
                <span>Subtotal ({cart.total_items} itens)</span>
                <span>{formatPrice(cart.total_amount)}</span>
              </div>
              <div className="flex justify-between">
                <span>Frete</span>
                <span>Grátis</span>
              </div>
              <div className="border-t pt-4">
                <div className="flex justify-between text-lg font-semibold">
                  <span>Total</span>
                  <span>{formatPrice(cart.total_amount)}</span>
                </div>
              </div>
              
                    <div className="space-y-2">
                      <Button asChild className="w-full mt-6">
                        <Link to="/checkout">Finalizar Compra</Link>
                      </Button>

                      {/* Direct link to shipping calculator using cart items */}
                      <Button
                        variant="outline"
                        className="w-full"
                        onClick={() => {
                          const itemsForQuote = cart.items.map((it) => ({
                            weight_kg: it.book?.weight_kg || 0.5,
                            length_cm: it.book?.length_cm || 20,
                            width_cm: it.book?.width_cm || 15,
                            height_cm: it.book?.height_cm || 5,
                            quantity: it.quantity,
                          }))
                          navigate('/shipping', { state: { items: itemsForQuote, declared_value: cart.total_amount } })
                        }}
                      >
                        Calcular frete
                      </Button>

                      <Button variant="outline" asChild className="w-full">
                        <Link to="/">Continuar Comprando</Link>
                      </Button>
                    </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Recommended Books Section */}
      {cart && cart.items.length > 0 && (
        <div className="mt-12">
          <h2 className="text-2xl font-bold mb-6">Você Também Pode Gostar</h2>
          {loadingRecommendations ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {Array.from({ length: 4 }).map((_, i) => (
                <div key={i} className="animate-pulse">
                  <div className="bg-gray-200 h-64 rounded-lg mb-4"></div>
                  <div className="bg-gray-200 h-4 rounded mb-2"></div>
                  <div className="bg-gray-200 h-4 rounded w-3/4"></div>
                </div>
              ))}
            </div>
          ) : recommendations.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {recommendations.map((rec) => 
                rec.book ? (
                  <BookCard key={rec.book_id} book={rec.book} />
                ) : null
              )}
            </div>
          ) : (
            <p className="text-gray-600">Nenhuma recomendação disponível no momento</p>
          )}
        </div>
      )}
    </div>
  )
}