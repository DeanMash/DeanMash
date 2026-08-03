import { useState } from 'react'
import { Contact } from './components/Contact'
import { Demo } from './components/Demo'
import { Footer } from './components/Footer'
import { Header } from './components/Header'
import { Hero } from './components/Hero'
import { HowItWorks } from './components/HowItWorks'
import { Industries } from './components/Industries'
import { Pricing } from './components/Pricing'
import { Problem } from './components/Problem'
import type { IndustryId } from './data/industries'

export default function App() {
  const [industryId, setIndustryId] = useState<IndustryId>('dental')

  return (
    <>
      <Header />
      <main>
        <Hero />
        <Problem />
        <HowItWorks />
        <Industries selected={industryId} onSelect={setIndustryId} />
        <Demo industryId={industryId} onIndustryChange={setIndustryId} />
        <Pricing />
        <Contact />
      </main>
      <Footer />
    </>
  )
}
