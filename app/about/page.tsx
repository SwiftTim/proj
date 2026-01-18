import Link from "next/link"

export default function AboutPage() {
  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-16 max-w-4xl">
        <div className="mb-12 text-center">
          <h1 className="text-4xl font-bold mb-4">About BudgetAI</h1>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Empowering transparency and accountability in government budgeting through artificial intelligence
          </p>
        </div>

        <div className="space-y-12">
          <section>
            <h2 className="text-2xl font-semibold mb-4">Our Mission</h2>
            <p className="text-muted-foreground leading-relaxed">
              BudgetAI was created to democratize access to government budget information and make fiscal transparency
              accessible to everyone. We believe that citizens, researchers, journalists, and government officials
              should have the tools they need to understand and analyze public spending effectively.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">The Problem We Solve</h2>
            <p className="text-muted-foreground leading-relaxed mb-4">
              Government budget documents are often complex, lengthy, and difficult to analyze. Traditional methods of
              budget analysis are time-consuming and require specialized expertise. This creates barriers to
              transparency and makes it difficult for stakeholders to hold governments accountable.
            </p>
            <p className="text-muted-foreground leading-relaxed">
              BudgetAI uses advanced artificial intelligence to automatically extract, analyze, and score budget
              documents, making transparency analysis accessible to everyone regardless of their technical background.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">Our Technology</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="p-6 border rounded-lg">
                <h3 className="font-semibold mb-2">AI-Powered OCR</h3>
                <p className="text-sm text-muted-foreground">
                  Advanced optical character recognition that can extract text from complex budget documents with 99.7%
                  accuracy.
                </p>
              </div>
              <div className="p-6 border rounded-lg">
                <h3 className="font-semibold mb-2">Natural Language Processing</h3>
                <p className="text-sm text-muted-foreground">
                  Sophisticated NLP algorithms that understand budget terminology and can identify key financial
                  information automatically.
                </p>
              </div>
              <div className="p-6 border rounded-lg">
                <h3 className="font-semibold mb-2">Transparency Scoring</h3>
                <p className="text-sm text-muted-foreground">
                  Proprietary algorithms that evaluate budget documents against international transparency standards and
                  best practices.
                </p>
              </div>
              <div className="p-6 border rounded-lg">
                <h3 className="font-semibold mb-2">Real-time Monitoring</h3>
                <p className="text-sm text-muted-foreground">
                  Continuous monitoring systems that can detect changes and anomalies in budget documents as they're
                  published.
                </p>
              </div>
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">Our Impact</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center">
                <div className="text-3xl font-bold text-accent mb-2">50+</div>
                <p className="text-sm text-muted-foreground">Government agencies using our platform</p>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-accent mb-2">$2.3M</div>
                <p className="text-sm text-muted-foreground">In potential fraud detected</p>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-accent mb-2">95%</div>
                <p className="text-sm text-muted-foreground">Faster analysis than manual methods</p>
              </div>
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">Our Team</h2>
            <p className="text-muted-foreground leading-relaxed mb-4">
              BudgetAI was founded by a team of researchers, technologists, and transparency advocates with experience
              in government, academia, and the private sector. Our diverse backgrounds give us unique insights into the
              challenges of budget transparency and the potential of technology to address them.
            </p>
            <p className="text-muted-foreground leading-relaxed">
              We're supported by leading organizations in the transparency and accountability space, including
              Transparency International, the Open Government Partnership, and various academic institutions focused on
              public policy research.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">Our Commitment</h2>
            <p className="text-muted-foreground leading-relaxed mb-4">
              We're committed to maintaining the highest standards of data security, privacy, and ethical AI practices.
              We believe that transparency tools should themselves be transparent, which is why we're open about our
              methodologies and regularly publish research on our findings.
            </p>
            <p className="text-muted-foreground leading-relaxed">
              Our platform is designed to complement, not replace, human expertise. We provide tools that enhance human
              analysis capabilities while ensuring that critical decisions remain in human hands.
            </p>
          </section>

          <section className="text-center">
            <h2 className="text-2xl font-semibold mb-4">Join Our Mission</h2>
            <p className="text-muted-foreground leading-relaxed mb-6">
              Whether you're a researcher, journalist, government official, or concerned citizen, BudgetAI can help you
              make sense of complex budget information and hold governments accountable.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/pricing"
                className="px-6 py-3 bg-accent text-accent-foreground rounded-lg font-medium hover:bg-accent/90 transition-colors text-center"
              >
                Start Free Trial
              </Link>
              <Link
                href="/support"
                className="px-6 py-3 border border-border rounded-lg font-medium hover:bg-muted transition-colors text-center"
              >
                Contact Us
              </Link>
            </div>
          </section>
        </div>
      </div>
    </div>
  )
}
