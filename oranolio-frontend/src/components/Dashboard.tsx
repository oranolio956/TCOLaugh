'use client'

import { useState } from 'react'
import { 
  Shield, 
  Zap, 
  Eye, 
  Lock, 
  Terminal, 
  Users, 
  Activity,
  Settings,
  LogOut,
  Menu,
  X
} from 'lucide-react'
import { useAuth } from '@/hooks/useAuth'
import AgentsPanel from './AgentsPanel'
import ListenersPanel from './ListenersPanel'
import TasksPanel from './TasksPanel'
import ConsolePanel from './ConsolePanel'
import FilesPanel from './FilesPanel'

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState('agents')
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const { user, logout } = useAuth()

  const tabs = [
    { id: 'agents', name: 'Agents', icon: Users, color: 'text-green-400' },
    { id: 'listeners', name: 'Listeners', icon: Eye, color: 'text-blue-400' },
    { id: 'tasks', name: 'Tasks', icon: Activity, color: 'text-yellow-400' },
    { id: 'console', name: 'Console', icon: Terminal, color: 'text-purple-400' },
    { id: 'files', name: 'Files', icon: Lock, color: 'text-red-400' },
  ]

  const renderContent = () => {
    switch (activeTab) {
      case 'agents':
        return <AgentsPanel />
      case 'listeners':
        return <ListenersPanel />
      case 'tasks':
        return <TasksPanel />
      case 'console':
        return <ConsolePanel />
      case 'files':
        return <FilesPanel />
      default:
        return <AgentsPanel />
    }
  }

  return (
    <div className="min-h-screen bg-gray-900">
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700">
        <div className="px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="lg:hidden p-2 rounded-md text-gray-400 hover:text-white hover:bg-gray-700"
              >
                {sidebarOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
              </button>
              <div className="flex items-center ml-4">
                <Shield className="h-8 w-8 text-red-500 mr-3" />
                <h1 className="text-xl font-bold text-white">ORANOLIO</h1>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="hidden sm:block">
                <span className="text-sm text-gray-400">Welcome,</span>
                <span className="text-sm font-medium text-white ml-1">{user?.username}</span>
              </div>
              <button
                onClick={logout}
                className="p-2 rounded-md text-gray-400 hover:text-white hover:bg-gray-700"
                title="Logout"
              >
                <LogOut className="h-5 w-5" />
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Sidebar */}
        <div className={`${sidebarOpen ? 'block' : 'hidden'} lg:block lg:w-64 bg-gray-800 border-r border-gray-700`}>
          <nav className="mt-5 px-2">
            <div className="space-y-1">
              {tabs.map((tab) => {
                const Icon = tab.icon
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`${
                      activeTab === tab.id
                        ? 'bg-gray-700 text-white'
                        : 'text-gray-300 hover:bg-gray-700 hover:text-white'
                    } group flex items-center px-2 py-2 text-sm font-medium rounded-md w-full text-left`}
                  >
                    <Icon className={`mr-3 h-5 w-5 ${tab.color}`} />
                    {tab.name}
                  </button>
                )
              })}
            </div>
          </nav>
        </div>

        {/* Main Content */}
        <div className="flex-1">
          <main className="p-6">
            {renderContent()}
          </main>
        </div>
      </div>
    </div>
  )
}