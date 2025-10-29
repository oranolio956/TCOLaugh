'use client'

import { useState, useEffect } from 'react'
import { 
  Lock, 
  Upload, 
  Download, 
  Folder,
  File,
  Image,
  FileText,
  Archive,
  Trash2,
  Eye,
  MoreVertical,
  Search,
  Filter
} from 'lucide-react'

interface FileItem {
  id: string
  name: string
  type: 'file' | 'folder'
  size: number
  modified: string
  path: string
  agent: string
  extension: string
}

export default function FilesPanel() {
  const [files, setFiles] = useState<FileItem[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [currentPath, setCurrentPath] = useState('C:\\')
  const [selectedFiles, setSelectedFiles] = useState<string[]>([])
  const [searchTerm, setSearchTerm] = useState('')

  useEffect(() => {
    // Simulate loading files
    setTimeout(() => {
      setFiles([
        {
          id: 'file-001',
          name: 'Documents',
          type: 'folder',
          size: 0,
          modified: '2024-01-15 10:30:00',
          path: 'C:\\Documents',
          agent: 'BEACON-001',
          extension: ''
        },
        {
          id: 'file-002',
          name: 'secret.txt',
          type: 'file',
          size: 1024,
          modified: '2024-01-15 09:15:00',
          path: 'C:\\secret.txt',
          agent: 'BEACON-001',
          extension: 'txt'
        },
        {
          id: 'file-003',
          name: 'screenshot.png',
          type: 'file',
          size: 2048000,
          modified: '2024-01-15 08:45:00',
          path: 'C:\\screenshot.png',
          agent: 'BEACON-001',
          extension: 'png'
        },
        {
          id: 'file-004',
          name: 'config.json',
          type: 'file',
          size: 512,
          modified: '2024-01-15 07:20:00',
          path: 'C:\\config.json',
          agent: 'GOPHER-002',
          extension: 'json'
        },
        {
          id: 'file-005',
          name: 'backup.zip',
          type: 'file',
          size: 10485760,
          modified: '2024-01-14 16:30:00',
          path: 'C:\\backup.zip',
          agent: 'BEACON-003',
          extension: 'zip'
        }
      ])
      setIsLoading(false)
    }, 1000)
  }, [])

  const getFileIcon = (file: FileItem) => {
    if (file.type === 'folder') {
      return <Folder className="h-5 w-5 text-blue-400" />
    }

    switch (file.extension.toLowerCase()) {
      case 'png':
      case 'jpg':
      case 'jpeg':
      case 'gif':
        return <Image className="h-5 w-5 text-green-400" />
      case 'txt':
      case 'log':
        return <FileText className="h-5 w-5 text-gray-400" />
      case 'zip':
      case 'rar':
      case '7z':
        return <Archive className="h-5 w-5 text-yellow-400" />
      default:
        return <File className="h-5 w-5 text-gray-400" />
    }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const filteredFiles = files.filter(file =>
    file.name.toLowerCase().includes(searchTerm.toLowerCase())
  )

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
            <Lock className="h-6 w-6 mr-3 text-red-400" />
            File Manager
          </h2>
          <p className="text-gray-400 mt-1">Browse and manage files on target systems</p>
        </div>
        <div className="flex items-center space-x-2">
          <button className="flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors">
            <Upload className="h-4 w-4 mr-2" />
            Upload
          </button>
          <button className="flex items-center px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors">
            <Download className="h-4 w-4 mr-2" />
            Download
          </button>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="flex items-center space-x-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search files..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-red-500 focus:border-transparent"
          />
        </div>
        <button className="flex items-center px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg">
          <Filter className="h-4 w-4 mr-2" />
          Filter
        </button>
      </div>

      {/* Current Path */}
      <div className="bg-gray-800 border border-gray-700 rounded-lg p-4">
        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-400">Current Path:</span>
          <span className="text-sm font-mono text-white">{currentPath}</span>
        </div>
      </div>

      {/* Files Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {filteredFiles.map((file) => (
          <div
            key={file.id}
            className={`bg-gray-800 border border-gray-700 rounded-lg p-4 hover:border-gray-600 transition-colors cursor-pointer ${
              selectedFiles.includes(file.id) ? 'ring-2 ring-red-500' : ''
            }`}
            onClick={() => {
              if (file.type === 'folder') {
                setCurrentPath(file.path)
              } else {
                setSelectedFiles(prev => 
                  prev.includes(file.id) 
                    ? prev.filter(id => id !== file.id)
                    : [...prev, file.id]
                )
              }
            }}
          >
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center">
                {getFileIcon(file)}
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-white truncate max-w-32">
                    {file.name}
                  </h3>
                  <p className="text-xs text-gray-400">{file.agent}</p>
                </div>
              </div>
              <button className="p-1 text-gray-400 hover:text-white">
                <MoreVertical className="h-4 w-4" />
              </button>
            </div>

            <div className="space-y-1 text-xs text-gray-400">
              <div className="flex justify-between">
                <span>Type:</span>
                <span className="text-white capitalize">{file.type}</span>
              </div>
              {file.type === 'file' && (
                <div className="flex justify-between">
                  <span>Size:</span>
                  <span className="text-white">{formatFileSize(file.size)}</span>
                </div>
              )}
              <div className="flex justify-between">
                <span>Modified:</span>
                <span className="text-white">{file.modified.split(' ')[0]}</span>
              </div>
            </div>

            <div className="mt-3 flex space-x-1">
              <button className="flex-1 flex items-center justify-center px-2 py-1 bg-gray-700 hover:bg-gray-600 text-white rounded text-xs">
                <Eye className="h-3 w-3 mr-1" />
                View
              </button>
              <button className="flex-1 flex items-center justify-center px-2 py-1 bg-gray-700 hover:bg-gray-600 text-white rounded text-xs">
                <Download className="h-3 w-3 mr-1" />
                Download
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Empty State */}
      {filteredFiles.length === 0 && (
        <div className="text-center py-12">
          <Lock className="h-16 w-16 text-gray-600 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-400 mb-2">No files found</h3>
          <p className="text-gray-500">
            {searchTerm ? 'Try adjusting your search terms' : 'No files available in this directory'}
          </p>
        </div>
      )}

      {/* Selected Files Actions */}
      {selectedFiles.length > 0 && (
        <div className="fixed bottom-6 left-1/2 transform -translate-x-1/2 bg-gray-800 border border-gray-700 rounded-lg p-4 shadow-lg">
          <div className="flex items-center space-x-4">
            <span className="text-sm text-gray-400">
              {selectedFiles.length} file{selectedFiles.length !== 1 ? 's' : ''} selected
            </span>
            <div className="flex space-x-2">
              <button className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded text-sm">
                Download All
              </button>
              <button className="px-3 py-1 bg-red-600 hover:bg-red-700 text-white rounded text-sm">
                Delete
              </button>
              <button 
                onClick={() => setSelectedFiles([])}
                className="px-3 py-1 bg-gray-600 hover:bg-gray-700 text-white rounded text-sm"
              >
                Clear
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}