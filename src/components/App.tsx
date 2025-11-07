import { useState, useEffect, useRef } from 'react'
import '../styles/App.css'
import AnimatedAscii from './AnimatedAscii'
import { useAsciiFrames } from '../hooks/useAsciiFrames'

interface Message {
  id: number
  type: 'command' | 'response' | 'system'
  content: string
  timestamp: Date
}

function App() {
  const { frames, metadata, loading: asciiLoading, error } = useAsciiFrames()
  
  // Debug logging
  useEffect(() => {
    console.log('App: asciiLoading =', asciiLoading, 'frames.length =', frames.length, 'error =', error)
  }, [asciiLoading, frames.length, error])
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 0,
      type: 'system',
      content: 'Welcome! I\'m an AI DJ, here to help discuss Diego Beuk\'s professional journey and skills!\n\nType \'help\' to see available commands, or just start chatting with me naturally!',
      timestamp: new Date()
    }
  ])
  const [currentInput, setCurrentInput] = useState('')
  const [commandHistory, setCommandHistory] = useState<string[]>([])
  const [historyIndex, setHistoryIndex] = useState(-1)
  const [isLoading, setIsLoading] = useState(false)
  const terminalRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const addMessage = (type: Message['type'], content: string) => {
    const newMessage: Message = {
      id: messages.length,
      type,
      content,
      timestamp: new Date()
    }
    setMessages(prev => [...prev, newMessage])
  }

  const scrollToBottom = () => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight
    }
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      executeCommand(currentInput.trim())
    } else if (e.key === 'ArrowUp') {
      e.preventDefault()
      if (historyIndex < commandHistory.length - 1) {
        const newIndex = historyIndex + 1
        setHistoryIndex(newIndex)
        setCurrentInput(commandHistory[commandHistory.length - 1 - newIndex])
      }
    } else if (e.key === 'ArrowDown') {
      e.preventDefault()
      if (historyIndex > 0) {
        const newIndex = historyIndex - 1
        setHistoryIndex(newIndex)
        setCurrentInput(commandHistory[commandHistory.length - 1 - newIndex])
      } else if (historyIndex === 0) {
        setHistoryIndex(-1)
        setCurrentInput('')
      }
    }
  }

  const executeCommand = async (command: string) => {
    if (!command) return

    addMessage('command', command)
    setCommandHistory(prev => [...prev, command])
    setHistoryIndex(-1)
    setCurrentInput('')
    setIsLoading(true)

    try {
      const response = await handleCommand(command)
      // Don't add empty responses (like from clear command)
      if (response && response.trim() !== '') {
        addMessage('response', response)
      }
    } catch (error) {
      addMessage('response', `Error: ${error instanceof Error ? error.message : 'Unknown error'}`)
    } finally {
      setIsLoading(false)
    }
  }

  const handleCommand = async (command: string): Promise<string> => {
    const [cmd, ...args] = command.split(' ')

    switch (cmd.toLowerCase()) {
      case 'help':
        return `
1. help                                 - Show a numbered list of available commands
2. spin-profile                         - Generate a quick summary of Diego's professional journey
3. amplify <skill>                      - Expand on a specific soft/technical skill with examples
4. career-analysis <job>                - Compare Diego's skills with a target job role
5. clear                                - Clear terminal

➜ You can also just type naturally and I'll answer any of your questions about Diego!`


      case 'spin-profile':
        try {
          const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: 'Generate a recruiter-ready summary of Diego Beuk\'s profile - short, catchy, and impactful. Focus on his key experience, strengths, achievements, and what makes him stand out to employers.' })
          })
          const result = await response.json()
          return result.response || 'No response received'
        } catch (error) {
          return 'Error generating profile. Make sure the backend is running.'
        }

      case 'amplify':
        if (args.length === 0) {
          return 'Usage: amplify <skill>\nExample: amplify Python\nExample: amplify leadership'
        }
        try {
          const skill = args.join(' ')
          const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: `Expand on Diego's ${skill} skills with measurable examples and impact statements. Show specific achievements and how this skill has contributed to his professional growth.` })
          })
          const result = await response.json()
          return result.response || 'No response received'
        } catch (error) {
          return 'Error amplifying skill. Make sure the backend is running.'
        }

      case 'career-analysis':
        if (args.length === 0) {
          return 'Usage: career-analysis <job role>\nExample: career-analysis AI Software Developer\nExample: career-analysis Product Manager'
        }
        try {
          const jobRole = args.join(' ')
          const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: `Compare Diego's experiences and skills with the ${jobRole} role. Identify his strengths, potential gaps, and how his unique background could be an advantage for this position.` })
          })
          const result = await response.json()
          return result.response || 'No response received'
        } catch (error) {
          return 'Error analysing career analysis. Make sure the backend is running.'
        }

      case 'clear':
        setMessages([])
        return ''

      case 'sudo':
        return `nice try. this isn't production.`

      case 'whoami':
        return 'Guest user of Diego Beuk\'s AI DJ ;)'

      case 'rm -rf /':
        return 'deleting system...' // TODO: trigger a meltdown of the ascii art

      case 'exit':
        window.close()
        return ''

      default:
        // If it's not a recognized command, treat it as a natural conversation
        try {
          const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: command })
          })
          const result = await response.json()
          return result.response || 'No response received'
        } catch (error) {
          return `Unknown command: ${cmd}. Type \'help\' for available commands, or try chatting naturally!`
        }
    }
  }

  const formatTimestamp = (date: Date) => {
    return date.toLocaleTimeString()
  }

  return (
    <div className="terminal-container">
    {/* Terminal Header */}
    <div className="terminal-header">
      {asciiLoading ? (
        <div className="terminal-title">
          Diego Beuk's AI DJ
        </div>
      ) : error ? (
        <div className="header-content">
          <span className="error-text">Error loading ASCII art</span>
          <span className="title-text">Diego Beuk's AI DJ</span>
        </div>
      ) : (
        <>
          <div className="header-content">
            <span className="title-text">Diego Beuk's AI DJ</span>
          </div>
          <div className="ascii-container">
            <AnimatedAscii 
              frames={frames} 
              fps={metadata?.fps || 8} 
              className="header-ascii"
            />
          </div>
        </>
      )}
    </div>

      {/* Terminal Body */}
      <div className="terminal-body" ref={terminalRef}>
        {messages.map((message) => (
          <div key={message.id} className={`message ${message.type}`}>
            {message.type === 'command' && (
              <span className="prompt">
                <span className="user">user@aidj</span>
                <span className="separator">:</span>
                <span className="path">~</span>
                <span className="separator">$</span>
              </span>
            )}
            {message.type === 'response' && (
              <span className="system-prompt">system/ai.dj:</span>
            )}
            {message.type === 'system' && (
              <span className="system-prompt">system/ai.dj:</span>
            )}
            <span className="content">{message.content}</span>
            <span className="timestamp">[{formatTimestamp(message.timestamp)}]</span>
          </div>
        ))}
        {isLoading && (
          <div className="message system">
            <span className="system-prompt">system/ai.dj:</span>
            <span className="loading-dots">...</span>
          </div>
        )}
        <div className="input-line">
          <span className="prompt">
            <span className="user">user@aidj</span>
            <span className="separator">:</span>
            <span className="path">~</span>
            <span className="separator">$</span>
          </span>
          <input
            ref={inputRef}
            type="text"
            value={currentInput}
            onChange={(e) => setCurrentInput(e.target.value)}
            onKeyDown={handleKeyPress}
            className="terminal-input"
            autoFocus
            placeholder=""
          />
        </div>
      </div>
    </div>
  )
}

export default App
