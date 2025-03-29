"use client"

import { formatDistanceToNow } from "date-fns"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import type { Job } from "@/lib/types"
import { Building2, CalendarDays, DollarSign, MapPin, ExternalLink } from "lucide-react"
import { Button } from "@/components/ui/button"

export function JobCard({ job }: { job: Job }) {
  const postedDate = new Date(job.postedDate)
  const timeAgo = formatDistanceToNow(postedDate, { addSuffix: true })

  return (
    <Card className="overflow-hidden transition-all hover:shadow-md hover:border-primary/20 group">
      <div className="h-2 bg-gradient-to-r from-primary to-primary/70 w-full" />
      <CardContent className="p-6">
        <div className="flex flex-col md:flex-row md:items-start gap-4">
          <div className="flex-shrink-0 w-12 h-12 rounded-md bg-primary/10 flex items-center justify-center text-primary">
            {job.logo || <Building2 className="h-6 w-6" />}
          </div>

          <div className="flex-grow space-y-4">
            <div>
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
                <h3 className="font-bold text-xl group-hover:text-primary transition-colors">{job.title}</h3>
                <Badge variant="outline" className="w-fit">
                  <MapPin className="h-3 w-3 mr-1" />
                  {job.location}
                </Badge>
              </div>
              <p className="text-muted-foreground font-medium">{job.company}</p>
            </div>

            <p className="text-sm text-muted-foreground line-clamp-2">{job.description}</p>

            <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3 pt-2">
              <div className="flex items-center text-sm font-medium text-primary">
                <DollarSign className="h-4 w-4 mr-1" />
                {job.salary}
              </div>
              <div className="flex items-center text-xs text-muted-foreground">
                <CalendarDays className="h-3 w-3 mr-1" />
                Posted {timeAgo}
              </div>
            </div>

            <div className="flex flex-col sm:flex-row gap-3 pt-2">
              <Button className="w-full sm:w-auto">Apply Now</Button>
              {job.url ? (
                <Button variant="outline" className="w-full sm:w-auto" onClick={() => window.open(job.url, "_blank")}>
                  <ExternalLink className="h-4 w-4 mr-2" />
                  View Details
                </Button>
              ) : (
                <Button variant="outline" className="w-full sm:w-auto">
                  View Details
                </Button>
              )}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

