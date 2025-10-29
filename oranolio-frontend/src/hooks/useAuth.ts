'use client'

import { useState, useEffect } from 'react'

interface User {
  username: string
  token: string
}

export function useAuth() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [user, setUser] = useState<User | null>(null)

  useEffect(() => {
    const token = localStorage.getItem('oranolio_token')
    const username = localStorage.getItem('oranolio_username')
    
    if (token && username) {
      setUser({ username, token })
      setIsAuthenticated(true)
    }
    
    setIsLoading(false)
  }, [])

  const login = async (username: string, password: string) => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      })

      if (response.ok) {
        const data = await response.json()
        localStorage.setItem('oranolio_token', data.access_token)
        localStorage.setItem('oranolio_username', username)
        setUser({ username, token: data.access_token })
        setIsAuthenticated(true)
        return true
      }
      return false
    } catch (error) {
      console.error('Login error:', error)
      return false
    }
  }

  const logout = () => {
    localStorage.removeItem('oranolio_token')
    localStorage.removeItem('oranolio_username')
    setUser(null)
    setIsAuthenticated(false)
  }

  return {
    isAuthenticated,
    isLoading,
    user,
    login,
    logout
  }
}