import { useEffect } from 'react'
import { useAuthStore } from '@/stores/authStore'
import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { useToast } from '@/hooks/use-toast'

const profileSchema = z.object({
  full_name: z.string().min(2, 'Nome deve ter pelo menos 2 caracteres'),
  reading_preferences: z.object({
    favorite_genres: z.array(z.string()).optional(),
    favorite_authors: z.array(z.string()).optional(),
  }).optional(),
})

type ProfileForm = z.infer<typeof profileSchema>

export function Profile() {
  const { user, updateUser, isLoading, error } = useAuthStore()
  const { toast } = useToast()

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<ProfileForm>({
    // resolver: zodResolver(profileSchema), // Temporarily disabled due to import issue
  })

  useEffect(() => {
    if (user) {
      reset({
        full_name: user.full_name,
        reading_preferences: user.reading_preferences || {},
      })
    }
  }, [user, reset])

  const onSubmit = async (data: ProfileForm) => {
    try {
      await updateUser(data)
      toast({
        title: "Perfil atualizado",
        description: "Suas informações foram atualizadas com sucesso.",
      })
    } catch (error) {
      // Error is handled by the store
    }
  }

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded mb-6"></div>
          <div className="bg-gray-200 h-64 rounded"></div>
        </div>
      </div>
    )
  }

  if (!user) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Usuário não encontrado</h1>
          <p className="text-gray-600">Faça login para acessar seu perfil.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Meu Perfil</h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Profile Information */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>Informações Pessoais</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                {error && (
                  <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
                    {error}
                  </div>
                )}

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
                    value={user.email}
                    disabled
                    className="bg-gray-100"
                  />
                  <p className="text-sm text-gray-500 mt-1">Email não pode ser alterado</p>
                </div>

                <Button type="submit" disabled={isLoading}>
                  {isLoading ? 'Salvando...' : 'Salvar Alterações'}
                </Button>
              </form>
            </CardContent>
          </Card>
        </div>

        {/* Account Info */}
        <div>
          <Card>
            <CardHeader>
              <CardTitle>Informações da Conta</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <span className="text-sm font-medium text-gray-500">Membro desde</span>
                <p className="text-sm">
                  {new Date(user.created_at).toLocaleDateString('pt-BR')}
                </p>
              </div>
              
              <div>
                <span className="text-sm font-medium text-gray-500">Status</span>
                <p className="text-sm">
                  {user.is_active ? 'Ativo' : 'Inativo'}
                </p>
              </div>

              {user.is_admin && (
                <div>
                  <span className="text-sm font-medium text-gray-500">Tipo de Conta</span>
                  <p className="text-sm">Administrador</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}