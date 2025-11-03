import { useEffect, useState } from 'react'
import { featuresService, type FeatureFlags, defaultFlags } from '@/services/featuresService'
import { useFeaturesStore } from '@/stores/features'

const allToggles: Array<{ key: keyof FeatureFlags; label: string; group: string }> = [
  { key: 'recommendation', label: 'Recomendações', group: 'Serviços' },
  { key: 'personalizedRecommendations', label: 'Recomendações Personalizadas', group: 'Experiências' },
  { key: 'similarInCart', label: 'Similares no Carrinho', group: 'Experiências' },
  { key: 'shipping', label: 'Envio/Entrega', group: 'Serviços' },
  { key: 'payment', label: 'Pagamento', group: 'Serviços' },
  { key: 'orders', label: 'Pedidos', group: 'Serviços' },
  { key: 'cart', label: 'Carrinho', group: 'Serviços' },
  { key: 'users', label: 'Usuários', group: 'Serviços' },
  { key: 'catalog', label: 'Catálogo', group: 'Serviços' },
]

export default function Config() {
  const { flags: storeFlags, load, save: saveStore, setFlags: updateStoreFlags, loading: storeLoading, saving: storeSaving } = useFeaturesStore()
  const [flags, setFlags] = useState<FeatureFlags>(storeFlags || defaultFlags)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [savedAt, setSavedAt] = useState<Date | null>(null)

  useEffect(() => {
    let mounted = true
    ;(async () => {
      try {
        await load()
        if (mounted) setFlags(useFeaturesStore.getState().flags)
      } finally {
        if (mounted) setLoading(false)
      }
    })()
    return () => {
      mounted = false
    }
  }, [])

  const grouped = allToggles.reduce<Record<string, typeof allToggles>>((acc, t) => {
    acc[t.group] = acc[t.group] || []
    acc[t.group].push(t)
    return acc
  }, {})

  const toggle = (key: keyof FeatureFlags) => {
    setFlags((prev) => ({ ...prev, [key]: !prev[key] }))
  }

  const save = async () => {
    setSaving(true)
    try {
      await saveStore(flags)
      setFlags(useFeaturesStore.getState().flags)
      setSavedAt(new Date())
    } finally {
      setSaving(false)
    }
  }

  if (loading || storeLoading) return <div>Carregando configuração...</div>

  return (
    <div className="max-w-3xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">Configuração do Produto (Feature Selector)</h1>
      <p className="text-muted-foreground mb-8">
        Selecione as features que devem compor o seu produto. Ao salvar, o gateway aplicará as
        restrições e a UI se adaptará às escolhas.
      </p>

      <div className="space-y-8">
        {Object.entries(grouped).map(([group, items]) => (
          <div key={group} className="border rounded-lg p-4">
            <h2 className="text-xl font-semibold mb-4">{group}</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {items.map(({ key, label }) => (
                <label key={key as string} className="flex items-center gap-3">
                  <input
                    type="checkbox"
                    checked={flags[key]}
                    onChange={() => toggle(key)}
                    className="h-4 w-4"
                  />
                  <span>{label}</span>
                </label>
              ))}
            </div>
          </div>
        ))}
      </div>

      <div className="mt-8 flex items-center gap-4">
        <button
          onClick={save}
          disabled={saving}
          className="px-4 py-2 rounded bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-70"
        >
          {saving || storeSaving ? 'Salvando...' : 'Salvar Configuração'}
        </button>
        {savedAt && (
          <span className="text-sm text-muted-foreground">Salvo em {savedAt.toLocaleTimeString()}</span>
        )}
      </div>

      <div className="mt-10 border rounded-lg p-4 bg-muted">
        <h3 className="font-semibold mb-2">Produto Construído</h3>
        <pre className="text-sm overflow-auto">{JSON.stringify(flags, null, 2)}</pre>
      </div>
    </div>
  )
}
