'use client'

import { useState, useEffect } from 'react'
import { 
  Shield, 
  Zap, 
  Eye, 
  Lock, 
  Terminal, 
  Users, 
  Activity,
  AlertTriangle,
  CheckCircle,
  XCircle
} from 'lucide-react'
import Dashboard from '@/components/Dashboard'
import Login from '@/components/Login'
import { useAuth } from '@/hooks/useAuth'

export default function Home() {
  const { isAuthenticated, isLoading } = useAuth()

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-red-500 mx-auto"></div>
          <p className="mt-4 text-xl text-gray-300">Initializing Oranolio...</p>
        </div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Login />
  }

  return <Dashboard />
}