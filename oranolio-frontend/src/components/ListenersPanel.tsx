'use client'

import { useState, useEffect } from 'react'
import { 
  Eye, 
  Plus, 
  Play, 
  Square, 
  Settings,
  Trash2,
  CheckCircle,
  XCircle,
  Clock,
  Globe,
  Shield
} from 'lucide-react'

interface Listener {
  id: string
  name: string
  type: string
  protocol: string
  host: string
  port: number
  status: 'running' | 'stopped' | 'starting'
  watermark: string
  agents: number
  config: any
}

export default function ListenersPanel() {
  const [listeners, setListeners] = useState<Listener[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [showCreateModal, setShowCreateModal] = useState(false)

  useEffect(() => {
    // Simulate loading listeners
    setTimeout(() => {
      setListeners([
        {
          id: 'listener-001',
          name: 'BeaconHTTP-01',
          type: 'BeaconHTTP',
          protocol: 'HTTP',
          host: '0.0.0.0',
          port: 8080,
          status: 'running',
          watermark: 'be4c0149',
          agents: 2,
          config: {
            url: '/api/beacon',
            userAgent: 'Mozilla/5.0',
            headers: {}
          }
        },
        {
          id: 'listener-002',
          name: 'BeaconTCP-01',
          type: 'BeaconTCP',
          protocol: 'TCP',
          host: '0.0.0.0',
          port: 4444,
          status: 'running',
          watermark: 'be4c0149',
          agents: 1,
          config: {
            timeout: 30,
            retries: 3
          }
        },
        {
          id: 'listener-003',
          name: 'GopherTCP-01',
          type: 'GopherTCP',
          protocol: 'TCP',
          host: '0.0.0.0',
          port: 9999,
          status: 'stopped',
          watermark: 'g0ph3r',
          agents: 0,
          config: {
            timeout: 60,
            retries: 5
          }
        }
      ])
      setIsLoading(false)
    }, 1000)
  }, [])

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running':
        return <CheckCircle className="h-4 w-4 text-green-400" />
      case 'stopped':
        return <XCircle className="h-4 w-4 text-red-400" />
      case 'starting':
        return <Clock className="h-4 w-4 text-yellow-400" />
      default:
        return <XCircle className="h-4 w-4 text-gray-400" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running':
        return 'bg-green-500'
      case 'stopped':
        return 'bg-red-500'
      case 'starting':
        return 'bg-yellow-500'
      default:
        return 'bg-gray-500'
    }
  }

  const getProtocolIcon = (protocol: string) => {
    switch (protocol) {
      case 'HTTP':
        return <Globe className="h-4 w-4 text-blue-400" />
      case 'TCP':
        return <Shield className="h-4 w-4 text-green-400" />
      case 'SMB':
        return <Shield className="h-4 w-4 text-purple-400" />
      default:
        return <Shield className="h-4 w-4 text-gray-400" />
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-500"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center">
            <Eye className="h-6 w-6 mr-3 text-blue-400" />
            Listeners
          </h2>
          <p className="text-gray-400 mt-1">Configure and manage your listener endpoints</p>
        </div>
        <button 
          onClick={() => setShowCreateModal(true)}
          className="flex items-center px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors glow-red"
        >
          <Plus className="h-4 w-4 mr-2" />
          Create Listener
        </button>
      </div>

      {/* Listeners Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {listeners.map((listener) => (
          <div
            key={listener.id}
            className="bg-gray-800 border border-gray-700 rounded-lg p-6 hover:border-gray-600 transition-colors"
          >
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center">
                <div className={`w-3 h-3 rounded-full ${getStatusColor(listener.status)} mr-3`}></div>
                <div>
                  <h3 className="text-lg font-semibold text-white">{listener.name}</h3>
                  <p className="text-sm text-gray-400">{listener.type}</p>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                {getStatusIcon(listener.status)}
                <button className="p-1 text-gray-400 hover:text-white">
                  <Settings className="h-4 w-4" />
                </button>
              </div>
            </div>

            <div className="space-y-2 text-sm mb-4">
              <div className="flex items-center justify-between">
                <span className="text-gray-400 flex items-center">
                  {getProtocolIcon(listener.protocol)}
                  <span className="ml-2">Protocol:</span>
                </span>
                <span className="text-white">{listener.protocol}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Host:</span>
                <span className="text-white">{listener.host}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Port:</span>
                <span className="text-white">{listener.port}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Watermark:</span>
                <span className="text-white font-mono text-xs">{listener.watermark}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Agents:</span>
                <span className="text-white">{listener.agents}</span>
              </div>
            </div>

            <div className="flex space-x-2">
              {listener.status === 'running' ? (
                <button className="flex-1 flex items-center justify-center px-3 py-2 bg-red-600 hover:bg-red-700 text-white rounded text-sm">
                  <Square className="h-4 w-4 mr-2" />
                  Stop
                </button>
              ) : (
                <button className="flex-1 flex items-center justify-center px-3 py-2 bg-green-600 hover:bg-green-700 text-white rounded text-sm">
                  <Play className="h-4 w-4 mr-2" />
                  Start
                </button>
              )}
              <button className="px-3 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded text-sm">
                <Settings className="h-4 w-4" />
              </button>
              <button className="px-3 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded text-sm">
                <Trash2 className="h-4 w-4" />
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Empty State */}
      {listeners.length === 0 && (
        <div className="text-center py-12">
          <Eye className="h-16 w-16 text-gray-600 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-400 mb-2">No listeners configured</h3>
          <p className="text-gray-500">Create your first listener to start accepting connections</p>
        </div>
      )}
    </div>
  )
}