'use client'

import { useState, useEffect, useRef } from 'react'
import { 
  Terminal, 
  Send, 
  Clear, 
  Download,
  Play,
  Square,
  Settings
} from 'lucide-react'

export default function ConsolePanel() {
  const [input, setInput] = useState('')
  const [output, setOutput] = useState<string[]>([])
  const [isConnected, setIsConnected] = useState(false)
  const [selectedAgent, setSelectedAgent] = useState('BEACON-001')
  const terminalRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    // Simulate initial connection
    setTimeout(() => {
      setIsConnected(true)
      addOutput('Connected to Oranolio Console')
      addOutput('Type "help" for available commands')
      addOutput('')
    }, 1000)
  }, [])

  useEffect(() => {
    // Auto-scroll to bottom
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight
    }
  }, [output])

  const addOutput = (line: string) => {
    setOutput(prev => [...prev, line])
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim()) return

    // Add command to output
    addOutput(`$ ${input}`)

    // Simulate command execution
    setTimeout(() => {
      if (input.toLowerCase() === 'help') {
        addOutput('Available commands:')
        addOutput('  help          - Show this help message')
        addOutput('  whoami        - Display current user')
        addOutput('  pwd           - Print working directory')
        addOutput('  ls            - List directory contents')
        addOutput('  ps            - List running processes')
        addOutput('  exit          - Disconnect from console')
        addOutput('')
      } else if (input.toLowerCase() === 'whoami') {
        addOutput('TARGET-DC-01\\admin')
        addOutput('')
      } else if (input.toLowerCase() === 'pwd') {
        addOutput('C:\\Users\\admin')
        addOutput('')
      } else if (input.toLowerCase() === 'ls') {
        addOutput('Desktop')
        addOutput('Documents')
        addOutput('Downloads')
        addOutput('Pictures')
        addOutput('Videos')
        addOutput('')
      } else if (input.toLowerCase() === 'ps') {
        addOutput('PID    Name')
        addOutput('----    ----')
        addOutput('1234   explorer.exe')
        addOutput('5678   notepad.exe')
        addOutput('9012   chrome.exe')
        addOutput('')
      } else if (input.toLowerCase() === 'exit') {
        addOutput('Disconnecting...')
        setIsConnected(false)
        addOutput('')
      } else {
        addOutput(`Command not found: ${input}`)
        addOutput('Type "help" for available commands')
        addOutput('')
      }
    }, 500)

    setInput('')
  }

  const clearConsole = () => {
    setOutput([])
  }

  const downloadLog = () => {
    const logContent = output.join('\n')
    const blob = new Blob([logContent], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `oranolio-console-${new Date().toISOString().split('T')[0]}.log`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center">
            <Terminal className="h-6 w-6 mr-3 text-purple-400" />
            Console
          </h2>
          <p className="text-gray-400 mt-1">Interactive command execution</p>
        </div>
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-400">Agent:</span>
            <select
              value={selectedAgent}
              onChange={(e) => setSelectedAgent(e.target.value)}
              className="bg-gray-700 border border-gray-600 rounded px-3 py-1 text-white text-sm"
            >
              <option value="BEACON-001">BEACON-001</option>
              <option value="GOPHER-002">GOPHER-002</option>
              <option value="BEACON-003">BEACON-003</option>
            </select>
          </div>
          <div className="flex items-center space-x-2">
            <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
            <span className="text-sm text-gray-400">
              {isConnected ? 'Connected' : 'Disconnected'}
            </span>
          </div>
          <button
            onClick={clearConsole}
            className="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded"
            title="Clear Console"
          >
            <Clear className="h-4 w-4" />
          </button>
          <button
            onClick={downloadLog}
            className="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded"
            title="Download Log"
          >
            <Download className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Terminal */}
      <div className="bg-black border border-gray-700 rounded-lg overflow-hidden">
        <div className="bg-gray-800 px-4 py-2 border-b border-gray-700 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-red-500 rounded-full"></div>
            <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
          </div>
          <span className="text-sm text-gray-400">Oranolio Console - {selectedAgent}</span>
        </div>
        
        <div
          ref={terminalRef}
          className="h-96 overflow-y-auto p-4 font-mono text-sm text-green-400"
        >
          {output.map((line, index) => (
            <div key={index} className="mb-1">
              {line}
            </div>
          ))}
        </div>

        {/* Input */}
        <form onSubmit={handleSubmit} className="border-t border-gray-700 p-4">
          <div className="flex items-center space-x-2">
            <span className="text-green-400 font-mono">$</span>
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Enter command..."
              className="flex-1 bg-transparent text-green-400 font-mono text-sm outline-none"
              disabled={!isConnected}
            />
            <button
              type="submit"
              disabled={!isConnected || !input.trim()}
              className="p-2 text-gray-400 hover:text-white disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Send className="h-4 w-4" />
            </button>
          </div>
        </form>
      </div>

      {/* Quick Commands */}
      <div className="bg-gray-800 border border-gray-700 rounded-lg p-4">
        <h3 className="text-lg font-semibold text-white mb-3">Quick Commands</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
          {[
            { cmd: 'whoami', desc: 'Current user' },
            { cmd: 'pwd', desc: 'Working directory' },
            { cmd: 'ls', desc: 'List files' },
            { cmd: 'ps', desc: 'Running processes' },
            { cmd: 'netstat', desc: 'Network connections' },
            { cmd: 'systeminfo', desc: 'System information' },
            { cmd: 'ipconfig', desc: 'Network config' },
            { cmd: 'help', desc: 'Show help' }
          ].map(({ cmd, desc }) => (
            <button
              key={cmd}
              onClick={() => setInput(cmd)}
              className="p-2 text-left bg-gray-700 hover:bg-gray-600 rounded text-sm text-gray-300 hover:text-white transition-colors"
            >
              <div className="font-mono text-green-400">{cmd}</div>
              <div className="text-xs text-gray-500">{desc}</div>
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}