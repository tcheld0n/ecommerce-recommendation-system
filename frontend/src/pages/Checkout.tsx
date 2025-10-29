import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useCartStore } from '@/stores/cartStore'
import { useOrderService } from '@/services/orderService'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { useToast } from '@/hooks/use-toast'

const checkoutSchema = z.object({
  full_name: z.string().min(2, 'Nome completo é obrigatório'),
  email: z.string().email('Email inválido'),
  phone: z.string().min(10, 'Telefone é obrigatório'),
  address: z.string().min(10, 'Endereço é obrigatório'),
  city: z.string().min(2, 'Cidade é obrigatória'),
  state: z.string().min(2, 'Estado é obrigatório'),
  zip_code: z.string().min(8, 'CEP é obrigatório'),
  payment_method: z.enum(['credit_card', 'debit_card', 'pix']),
})

type CheckoutForm = z.infer<typeof checkoutSchema>

export function Checkout() {
  const navigate = useNavigate()
  const { cart, getCart } = useCartStore()
  const { createOrder } = useOrderService()
  const { toast } = useToast()
  const [isProcessing, setIsProcessing] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<CheckoutForm>({
    resolver: zodResolver(checkoutSchema),
  })

  const onSubmit = async (data: CheckoutForm) => {
    if (!cart || cart.items.length === 0) {
      toast({
        title: "Erro",
        description: "Seu carrinho está vazio",
        variant: "destructive",
      })
      return
    }

    setIsProcessing(true)
    try {
      const orderData = {
        shipping_address: {
          full_name: data.full_name,
          email: data.email,
          phone: data.phone,
          address: data.address,
          city: data.city,
          state: data.state,
          zip_code: data.zip_code,
        },
        payment_method: data.payment_method,
        items: cart.items.map(item => ({
          book_id: item.book_id,
          quantity: item.quantity,
          unit_price: item.unit_price || 0,
        }))
      }

      const order = await createOrder(orderData)
      
      toast({
        title: "Pedido realizado com sucesso!",
        description: `Seu pedido #${order.id} foi criado.`,
      })

      navigate(`/orders/${order.id}`)
    } catch (error: any) {
      toast({
        title: "Erro",
        description: error.response?.data?.detail || "Erro ao processar pedido",
        variant: "destructive",
      })
    } finally {
      setIsProcessing(false)
    }
  }

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(price)
  }

  if (!cart || cart.items.length === 0) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Carrinho vazio</h1>
          <p className="text-gray-600 mb-6">Adicione itens ao carrinho antes de finalizar a compra</p>
          <Button asChild>
            <a href="/">Continuar Comprando</a>
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Finalizar Compra</h1>

      <form onSubmit={handleSubmit(onSubmit)} className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Shipping Information */}
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Informações de Entrega</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Nome Completo</label>
                <Input
                  {...register('full_name')}
                  className={errors.full_name ? 'border-red-500' : ''}
                />
                {errors.full_name && (
                  <p className="text-red-500 text-sm mt-1">{errors.full_name.message}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Email</label>
                <Input
                  type="email"
                  {...register('email')}
                  className={errors.email ? 'border-red-500' : ''}
                />
                {errors.email && (
                  <p className="text-red-500 text-sm mt-1">{errors.email.message}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Telefone</label>
                <Input
                  {...register('phone')}
                  className={errors.phone ? 'border-red-500' : ''}
                />
                {errors.phone && (
                  <p className="text-red-500 text-sm mt-1">{errors.phone.message}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Endereço</label>
                <Input
                  {...register('address')}
                  className={errors.address ? 'border-red-500' : ''}
                />
                {errors.address && (
                  <p className="text-red-500 text-sm mt-1">{errors.address.message}</p>
                )}
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Cidade</label>
                  <Input
                    {...register('city')}
                    className={errors.city ? 'border-red-500' : ''}
                  />
                  {errors.city && (
                    <p className="text-red-500 text-sm mt-1">{errors.city.message}</p>
                  )}
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Estado</label>
                  <Input
                    {...register('state')}
                    className={errors.state ? 'border-red-500' : ''}
                  />
                  {errors.state && (
                    <p className="text-red-500 text-sm mt-1">{errors.state.message}</p>
                  )}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">CEP</label>
                <Input
                  {...register('zip_code')}
                  className={errors.zip_code ? 'border-red-500' : ''}
                />
                {errors.zip_code && (
                  <p className="text-red-500 text-sm mt-1">{errors.zip_code.message}</p>
                )}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Método de Pagamento</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <label className="flex items-center space-x-2">
                  <input
                    type="radio"
                    value="credit_card"
                    {...register('payment_method')}
                    className="text-blue-600"
                  />
                  <span>Cartão de Crédito</span>
                </label>
                <label className="flex items-center space-x-2">
                  <input
                    type="radio"
                    value="debit_card"
                    {...register('payment_method')}
                    className="text-blue-600"
                  />
                  <span>Cartão de Débito</span>
                </label>
                <label className="flex items-center space-x-2">
                  <input
                    type="radio"
                    value="pix"
                    {...register('payment_method')}
                    className="text-blue-600"
                  />
                  <span>PIX</span>
                </label>
              </div>
              {errors.payment_method && (
                <p className="text-red-500 text-sm">{errors.payment_method.message}</p>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Order Summary */}
        <div>
          <Card>
            <CardHeader>
              <CardTitle>Resumo do Pedido</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {cart.items.map((item) => (
                  <div key={item.id} className="flex items-center space-x-4">
                    <img
                      src={item.book?.cover_image_url || '/placeholder-book.svg'}
                      alt={item.book?.title}
                      className="w-16 h-20 object-cover rounded"
                    />
                    <div className="flex-1">
                      <h4 className="font-semibold">{item.book?.title}</h4>
                      <p className="text-sm text-gray-600">Qtd: {item.quantity}</p>
                    </div>
                    <div className="text-right">
                      <p className="font-semibold">{formatPrice(item.subtotal || 0)}</p>
                    </div>
                  </div>
                ))}

                <div className="border-t pt-4 space-y-2">
                  <div className="flex justify-between">
                    <span>Subtotal ({cart.total_items} itens)</span>
                    <span>{formatPrice(cart.total_amount)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Frete</span>
                    <span>Grátis</span>
                  </div>
                  <div className="flex justify-between text-lg font-semibold border-t pt-2">
                    <span>Total</span>
                    <span>{formatPrice(cart.total_amount)}</span>
                  </div>
                </div>

                <Button
                  type="submit"
                  className="w-full mt-6"
                  disabled={isProcessing}
                >
                  {isProcessing ? 'Processando...' : 'Finalizar Pedido'}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </form>
    </div>
  )
}
