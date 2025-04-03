import React from 'react'
import styles from './GlobalLoader.module.css'

interface GlobalLoaderProps {
  isLoading: boolean
}

export default function GlobalLoader({ isLoading }: GlobalLoaderProps) {
  if (!isLoading) return null

  return (
    <div className="fixed top-4 right-4 z-[9999]">
      <div className={styles.loader}></div>
    </div>
  )
}
