import React from 'react'
import '../styles/globals.css'

function MyApp({
  Component,
  pageProps,
}: {
  Component: React.ComponentType
  pageProps: any
}) {
  return <Component {...pageProps} />
}

export default MyApp
