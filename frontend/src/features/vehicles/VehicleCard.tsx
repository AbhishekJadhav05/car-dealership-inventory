import { useState } from 'react'
import { Pencil, Trash2, ShoppingCart, Package } from 'lucide-react'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from '@/components/ui/card'
import { api, ApiError } from '@/lib/api'
import type { Vehicle } from '@/types'
import PurchaseDialog from './PurchaseDialog'
import RestockDialog from './RestockDialog'

interface Props {
  vehicle: Vehicle
  token: string
  isAdmin: boolean
  onEdit: (vehicle: Vehicle) => void
  onRefresh: () => void
}

export default function VehicleCard({ vehicle, token, isAdmin, onEdit, onRefresh }: Props) {
  const [purchaseOpen, setPurchaseOpen] = useState(false)
  const [restockOpen, setRestockOpen] = useState(false)
  const [deleting, setDeleting] = useState(false)

  async function handleDelete() {
    if (!confirm(`Delete ${vehicle.make} ${vehicle.model}?`)) return
    setDeleting(true)
    try {
      await api.delete<void>(`/api/vehicles/${vehicle.id}`, token)
      toast.success('Vehicle deleted')
      onRefresh()
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : 'Delete failed')
    } finally {
      setDeleting(false)
    }
  }

  const outOfStock = vehicle.quantity === 0

  return (
    <>
      <Card className="flex flex-col">
        <CardHeader>
          <div className="flex items-start justify-between gap-2">
            <CardTitle className="text-base">
              {vehicle.make} {vehicle.model}
            </CardTitle>
            <Badge variant="secondary" className="text-xs capitalize shrink-0">
              {vehicle.category}
            </Badge>
          </div>
        </CardHeader>

        <CardContent className="flex-1">
          <div className="flex items-center justify-between">
            <p className="text-2xl font-semibold">
              ${vehicle.price.toLocaleString('en-US', { minimumFractionDigits: 2 })}
            </p>
            <p className={`text-sm font-medium ${outOfStock ? 'text-destructive' : 'text-muted-foreground'}`}>
              {outOfStock ? 'Out of stock' : `${vehicle.quantity} in stock`}
            </p>
          </div>
        </CardContent>

        <CardFooter className="flex gap-2 flex-wrap">
          {/* Customer action */}
          <Button
            size="sm"
            className="flex-1"
            disabled={outOfStock}
            onClick={() => setPurchaseOpen(true)}
          >
            <ShoppingCart className="size-3.5" />
            {outOfStock ? 'Out of stock' : 'Purchase'}
          </Button>

          {/* Admin actions */}
          {isAdmin && (
            <>
              <Button size="icon-sm" variant="outline" onClick={() => setRestockOpen(true)} aria-label="Restock">
                <Package className="size-3.5" />
              </Button>
              <Button size="icon-sm" variant="outline" onClick={() => onEdit(vehicle)} aria-label="Edit">
                <Pencil className="size-3.5" />
              </Button>
              <Button
                size="icon-sm"
                variant="destructive"
                onClick={handleDelete}
                disabled={deleting}
                aria-label="Delete"
              >
                <Trash2 className="size-3.5" />
              </Button>
            </>
          )}
        </CardFooter>
      </Card>

      <PurchaseDialog
        token={token}
        vehicle={vehicle}
        open={purchaseOpen}
        onOpenChange={setPurchaseOpen}
        onDone={onRefresh}
      />

      {isAdmin && (
        <RestockDialog
          token={token}
          vehicle={vehicle}
          open={restockOpen}
          onOpenChange={setRestockOpen}
          onDone={onRefresh}
        />
      )}
    </>
  )
}
