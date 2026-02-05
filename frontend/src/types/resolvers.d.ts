declare module '@hookform/resolvers' {
  export * from '@hookform/resolvers/dist/index.d.ts'
}

declare module '@hookform/resolvers/zod' {
  import { Resolver } from 'react-hook-form'
  import { z } from 'zod'
  
  export function zodResolver<T extends z.ZodSchema<any, any>>(
    schema: T,
    schemaOptions?: any,
    resolverOptions?: any
  ): Resolver<z.infer<T>>
}
