import { useNavigate } from 'react-router-dom'
import { LogOut, Car } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { useAuth } from '@/features/auth/AuthContext'

export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  function handleLogout() {
    logout()
    navigate('/login', { replace: true })
  }

  return (
    <header className="border-b bg-card">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-14 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Car className="size-5" />
          <span className="font-semibold text-sm">Dealership Inventory</span>
        </div>

        {user && (
          <div className="flex items-center gap-3">
            <span className="text-sm text-muted-foreground hidden sm:block">
              {user.email}
            </span>
            {user.role === 'admin' && (
              <Badge variant="secondary" className="text-xs">
                Admin
              </Badge>
            )}
            <Button
              variant="ghost"
              size="icon-sm"
              onClick={handleLogout}
              aria-label="Sign out"
            >
              <LogOut className="size-4" />
            </Button>
          </div>
        )}
      </div>
    </header>
  )
}
