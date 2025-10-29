import React, { useEffect, useState } from 'react'
import { useOrderService } from '@/services/orderService'

const MyOrders: React.FC = () => {
  const { getUserOrders } = useOrderService()
  const [orders, setOrders] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    // NOTE: do not include `getUserOrders` in deps because useOrderService returns
    // new function instances on each render which would cause this effect to
    // re-run repeatedly. We intentionally run this effect only once on mount.
    let mounted = true
    const load = async () => {
      setIsLoading(true)
      setError(null)
      try {
        const data = await getUserOrders()
        if (mounted) setOrders(data)
      } catch (err: any) {
        if (mounted) setError(err?.response?.data?.detail || err.message || 'Erro ao carregar pedidos')
      } finally {
        if (mounted) setIsLoading(false)
      }
    }

    load()
    return () => { mounted = false }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-semibold mb-4">Meus pedidos</h1>

      {isLoading && <p>Carregando pedidos...</p>}

      {error && (
        <div className="p-4 bg-red-50 text-red-700 rounded mb-4">
          {error}
        </div>
      )}

      {!isLoading && !error && orders.length === 0 && (
        <div className="p-4 bg-yellow-50 text-yellow-800 rounded">Você ainda não tem pedidos.</div>
      )}

      <ul className="space-y-4 mt-4">
        {orders.map((order) => (
          <li key={order.id} className="border p-4 rounded shadow-sm">
            <div className="flex justify-between items-center">
              <div>
                <div className="text-sm text-gray-500">Pedido #{order.id}</div>
                <div className="text-lg font-medium">Status: {order.status}</div>
              </div>
              <div className="text-right">
                <div className="text-sm text-gray-500">Itens: {order.items_count ?? order.items?.length ?? 0}</div>
                <div className="text-lg font-semibold">R$ {Number(order.total_amount).toFixed(2)}</div>
                <div className="text-sm text-gray-400">{new Date(order.created_at).toLocaleString()}</div>
              </div>
            </div>

            {order.items && order.items.length > 0 && (
              <div className="mt-3 border-t pt-3">
                <h4 className="text-sm font-medium mb-2">Itens</h4>
                <ul className="space-y-2">
                  {order.items.map((it: any) => (
                    <li key={it.id} className="flex justify-between text-sm">
                      <div>{it.book?.title ?? it.book_id}</div>
                      <div>{it.quantity} x R$ {Number(it.unit_price).toFixed(2)}</div>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </li>
        ))}
      </ul>
    </div>
  )
}

export default MyOrders
