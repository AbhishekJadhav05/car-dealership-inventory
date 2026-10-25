import { useEffect, useState } from 'react'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { api, ApiError } from '@/lib/api'
import { CATEGORIES, type Vehicle } from '@/types'

interface Props {
  token: string
  vehicle?: Vehicle | null   // null = create mode
  open: boolean
  onOpenChange: (open: boolean) => void
  onSaved: () => void
}

export default function VehicleFormDialog({ token, vehicle, open, onOpenChange, onSaved }: Props) {
  const isEdit = !!vehicle

  const [make, setMake] = useState('')
  const [model, setModel] = useState('')
  const [category, setCategory] = useState('')
  const [price, setPrice] = useState('')
  const [quantity, setQuantity] = useState('')
  const [submitting, setSubmitting] = useState(false)

  // Populate form when editing
  useEffect(() => {
    if (vehicle) {
      setMake(vehicle.make)
      setModel(vehicle.model)
      setCategory(vehicle.category)
      setPrice(String(vehicle.price))
      setQuantity(String(vehicle.quantity))
    } else {
      setMake('')
      setModel('')
      setCategory('')
      setPrice('')
      setQuantity('')
    }
  }, [vehicle, open])

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setSubmitting(true)
    try {
      const body = {
        make,
        model,
        category,
        price: parseFloat(price),
        quantity: parseInt(quantity, 10),
      }
      if (isEdit) {
        await api.put<Vehicle>(`/api/vehicles/${vehicle!.id}`, body, token)
        toast.success('Vehicle updated')
      } else {
        await api.post<Vehicle>('/api/vehicles', body, token)
        toast.success('Vehicle created')
      }
      onSaved()
      onOpenChange(false)
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : 'Something went wrong')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>{isEdit ? 'Edit vehicle' : 'Add vehicle'}</DialogTitle>
        </DialogHeader>
        <form id="vehicle-form" onSubmit={handleSubmit} className="flex flex-col gap-4 py-2">
          <div className="grid grid-cols-2 gap-3">
            <div className="flex flex-col gap-1.5">
              <Label htmlFor="vf-make">Make</Label>
              <Input
                id="vf-make"
                required
                value={make}
                onChange={(e) => setMake(e.target.value)}
                placeholder="Toyota"
              />
            </div>
            <div className="flex flex-col gap-1.5">
              <Label htmlFor="vf-model">Model</Label>
              <Input
                id="vf-model"
                required
                value={model}
                onChange={(e) => setModel(e.target.value)}
                placeholder="Camry"
              />
            </div>
          </div>

          <div className="flex flex-col gap-1.5">
            <Label htmlFor="vf-category">Category</Label>
            <Select value={category} onValueChange={setCategory} required>
              <SelectTrigger id="vf-category">
                <SelectValue placeholder="Select category" />
              </SelectTrigger>
              <SelectContent>
                {CATEGORIES.map((c) => (
                  <SelectItem key={c} value={c}>
                    {c.charAt(0).toUpperCase() + c.slice(1)}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="flex flex-col gap-1.5">
              <Label htmlFor="vf-price">Price ($)</Label>
              <Input
                id="vf-price"
                type="number"
                min="0.01"
                step="0.01"
                required
                value={price}
                onChange={(e) => setPrice(e.target.value)}
                placeholder="25000.00"
              />
            </div>
            <div className="flex flex-col gap-1.5">
              <Label htmlFor="vf-qty">Quantity</Label>
              <Input
                id="vf-qty"
                type="number"
                min="0"
                step="1"
                required
                value={quantity}
                onChange={(e) => setQuantity(e.target.value)}
                placeholder="10"
              />
            </div>
          </div>
        </form>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)} disabled={submitting}>
            Cancel
          </Button>
          <Button type="submit" form="vehicle-form" disabled={submitting || !category}>
            {submitting ? 'Saving…' : isEdit ? 'Save changes' : 'Add vehicle'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
