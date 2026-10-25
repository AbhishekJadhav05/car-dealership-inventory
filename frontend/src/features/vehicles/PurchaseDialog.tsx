import { useState } from 'react'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from '@/components/ui/dialog'
import { api, ApiError } from '@/lib/api'
import type { Vehicle } from '@/types'

interface Props {
  token: string
  vehicle: Vehicle
  open: boolean
  onOpenChange: (open: boolean) => void
  onDone: () => void
}

export default function PurchaseDialog({ token, vehicle, open, onOpenChange, onDone }: Props) {
  const [qty, setQty] = useState('1')
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setSubmitting(true)
    try {
      await api.post<Vehicle>(`/api/vehicles/${vehicle.id}/purchase`, { quantity: parseInt(qty, 10) }, token)
      toast.success(`Purchased ${qty} × ${vehicle.make} ${vehicle.model}`)
      onDone()
      onOpenChange(false)
      setQty('1')
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : 'Purchase failed')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-sm">
        <DialogHeader>
          <DialogTitle>Purchase vehicle</DialogTitle>
          <DialogDescription>
            {vehicle.make} {vehicle.model} — {vehicle.quantity} in stock
          </DialogDescription>
        </DialogHeader>
        <form id="purchase-form" onSubmit={handleSubmit} className="py-2">
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="purchase-qty">Quantity</Label>
            <Input
              id="purchase-qty"
              type="number"
              min="1"
              max={vehicle.quantity}
              step="1"
              required
              value={qty}
              onChange={(e) => setQty(e.target.value)}
            />
          </div>
        </form>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)} disabled={submitting}>
            Cancel
          </Button>
          <Button type="submit" form="purchase-form" disabled={submitting || vehicle.quantity === 0}>
            {submitting ? 'Purchasing…' : 'Confirm purchase'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
