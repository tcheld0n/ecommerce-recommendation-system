import { useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useCartStore } from '@/stores/cartStore'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Trash2, Plus, Minus, ShoppingBag } from 'lucide-react'

export function Cart() {
  const { cart, getCart, updateCartItem, removeFromCart, clearCart, isLoading } = useCartStore()

  useEffect(() => {
    getCart()
  }, [getCart])

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
                      src={item.book?.cover_image_url || '/placeholder-book.jpg'}
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
              
              <Button asChild className="w-full mt-6">
                <Link to="/checkout">Finalizar Compra</Link>
              </Button>
              
              <Button variant="outline" asChild className="w-full">
                <Link to="/">Continuar Comprando</Link>
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
