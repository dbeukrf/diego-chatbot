import { useState, useEffect } from 'react'

interface AsciiAnimationProps {
  frames: string[]
  fps: number
  className?: string
  scrollMode?: boolean
}

// Function to get shading class for a character
const getShadingClass = (char: string): string => {
  // White/brightest characters - solid blocks
  if (char === '#' || char === '%') {
    return 'ascii-shade-white'
  }
  // Light characters - stars and plus signs
  if (char === '*' || char === '+') {
    return 'ascii-shade-light'
  }
  // Medium characters - equals and dashes
  if (char === '=' || char === '-') {
    return 'ascii-shade-medium'
  }
  // Dark characters - dots and colons
  if (char === '.' || char === ':') {
    return 'ascii-shade-dark'
  }
  // Black/darkest characters - spaces and newlines
  if (char === ' ' || char === '\n' || char === '\r') {
    return 'ascii-shade-black'
  }
  // Default for other characters - treat as medium
  return 'ascii-shade-medium'
}

// Function to render ASCII with shading
const renderAsciiWithShading = (asciiText: string): JSX.Element => {
  return (
    <>
      {asciiText.split('').map((char, index) => (
        <span key={index} className={getShadingClass(char)}>
          {char}
        </span>
      ))}
    </>
  )
}

const AnimatedAscii: React.FC<AsciiAnimationProps> = ({ frames, fps, className = '', scrollMode = false }) => {
  const [currentFrame, setCurrentFrame] = useState(0)

  useEffect(() => {
    console.log('AnimatedAscii: frames.length =', frames.length, 'fps =', fps)
    if (frames.length === 0) return

    const interval = setInterval(() => {
      setCurrentFrame((prev) => (prev + 1) % frames.length)
    }, 1000 / fps)

    return () => clearInterval(interval)
  }, [frames, fps])

  if (frames.length === 0) {
    console.log('AnimatedAscii: No frames available, showing loading')
    return <div className={className}>Loading...</div>
  }

  return (
    <pre className={`ascii-art ${className}`}>
      {renderAsciiWithShading(frames[currentFrame])}
    </pre>
  )
}

export default AnimatedAscii