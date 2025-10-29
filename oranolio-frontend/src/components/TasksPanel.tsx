'use client'

import { useState, useEffect } from 'react'
import { 
  Activity, 
  Plus, 
  Play, 
  Square, 
  CheckCircle,
  XCircle,
  Clock,
  Terminal,
  FileText,
  Eye,
  Trash2
} from 'lucide-react'

interface Task {
  id: string
  agentId: string
  agentName: string
  command: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  startTime: string
  endTime?: string
  output?: string
  type: 'command' | 'file' | 'download' | 'upload'
}

export default function TasksPanel() {
  const [tasks, setTasks] = useState<Task[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [selectedTask, setSelectedTask] = useState<Task | null>(null)

  useEffect(() => {
    // Simulate loading tasks
    setTimeout(() => {
      setTasks([
        {
          id: 'task-001',
          agentId: 'agent-001',
          agentName: 'BEACON-001',
          command: 'whoami',
          status: 'completed',
          startTime: '2024-01-15 10:30:00',
          endTime: '2024-01-15 10:30:02',
          output: 'TARGET-DC-01\\admin',
          type: 'command'
        },
        {
          id: 'task-002',
          agentId: 'agent-001',
          agentName: 'BEACON-001',
          command: 'ls C:\\Users',
          status: 'running',
          startTime: '2024-01-15 10:35:00',
          type: 'command'
        },
        {
          id: 'task-003',
          agentId: 'agent-002',
          agentName: 'GOPHER-002',
          command: 'download C:\\Documents\\secret.txt',
          status: 'pending',
          startTime: '2024-01-15 10:40:00',
          type: 'download'
        },
        {
          id: 'task-004',
          agentId: 'agent-001',
          agentName: 'BEACON-001',
          command: 'screenshot',
          status: 'failed',
          startTime: '2024-01-15 10:25:00',
          endTime: '2024-01-15 10:25:05',
          output: 'Error: Unable to capture screenshot',
          type: 'command'
        }
      ])
      setIsLoading(false)
    }, 1000)
  }, [])

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-400" />
      case 'failed':
        return <XCircle className="h-4 w-4 text-red-400" />
      case 'running':
        return <Clock className="h-4 w-4 text-yellow-400 animate-spin" />
      case 'pending':
        return <Clock className="h-4 w-4 text-blue-400" />
      default:
        return <Clock className="h-4 w-4 text-gray-400" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-500'
      case 'failed':
        return 'bg-red-500'
      case 'running':
        return 'bg-yellow-500'
      case 'pending':
        return 'bg-blue-500'
      default:
        return 'bg-gray-500'
    }
  }

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'command':
        return <Terminal className="h-4 w-4 text-green-400" />
      case 'file':
        return <FileText className="h-4 w-4 text-blue-400" />
      case 'download':
        return <FileText className="h-4 w-4 text-yellow-400" />
      case 'upload':
        return <FileText className="h-4 w-4 text-purple-400" />
      default:
        return <Activity className="h-4 w-4 text-gray-400" />
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
            <Activity className="h-6 w-6 mr-3 text-yellow-400" />
            Task Queue
          </h2>
          <p className="text-gray-400 mt-1">Monitor and manage agent tasks</p>
        </div>
        <button className="flex items-center px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors glow-red">
          <Plus className="h-4 w-4 mr-2" />
          New Task
        </button>
      </div>

      {/* Tasks List */}
      <div className="bg-gray-800 border border-gray-700 rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-700">
            <thead className="bg-gray-700">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                  Task
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                  Agent
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                  Command
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                  Start Time
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-gray-800 divide-y divide-gray-700">
              {tasks.map((task) => (
                <tr key={task.id} className="hover:bg-gray-700">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      {getTypeIcon(task.type)}
                      <span className="ml-2 text-sm font-medium text-white">
                        {task.id}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-300">{task.agentName}</div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm text-gray-300 font-mono max-w-xs truncate">
                      {task.command}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className={`w-2 h-2 rounded-full ${getStatusColor(task.status)} mr-2`}></div>
                      <span className={`text-sm ${
                        task.status === 'completed' ? 'text-green-400' :
                        task.status === 'failed' ? 'text-red-400' :
                        task.status === 'running' ? 'text-yellow-400' :
                        'text-blue-400'
                      }`}>
                        {task.status}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                    {task.startTime}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div className="flex space-x-2">
                      <button 
                        onClick={() => setSelectedTask(task)}
                        className="text-blue-400 hover:text-blue-300"
                        title="View Output"
                      >
                        <Eye className="h-4 w-4" />
                      </button>
                      {task.status === 'running' && (
                        <button className="text-red-400 hover:text-red-300" title="Stop Task">
                          <Square className="h-4 w-4" />
                        </button>
                      )}
                      <button className="text-gray-400 hover:text-gray-300" title="Delete Task">
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Empty State */}
      {tasks.length === 0 && (
        <div className="text-center py-12">
          <Activity className="h-16 w-16 text-gray-600 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-400 mb-2">No tasks in queue</h3>
          <p className="text-gray-500">Create a new task to get started</p>
        </div>
      )}

      {/* Task Output Modal */}
      {selectedTask && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-gray-800 border border-gray-700 rounded-lg max-w-2xl w-full max-h-96">
            <div className="flex items-center justify-between p-4 border-b border-gray-700">
              <h3 className="text-lg font-semibold text-white">Task Output</h3>
              <button
                onClick={() => setSelectedTask(null)}
                className="text-gray-400 hover:text-white"
              >
                <XCircle className="h-5 w-5" />
              </button>
            </div>
            <div className="p-4">
              <div className="mb-4">
                <p className="text-sm text-gray-400">Command:</p>
                <p className="text-white font-mono text-sm bg-gray-900 p-2 rounded">
                  {selectedTask.command}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-400 mb-2">Output:</p>
                <div className="bg-black text-green-400 font-mono text-sm p-4 rounded h-48 overflow-y-auto">
                  {selectedTask.output || 'No output available'}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}