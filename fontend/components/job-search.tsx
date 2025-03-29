"use client"

import { useState, useEffect } from "react"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { JobCard } from "@/components/job-card"
import type { Job } from "@/lib/types"
import { Search, X, Loader2, Briefcase } from "lucide-react"
import { toast } from "@/components/ui/use-toast"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

type JobPlatform = "indeed" | "linkedin" | "ziprecruiter"

const countries = ["United States", "United Kingdom", "Canada", "Germany", "Australia", "India", "Remote"]

export function JobSearch({ initialJobs }: { initialJobs: Job[] }) {
  const [searchTerm, setSearchTerm] = useState("")
  const [selectedTags, setSelectedTags] = useState<string[]>([])
  const [filteredJobs, setFilteredJobs] = useState<Job[]>(initialJobs)
  const [isLoading, setIsLoading] = useState(false)
  const [location, setLocation] = useState("usa")
  const [platform, setPlatform] = useState<JobPlatform>("indeed")

  useEffect(() => {
    const filtered = initialJobs.filter((job) => {
      const matchesSearch =
        job.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        job.company.toLowerCase().includes(searchTerm.toLowerCase()) ||
        job.description.toLowerCase().includes(searchTerm.toLowerCase())

      const matchesTags = selectedTags.length === 0 || selectedTags.includes(job.location)

      return matchesSearch && matchesTags
    })

    setFilteredJobs(filtered)
  }, [searchTerm, selectedTags, initialJobs])

  const toggleTag = (tag: string) => {
    setSelectedTags((prev) => {
      const isTagSelected = prev.includes(tag)
      const updatedTags = isTagSelected ? prev.filter((t) => t !== tag) : [...prev, tag]

      if (!isTagSelected) {
        let apiLocation = "usa"
        if (tag === "United States") apiLocation = "USA"
        else if (tag === "United Kingdom") apiLocation = "uk"
        else if (tag === "Canada") apiLocation = "canada"
        else if (tag === "Germany") apiLocation = "germany"
        else if (tag === "Australia") apiLocation = "australia"
        else if (tag === "India") apiLocation = "india"
        else if (tag === "Remote") apiLocation = "remote"

        setLocation(apiLocation)
      }

      return updatedTags
    })
  }

  const handleSearch = async () => {
    if (!searchTerm.trim()) {
      toast({
        title: "Please enter a search term",
        description: "Enter a job title, company, or keywords to search",
        variant: "destructive",
      })
      return
    }

    setIsLoading(true)

    try {
      let endpoint = ""
      let requestBody = {}

      if (platform === "indeed") {
        endpoint = "http://localhost:8000/indeed/get"
        requestBody = {
          search_term: searchTerm,
          google_search_term: `${searchTerm} near ${selectedTags[0] || "newyork"}`,
          location: location,
        }
      } else if (platform === "linkedin") {
        endpoint = "http://localhost:8000/linkdin/get"
        requestBody = {
          skill: searchTerm,
          location: location,
          pagenumber: 1
        }
      } 
      
      // else if (platform === "ziprecruiter") {
      //   endpoint = "http://localhost:8000/ziprecuter/get"
      //   requestBody = {
      //     search_term: searchTerm,
      //     location: location,
      //   }
      // }

      else if (platform === "ziprecruiter") {
        endpoint = "http://localhost:8000/ziprecuter/get" // Fix typo in endpoint
        requestBody = {
          search_term: searchTerm,
          google_search_term: `${searchTerm} near ${selectedTags[0] || "newyork"}`, // Add required field
          location: location,
          results_wanted: 20, // Add required parameter
          hours_old: 72, // Add required parameter
          country_indeed: "USA" // Add required parameter
        }
      }

      const response = await fetch(endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestBody),
      })

      if (!response.ok) throw new Error(`Error: ${response.status}`)
      const data = await response.json()

      let apiJobs: Job[] = []
      if (platform === "indeed") {
        apiJobs = data.map((item: any[], index: number) => ({
          id: `indeed-${index}`,
          title: item[1] || "Unknown Position",
          company: item[0] || "Unknown Company",
          location: selectedTags[0] || "Unknown Location",
          description: `This job was posted on Indeed. Click "View Details" to learn more.`,
          salary: item[4] || "Salary not specified",
          postedDate: item[3] || new Date().toISOString(),
          url: item[2] || "#",
        }))
      } else if (platform === "linkedin") {
        apiJobs = data.map((item: any[], index: number) => ({
          id: `linkedin-${index}`,
          title: item[1] || "Unknown Position",
          company: item[0] || "Unknown Company",
          location: location,
          description: `This job was posted on LinkedIn. Click "View Details" to learn more.`,
          salary: item[3] || "Salary not specified",
          postedDate: new Date().toISOString(), // LinkedIn provides relative time, use current date as fallback
          url: item[2] || "#",
        }))
      } 
      
      // else if (platform === "ziprecruiter") {
      //   apiJobs = data.map((item: any[], index: number) => ({
      //     id: `zip-${index}`,
      //     title: item[1] || "Unknown Position",
      //     company: item[0] || "Unknown Company",
      //     location: location,
      //     description: `This job was posted on ZipRecruiter. Click "View Details" to learn more.`,
      //     salary: item[4] || "Salary not specified",
      //     postedDate: item[3] || new Date().toISOString(),
      //     url: item[2] || "#",
      //   }))
      // }


    else if (platform === "ziprecruiter") {
      apiJobs = data.map((item: any, index: number) => ({
        id: `zip-${index}`,
        title: item.title || "Unknown Position",
        company: item.company || "Unknown Company",
        location: item.location || location,
        description: item.description || `This job was posted on ZipRecruiter. Click "View Details" to learn more.`,
        salary: item.salary_info || "Salary not specified",
        postedDate: item.date_posted || new Date().toISOString(),
        url: item.job_url || "#",
      }))
    }

      setFilteredJobs(apiJobs)
      toast({
        title: `${platform.charAt(0).toUpperCase() + platform.slice(1)} search completed`,
        description: `Found ${apiJobs.length} jobs matching "${searchTerm}"`,
      })
    } catch (error) {
      console.error("Error fetching jobs:", error)
      toast({
        title: "Error searching jobs",
        description: "There was a problem connecting to the search service. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  // The rest of the component remains the same...


  return (
    <div className="space-y-8">
      <div className="bg-card rounded-xl shadow-lg p-6 border border-border/40">
        <div className="mb-6">
          <div className="flex flex-col md:flex-row gap-4 mb-4">
            <Select value={platform} onValueChange={(value: JobPlatform) => setPlatform(value)}>
              <SelectTrigger className="w-full md:w-[200px]">
                <SelectValue placeholder="Select Platform" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="indeed">Indeed</SelectItem>
                <SelectItem value="linkedin">LinkedIn</SelectItem>
                <SelectItem value="ziprecruiter">ZipRecruiter</SelectItem>
              </SelectContent>
            </Select>

            <div className="relative flex-grow flex items-center">
              <div className="relative flex-grow">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-5 w-5" />
                <Input
                  placeholder="Search for jobs, companies, or keywords..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 h-12 bg-background/50 border-muted pr-10"
                  onKeyDown={(e) => {
                    if (e.key === "Enter") {
                      handleSearch()
                    }
                  }}
                />
                {searchTerm && (
                  <Button
                    onClick={() => setSearchTerm("")}
                    variant="ghost"
                    size="icon"
                    className="absolute right-2 top-1/2 transform -translate-y-1/2 h-8 w-8"
                  >
                    <X className="h-4 w-4" />
                  </Button>
                )}
              </div>
              <Button className="ml-2 h-12 px-6" onClick={handleSearch} disabled={isLoading}>
                {isLoading ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Searching...
                  </>
                ) : (
                  <>
                    <Search className="h-4 w-4 mr-2" />
                    Search
                  </>
                )}
              </Button>
            </div>
          </div>

          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Briefcase className="h-4 w-4" />
            <span>
              Searching on: <span className="font-medium text-foreground capitalize">{platform}</span>
            </span>
          </div>
        </div>

        <div className="space-y-3">
          <h2 className="text-sm font-medium text-muted-foreground">Filter by location:</h2>
          <div className="flex flex-wrap gap-2">
            {countries.map((country) => (
              <Badge
                key={country}
                variant={selectedTags.includes(country) ? "default" : "outline"}
                className={`cursor-pointer text-xs px-3 py-1 rounded-full transition-all ${
                  selectedTags.includes(country) ? "bg-primary hover:bg-primary/90" : "hover:bg-muted"
                }`}
                onClick={() => toggleTag(country)}
              >
                {country}
              </Badge>
            ))}
          </div>
        </div>
      </div>

      <div className="space-y-6">
        <div className="flex justify-between items-center border-b border-border/40 pb-3">
          <h2 className="text-xl font-semibold">Available Positions</h2>
          <p className="text-sm text-muted-foreground px-3 py-1 bg-muted rounded-full">
            {filteredJobs.length} jobs found
          </p>
        </div>

        {isLoading ? (
          <div className="text-center py-16 bg-card rounded-xl border border-border/40">
            <div className="flex flex-col items-center gap-2">
              <Loader2 className="h-12 w-12 text-primary animate-spin" />
              <h3 className="text-xl font-medium mt-2">Searching for jobs...</h3>
              <p className="text-muted-foreground max-w-md">
                We're looking for the best matches for "{searchTerm}" on {platform}. This may take a moment.
              </p>
            </div>
          </div>
        ) : filteredJobs.length > 0 ? (
          <div className="grid gap-6">
            {filteredJobs.map((job) => (
              <JobCard key={job.id} job={job} />
            ))}
          </div>
        ) : (
          <div className="text-center py-16 bg-card rounded-xl border border-border/40">
            <div className="flex flex-col items-center gap-2">
              <Search className="h-12 w-12 text-muted-foreground/50" />
              <h3 className="text-xl font-medium mt-2">No jobs found</h3>
              <p className="text-muted-foreground max-w-md">
                We couldn't find any jobs matching your search criteria. Try adjusting your filters or search term.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

