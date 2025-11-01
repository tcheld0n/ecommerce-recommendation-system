import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { CheckCircle2, Package, AlertCircle } from 'lucide-react'
import { useOrderService } from '@/services/orderService'
import { useToast } from '@/hooks/use-toast'

export function OrderConfirmation() {
  const { orderId } = useParams<{ orderId: string }>()
  const { getOrder } = useOrderService()
  const { toast } = useToast()
  const [order, setOrder] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    // Não incluir getOrder e toast como dependências para evitar re-renders infinitos
    if (!orderId) {
      setError('ID do pedido não fornecido')
      setLoading(false)
      return
    }

    const fetchOrder = async () => {
      try {
        setLoading(true)
        setError(null)

        console.log('Buscando pedido:', orderId)
        const orderData = await getOrder(orderId)
        console.log('Pedido recebido:', orderData)
        setOrder(orderData)
      } catch (error: any) {
        console.error('Erro ao carregar pedido:', error)
        const errorMsg = error.response?.data?.detail || error.message || 'Erro ao carregar pedido'
        setError(errorMsg)
        
        // Mostrar toast com o erro
        toast({
          title: "Erro",
          description: errorMsg,
          variant: "destructive",
        })
      } finally {
        setLoading(false)
      }
    }

    fetchOrder()
  }, [orderId]) // Apenas orderId como dependência

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(price)
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  if (loading) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-8">
        <div className="animate-pulse space-y-4">
          <div className="h-20 bg-gray-200 rounded"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    )
  }

  if (error || !order) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-8">
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <div className="flex items-start space-x-4">
              <AlertCircle className="w-8 h-8 text-red-600 flex-shrink-0 mt-1" />
              <div>
                <h2 className="text-lg font-semibold text-red-900 mb-2">
                  Erro ao carregar pedido
                </h2>
                <p className="text-red-700 mb-4">
                  {error || 'Pedido não encontrado'}
                </p>
                <div className="space-y-2">
                  <p className="text-sm text-red-600">
                    ID do pedido: <span className="font-mono">{orderId}</span>
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="mt-6 space-y-2">
          <Button asChild className="w-full">
            <a href="/orders">Ver Meus Pedidos</a>
          </Button>
          <Button variant="outline" asChild className="w-full">
            <a href="/">Voltar para Início</a>
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-2xl mx-auto px-4 py-8">
      {/* Success Message */}
      <div className="text-center mb-8">
        <div className="flex justify-center mb-4">
          <CheckCircle2 className="w-16 h-16 text-green-600" />
        </div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Pedido Confirmado!</h1>
        <p className="text-gray-600 text-lg">
          Obrigado pela sua compra. Seu pedido foi processado com sucesso.
        </p>
      </div>

      {/* Order Details Card */}
      <Card className="mb-6">
        <CardHeader className="bg-blue-50">
          <CardTitle className="text-xl">Detalhes do Pedido</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6 pt-6">
          {/* Order ID and Date */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-500 mb-1">Número do Pedido</p>
              <p className="text-lg font-semibold text-gray-900 font-mono">{order.id}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500 mb-1">Data</p>
              <p className="text-lg font-semibold text-gray-900">
                {formatDate(order.created_at)}
              </p>
            </div>
          </div>

          {/* Status */}
          <div>
            <p className="text-sm text-gray-500 mb-2">Status do Pedido</p>
            <div className="flex items-center space-x-2 bg-blue-50 px-4 py-2 rounded-lg w-fit">
              <Package className="w-5 h-5 text-blue-600" />
              <span className="font-semibold text-blue-600">
                {order.status === 'pending' ? 'Pendente' : 
                 order.status === 'paid' ? 'Pago' :
                 order.status === 'processing' ? 'Processando' :
                 order.status === 'shipped' ? 'Enviado' :
                 order.status === 'delivered' ? 'Entregue' : order.status}
              </span>
            </div>
          </div>

          {/* Shipping Address */}
          {order.shipping_address && (
            <div>
              <p className="text-sm text-gray-500 mb-2">Endereço de Entrega</p>
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="font-semibold text-gray-900">{order.shipping_address?.full_name}</p>
                <p className="text-gray-600">{order.shipping_address?.address}</p>
                <p className="text-gray-600">
                  {order.shipping_address?.city}, {order.shipping_address?.state} {order.shipping_address?.zip_code}
                </p>
                <p className="text-gray-600 mt-2">{order.shipping_address?.email}</p>
                <p className="text-gray-600">{order.shipping_address?.phone}</p>
              </div>
            </div>
          )}

          {/* Items Summary */}
          {order.items && order.items.length > 0 && (
            <div>
              <p className="text-sm text-gray-500 mb-2">Itens do Pedido</p>
              <div className="space-y-2">
                {order.items.map((item: any, idx: number) => (
                  <div key={idx} className="flex justify-between items-center py-2 border-b last:border-b-0">
                    <div>
                      <p className="font-semibold text-gray-900">
                        {item.book?.title || `Livro #${item.book_id}`}
                      </p>
                      <p className="text-sm text-gray-600">
                        Quantidade: {item.quantity} × {formatPrice(parseFloat(item.unit_price) || 0)}
                      </p>
                    </div>
                    <p className="font-semibold text-gray-900">
                      {formatPrice(item.quantity * parseFloat(item.unit_price))}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Total */}
          <div className="border-t pt-4">
            <div className="flex justify-between items-center text-lg font-semibold">
              <span className="text-gray-900">Total</span>
              <span className="text-green-600">{formatPrice(parseFloat(order.total_amount) || 0)}</span>
            </div>
          </div>

          {/* Payment Method */}
          {order.payment_method && (
            <div>
              <p className="text-sm text-gray-500 mb-2">Método de Pagamento</p>
              <p className="text-gray-900">
                {order.payment_method === 'credit_card' ? 'Cartão de Crédito' :
                 order.payment_method === 'debit_card' ? 'Cartão de Débito' :
                 order.payment_method === 'pix' ? 'PIX' : order.payment_method}
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* What's Next */}
      <Card className="mb-6 bg-blue-50 border-blue-200">
        <CardHeader>
          <CardTitle className="text-lg text-blue-900">O que Vem a Seguir?</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex space-x-3">
            <div className="flex-shrink-0">
              <div className="flex items-center justify-center h-8 w-8 rounded-md bg-blue-600 text-white text-sm font-semibold">1</div>
            </div>
            <div>
              <p className="font-semibold text-gray-900">Confirmação por Email</p>
              <p className="text-sm text-gray-600">Você receberá um email de confirmação em breve</p>
            </div>
          </div>

          <div className="flex space-x-3">
            <div className="flex-shrink-0">
              <div className="flex items-center justify-center h-8 w-8 rounded-md bg-blue-600 text-white text-sm font-semibold">2</div>
            </div>
            <div>
              <p className="font-semibold text-gray-900">Preparação do Pedido</p>
              <p className="text-sm text-gray-600">Sua compra será preparada e embalada com cuidado</p>
            </div>
          </div>

          <div className="flex space-x-3">
            <div className="flex-shrink-0">
              <div className="flex items-center justify-center h-8 w-8 rounded-md bg-blue-600 text-white text-sm font-semibold">3</div>
            </div>
            <div>
              <p className="font-semibold text-gray-900">Envio</p>
              <p className="text-sm text-gray-600">Será enviado para o endereço informado</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Action Buttons */}
      <div className="flex gap-4">
        <Button asChild className="flex-1">
          <a href="/orders">Ver Meus Pedidos</a>
        </Button>
        <Button variant="outline" asChild className="flex-1">
          <a href="/">Continuar Comprando</a>
        </Button>
      </div>

      {/* Support Message */}
      <div className="mt-8 p-4 bg-gray-50 rounded-lg text-center">
        <p className="text-sm text-gray-600">
          Tem dúvidas? Entre em contato com nosso suporte em{' '}
          <a href="mailto:support@bookstore.com" className="text-blue-600 hover:underline">
            support@bookstore.com
          </a>
        </p>
      </div>
    </div>
  )
}
