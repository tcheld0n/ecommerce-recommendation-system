import { useState } from 'react'
import { shippingService, type QuoteResponse, type PackageItem } from '@/services/shippingService'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'

export function Shipping() {
  const [zip, setZip] = useState('01001-000')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [quote, setQuote] = useState<QuoteResponse | null>(null)

  const handleQuote = async () => {
    setLoading(true)
    setError(null)
    setQuote(null)
    try {
      const items: PackageItem[] = [
        { weight_kg: 0.5, length_cm: 20, width_cm: 15, height_cm: 5, quantity: 1 },
      ]
      const res = await shippingService.quote({ destination_zip: zip, items, declared_value: 150 })
      setQuote(res)
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Não foi possível calcular o frete agora.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <section>
      <h1 className="text-2xl font-bold mb-4">Envio e Frete</h1>
      <p className="text-gray-600 mb-6">Calcule o frete estimado informando seu CEP.</p>

      <div className="flex items-center gap-3 mb-4 max-w-md">
        <Input value={zip} onChange={(e) => setZip(e.target.value)} placeholder="Seu CEP" />
        <Button onClick={handleQuote} disabled={loading}>
          {loading ? 'Calculando...' : 'Calcular frete'}
        </Button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">{error}</div>
      )}

      {quote && (
        <div className="space-y-3">
          <h2 className="text-lg font-semibold">Opções de frete para {quote.destination_zip}</h2>
          <ul className="space-y-2">
            {quote.options.map((opt, idx) => (
              <li key={idx} className="border rounded p-3 flex items-center justify-between">
                <div>
                  <div className="font-medium">{opt.carrier} · {opt.service}</div>
                  <div className="text-sm text-gray-600">Entrega em ~{opt.estimated_days} dias</div>
                </div>
                <div className="font-semibold">{opt.currency} {opt.price.toFixed(2)}</div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </section>
  )
}

export default Shipping
