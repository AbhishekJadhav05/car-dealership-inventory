import { useCallback, useEffect, useState } from 'react'
import { Plus, Search, X } from 'lucide-react'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { useAuth } from '@/features/auth/AuthContext'
import { api, ApiError } from '@/lib/api'
import { CATEGORIES, type Category, type Vehicle } from '@/types'
import VehicleCard from './VehicleCard'
import VehicleFormDialog from './VehicleFormDialog'

const ALL = 'all'

export default function VehiclesPage() {
  const { token, user } = useAuth()
  const isAdmin = user?.role === 'admin'

  const [vehicles, setVehicles] = useState<Vehicle[]>([])
  const [loading, setLoading] = useState(true)

  // Search state
  const [make, setMake] = useState('')
  const [model, setModel] = useState('')
  const [category, setCategory] = useState<Category | typeof ALL>(ALL)
  const [minPrice, setMinPrice] = useState('')
  const [maxPrice, setMaxPrice] = useState('')

  // Dialog state
  const [formOpen, setFormOpen] = useState(false)
  const [editingVehicle, setEditingVehicle] = useState<Vehicle | null>(null)

  const hasFilters = make || model || category !== ALL || minPrice || maxPrice

  const fetchVehicles = useCallback(async () => {
    if (!token) return
    setLoading(true)
    try {
      let data: Vehicle[]
      if (hasFilters) {
        const params = new URLSearchParams()
        if (make) params.set('make', make)
        if (model) params.set('model', model)
        if (category !== ALL) params.set('category', category)
        if (minPrice) params.set('min_price', minPrice)
        if (maxPrice) params.set('max_price', maxPrice)
        data = await api.get<Vehicle[]>(`/api/vehicles/search?${params.toString()}`, token)
      } else {
        data = await api.get<Vehicle[]>('/api/vehicles', token)
      }
      setVehicles(data)
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : 'Failed to load vehicles')
    } finally {
      setLoading(false)
    }
  }, [token, make, model, category, minPrice, maxPrice, hasFilters])

  useEffect(() => {
    fetchVehicles()
  }, [fetchVehicles])

  function clearFilters() {
    setMake('')
    setModel('')
    setCategory(ALL)
    setMinPrice('')
    setMaxPrice('')
  }

  function openCreate() {
    setEditingVehicle(null)
    setFormOpen(true)
  }

  function openEdit(vehicle: Vehicle) {
    setEditingVehicle(vehicle)
    setFormOpen(true)
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Page heading + add button */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-xl font-semibold">Inventory</h1>
          <p className="text-sm text-muted-foreground mt-0.5">
            {loading ? 'Loading…' : `${vehicles.length} vehicle${vehicles.length !== 1 ? 's' : ''}`}
          </p>
        </div>
        {isAdmin && (
          <Button onClick={openCreate} size="sm">
            <Plus className="size-3.5" />
            Add vehicle
          </Button>
        )}
      </div>

      {/* Search / filter bar */}
      <div className="flex flex-wrap gap-2 mb-6">
        <div className="relative flex-1 min-w-36">
          <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 size-3.5 text-muted-foreground pointer-events-none" />
          <Input
            placeholder="Make"
            value={make}
            onChange={(e) => setMake(e.target.value)}
            className="pl-8"
          />
        </div>
        <Input
          placeholder="Model"
          value={model}
          onChange={(e) => setModel(e.target.value)}
          className="flex-1 min-w-36"
        />
        <Select
          value={category}
          onValueChange={(v) => setCategory(v as Category | typeof ALL)}
        >
          <SelectTrigger className="w-36">
            <SelectValue placeholder="Category" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value={ALL}>All categories</SelectItem>
            {CATEGORIES.map((c) => (
              <SelectItem key={c} value={c}>
                {c.charAt(0).toUpperCase() + c.slice(1)}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Input
          type="number"
          placeholder="Min $"
          value={minPrice}
          onChange={(e) => setMinPrice(e.target.value)}
          className="w-24"
          min="0"
        />
        <Input
          type="number"
          placeholder="Max $"
          value={maxPrice}
          onChange={(e) => setMaxPrice(e.target.value)}
          className="w-24"
          min="0"
        />
        {hasFilters && (
          <Button variant="ghost" size="icon" onClick={clearFilters} aria-label="Clear filters">
            <X className="size-4" />
          </Button>
        )}
      </div>

      {/* Vehicle grid */}
      {loading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className="h-48 rounded-xl bg-muted animate-pulse" />
          ))}
        </div>
      ) : vehicles.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-24 text-center">
          <p className="text-muted-foreground text-sm">
            {hasFilters ? 'No vehicles match your search.' : 'No vehicles in inventory yet.'}
          </p>
          {hasFilters && (
            <Button variant="link" size="sm" onClick={clearFilters} className="mt-2">
              Clear filters
            </Button>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {vehicles.map((v) => (
            <VehicleCard
              key={v.id}
              vehicle={v}
              token={token!}
              isAdmin={isAdmin}
              onEdit={openEdit}
              onRefresh={fetchVehicles}
            />
          ))}
        </div>
      )}

      {/* Create / Edit dialog */}
      <VehicleFormDialog
        token={token!}
        vehicle={editingVehicle}
        open={formOpen}
        onOpenChange={setFormOpen}
        onSaved={fetchVehicles}
      />
    </div>
  )
}
