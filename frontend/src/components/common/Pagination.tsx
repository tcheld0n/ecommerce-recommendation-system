import { Button } from '@/components/ui/button'
import { ChevronLeft, ChevronRight, MoreHorizontal } from 'lucide-react'
import { cn } from '@/lib/utils'

interface PaginationProps {
  currentPage: number
  totalPages?: number
  totalItems?: number
  itemsPerPage?: number
  hasNextPage?: boolean
  hasPrevPage?: boolean
  onPageChange: (page: number) => void
  className?: string
}

export function Pagination({
  currentPage,
  totalPages,
  totalItems,
  itemsPerPage = 20,
  hasNextPage,
  hasPrevPage,
  onPageChange,
  className
}: PaginationProps) {
  // Se totalItems é fornecido, calcula totalPages
  const calculatedTotalPages = totalItems && itemsPerPage 
    ? Math.ceil(totalItems / itemsPerPage)
    : undefined

  // Se não temos totalPages, calculamos baseado em hasNextPage
  // Assumimos que se há próxima página, há pelo menos mais uma página
  const effectiveTotalPages = calculatedTotalPages ?? totalPages ?? (hasNextPage ? currentPage + 1 : currentPage)

  // Determina se há página anterior (não é a primeira página)
  const hasPreviousPage = hasPrevPage ?? (currentPage > 1)

  // Determina se há próxima página
  const hasNext = hasNextPage ?? (currentPage < effectiveTotalPages)

  // Gera números de página para mostrar
  const getPageNumbers = () => {
    const pages: (number | 'ellipsis')[] = []
    const delta = 3  // Páginas ao redor da página atual

    // Sempre mostra as primeiras e últimas páginas
    for (let i = 1; i <= effectiveTotalPages; i++) {
      if (
        i === 1 ||
        i === effectiveTotalPages ||
        (i >= currentPage - delta && i <= currentPage + delta)
      ) {
        pages.push(i)
      } else if (
        pages[pages.length - 1] !== 'ellipsis' &&
        i < currentPage - delta
      ) {
        pages.push('ellipsis')
      }
    }

    return pages
  }

  const pageNumbers = getPageNumbers()

  if (effectiveTotalPages <= 1) {
    return null
  }

  return (
    <div className={cn("flex items-center justify-center gap-2", className)}>
      {/* Botão Anterior */}
      <Button
        variant="outline"
        size="sm"
        onClick={() => onPageChange(currentPage - 1)}
        disabled={!hasPreviousPage}
        className="gap-1"
      >
        <ChevronLeft className="h-4 w-4" />
        <span className="hidden sm:inline">Anterior</span>
      </Button>

      {/* Números de Página */}
      <div className="flex items-center gap-1">
        {pageNumbers.map((page, index) => {
          if (page === 'ellipsis') {
            return (
              <div
                key={`ellipsis-${index}`}
                className="flex h-9 w-9 items-center justify-center"
              >
                <MoreHorizontal className="h-4 w-4 text-muted-foreground" />
              </div>
            )
          }

          return (
            <Button
              key={page}
              variant={currentPage === page ? 'default' : 'outline'}
              size="sm"
              onClick={() => onPageChange(page)}
              className="h-9 w-9 p-0"
            >
              {page}
            </Button>
          )
        })}
      </div>

      {/* Botão Próximo */}
      <Button
        variant="outline"
        size="sm"
        onClick={() => onPageChange(currentPage + 1)}
        disabled={!hasNext}
        className="gap-1"
      >
        <span className="hidden sm:inline">Próximo</span>
        <ChevronRight className="h-4 w-4" />
      </Button>
    </div>
  )
}

