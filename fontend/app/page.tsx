import { JobSearch } from "@/components/job-search"
import { jobData } from "@/lib/data"

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-background to-muted/30">
      <div className="container mx-auto py-12 px-4">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold mb-3 bg-clip-text text-transparent bg-gradient-to-r from-primary to-primary/70">
          JobHub
          </h1>
          <p className="text-muted-foreground max-w-md mx-auto">
            Search thousands of job opportunities from top companies around the world
          </p>
        </div>
        <div className="max-w-4xl mx-auto">
          <JobSearch initialJobs={jobData} />
        </div>
      </div>
    </main>
  )
}

