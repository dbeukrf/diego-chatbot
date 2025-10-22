import { useState, useEffect } from 'react'

interface AsciiAnimationProps {
  frames: string[]
  fps: number
  className?: string
  scrollMode?: boolean
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

  if (scrollMode) {
    // For horizontal scrolling, we'll create a continuous stream of frames
    const repeatedFrames = Array(3).fill(frames).flat() // Repeat frames 3 times for continuous effect
    const currentRepeatedFrame = repeatedFrames[currentFrame % repeatedFrames.length]
    
    return (
      <pre className={`ascii-art ${className}`}>
        {currentRepeatedFrame}
      </pre>
    )
  }

  return (
    <pre className={`ascii-art ${className}`}>
      {frames[currentFrame]}
    </pre>
  )
}

export default AnimatedAscii