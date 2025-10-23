import { useState, useEffect } from 'react'

interface AsciiMetadata {
  total_frames: number
  width: number
  height: number
  fps: number
  duration: number
  original_fps: number
  original_duration: number
}

export const useAsciiFrames = () => {
  const [frames, setFrames] = useState<string[]>([])
  const [metadata, setMetadata] = useState<AsciiMetadata | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const loadFrames = async () => {
      try {
        console.log('Loading ASCII frames...')
        // Load metadata first
        const metadataResponse = await fetch('/media/ascii_frames/metadata.json')
        if (!metadataResponse.ok) {
          throw new Error('Failed to load metadata')
        }
        const metadataData: AsciiMetadata = await metadataResponse.json()
        console.log('Metadata loaded:', metadataData)
        setMetadata(metadataData)

        // Load all frames
        const framePromises = []
        for (let i = 0; i < metadataData.total_frames; i++) {
          const frameNumber = i.toString().padStart(4, '0')
          framePromises.push(
            fetch(`/media/ascii_frames/frame_${frameNumber}.txt`)
              .then(response => response.text())
          )
        }

        const frameTexts = await Promise.all(framePromises)
        console.log('Frames loaded:', frameTexts.length)
        setFrames(frameTexts)
        setLoading(false)
      } catch (err) {
        console.error('Error loading ASCII frames:', err)
        setError(err instanceof Error ? err.message : 'Failed to load ASCII frames')
        setLoading(false)
      }
    }

    loadFrames()
  }, [])

  return { frames, metadata, loading, error }
}