export type Role = 'customer' | 'admin'

export type Category =
  | 'sedan'
  | 'suv'
  | 'truck'
  | 'van'
  | 'coupe'
  | 'hatchback'
  | 'convertible'
  | 'pickup'

export const CATEGORIES: Category[] = [
  'sedan',
  'suv',
  'truck',
  'van',
  'coupe',
  'hatchback',
  'convertible',
  'pickup',
]

export interface User {
  id: number
  email: string
  role: Role
}

export interface Vehicle {
  id: number
  make: string
  model: string
  category: Category
  price: number
  quantity: number
}

export interface AuthToken {
  access_token: string
  token_type: string
}
