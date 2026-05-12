import { expect, test } from 'vitest'
import { render } from '@testing-library/react'
import Navbar from './components/Navbar'
import App from './App'
import SidePanel from './components/SidePanel'
function sum(a, b) {
  return a + b
}

// errors because ./data/countries is not mocked, and it is imported by App.jsx
test('renders app', () => {
  render(<App />)
})

test('renders navbar', () => {
  render(<Navbar />)
})