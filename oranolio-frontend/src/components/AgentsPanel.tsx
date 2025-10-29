'use client'

import { useState, useEffect } from 'react'
import { 
  Users, 
  Plus, 
  Trash2, 
  Play, 
  Square, 
  Eye,
  Terminal,
  FileText,
  MoreVertical,
  CheckCircle,
  XCircle,
  Clock
} from 'lucide-react'

interface Agent {
  id: string
  name: string
  computer: string
  username: string
  os: string
  arch: string
  elevated: boolean
  lastSeen: string
  status: 'online' | 'offline' | 'connecting'
  listener: string
  process: string
  ip: string
}

export default function AgentsPanel() {
  const [agents, setAgents] = useState<Agent[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null)

  useEffect(() => {
    // Simulate loading agents
    setTimeout(() => {
      setAgents([
        {
          id: 'agent-001',
          name: 'BEACON-001',
          computer: 'TARGET-DC-01',
          username: 'admin',
          os: 'Windows Server 2019',
          arch: 'x64',
          elevated: true,
          lastSeen: '2 minutes ago',
          status: 'online',
          listener: 'BeaconHTTP',
          process: 'explorer.exe',
          ip: '192.168.1.100'
        },
        {
          id: 'agent-002',
          name: 'GOPHER-002',
          computer: 'WORKSTATION-03',
          username: 'user',
          os: 'Windows 10',
          arch: 'x64',
          elevated: false,
          lastSeen: '5 minutes ago',
          status: 'online',
          listener: 'GopherTCP',
          process: 'notepad.exe',
          ip: '192.168.1.150'
        },
        {
          id: 'agent-003',
          name: 'BEACON-003',
          computer: 'SERVER-02',
          username: 'service',
          os: 'Windows Server 2016',
          arch: 'x86',
          elevated: true,
          lastSeen: '1 hour ago',
          status: 'offline',
          listener: 'BeaconSMB',
          process: 'svchost.exe',
          ip: '192.168.1.200'
        }
      ])
      setIsLoading(false)
    }, 1000)
  }, [])

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'online':
        return <CheckCircle className="h-4 w-4 text-green-400" />
      case 'offline':
        return <XCircle className="h-4 w-4 text-red-400" />
      case 'connecting':
        return <Clock className="h-4 w-4 text-yellow-400" />
      default:
        return <XCircle className="h-4 w-4 text-gray-400" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online':
        return 'bg-green-500'
      case 'offline':
        return 'bg-red-500'
      case 'connecting':
        return 'bg-yellow-500'
      default:
        return 'bg-gray-500'
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
            <Users className="h-6 w-6 mr-3 text-green-400" />
            Active Agents
          </h2>
          <p className="text-gray-400 mt-1">Manage and monitor your deployed agents</p>
        </div>
        <button className="flex items-center px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors glow-red">
          <Plus className="h-4 w-4 mr-2" />
          Deploy Agent
        </button>
      </div>

      {/* Agents Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {agents.map((agent) => (
          <div
            key={agent.id}
            className={`bg-gray-800 border border-gray-700 rounded-lg p-6 hover:border-gray-600 transition-colors cursor-pointer ${
              selectedAgent?.id === agent.id ? 'ring-2 ring-red-500' : ''
            }`}
            onClick={() => setSelectedAgent(agent)}
          >
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center">
                <div className={`w-3 h-3 rounded-full ${getStatusColor(agent.status)} mr-3`}></div>
                <div>
                  <h3 className="text-lg font-semibold text-white">{agent.name}</h3>
                  <p className="text-sm text-gray-400">{agent.computer}</p>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                {getStatusIcon(agent.status)}
                <button className="p-1 text-gray-400 hover:text-white">
                  <MoreVertical className="h-4 w-4" />
                </button>
              </div>
            </div>

            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-400">User:</span>
                <span className="text-white">{agent.username}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">OS:</span>
                <span className="text-white">{agent.os}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Arch:</span>
                <span className="text-white">{agent.arch}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Elevated:</span>
                <span className={agent.elevated ? 'text-green-400' : 'text-red-400'}>
                  {agent.elevated ? 'Yes' : 'No'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Listener:</span>
                <span className="text-white">{agent.listener}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Last Seen:</span>
                <span className="text-white">{agent.lastSeen}</span>
              </div>
            </div>

            <div className="mt-4 flex space-x-2">
              <button className="flex-1 flex items-center justify-center px-3 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded text-sm">
                <Terminal className="h-4 w-4 mr-2" />
                Console
              </button>
              <button className="flex-1 flex items-center justify-center px-3 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded text-sm">
                <FileText className="h-4 w-4 mr-2" />
                Files
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Empty State */}
      {agents.length === 0 && (
        <div className="text-center py-12">
          <Users className="h-16 w-16 text-gray-600 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-400 mb-2">No agents deployed</h3>
          <p className="text-gray-500">Deploy your first agent to get started</p>
        </div>
      )}
    </div>
  )
}