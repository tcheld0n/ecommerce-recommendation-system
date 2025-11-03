import { create } from 'zustand'
import { devtools } from 'zustand/middleware'
import { featuresService, type FeatureFlags, defaultFlags } from '@/services/featuresService'

type FeaturesState = {
  flags: FeatureFlags
  loaded: boolean
  loading: boolean
  saving: boolean
  load: () => Promise<void>
  save: (next?: Partial<FeatureFlags>) => Promise<void>
  setFlags: (partial: Partial<FeatureFlags>) => void
}

export const useFeaturesStore = create<FeaturesState>()(devtools((set, get) => ({
  flags: defaultFlags,
  loaded: false,
  loading: false,
  saving: false,
  load: async () => {
    if (get().loading) return
    set({ loading: true })
    try {
      const f = await featuresService.get()
      set({ flags: f, loaded: true })
    } finally {
      set({ loading: false })
    }
  },
  save: async (next) => {
    set({ saving: true })
    try {
      const toSave = { ...get().flags, ...(next || {}) }
      const saved = await featuresService.update(toSave)
      set({ flags: saved, loaded: true })
    } finally {
      set({ saving: false })
    }
  },
  setFlags: (partial) => set((state) => ({ flags: { ...state.flags, ...partial } })),
})))
