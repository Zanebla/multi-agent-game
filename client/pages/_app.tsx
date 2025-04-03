import React from 'react'
import '../styles/globals.css'
import GlobalLoader from '../components/GlobalLoader'

function MyApp({
  Component,
  pageProps,
}: {
  Component: React.ComponentType
  pageProps: any
}) {
  return (
    <>
      <Component {...pageProps} />
      <GlobalLoader isLoading={false} />
    </>
  )
}

export default MyApp
