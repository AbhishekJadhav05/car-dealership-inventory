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

export default function RestockDialog({ token, vehicle, open, onOpenChange, onDone }: Props) {
  const [qty, setQty] = useState('10')
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setSubmitting(true)
    try {
      await api.post<Vehicle>(
        `/api/vehicles/${vehicle.id}/restock`,
        { quantity: parseInt(qty, 10) },
        token,
      )
      toast.success(`Restocked ${qty} units of ${vehicle.make} ${vehicle.model}`)
      onDone()
      onOpenChange(false)
      setQty('10')
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : 'Restock failed')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-sm">
        <DialogHeader>
          <DialogTitle>Restock vehicle</DialogTitle>
          <DialogDescription>
            {vehicle.make} {vehicle.model} — currently {vehicle.quantity} in stock
          </DialogDescription>
        </DialogHeader>
        <form id="restock-form" onSubmit={handleSubmit} className="py-2">
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="restock-qty">Units to add</Label>
            <Input
              id="restock-qty"
              type="number"
              min="1"
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
          <Button type="submit" form="restock-form" disabled={submitting}>
            {submitting ? 'Restocking…' : 'Confirm restock'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
