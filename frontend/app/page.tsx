"use client";

import { useEffect, useState, useMemo } from "react";
import {
  Search,
  Building2,
  Briefcase,
  ExternalLink,
  RefreshCw,
} from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

// Sample data - replace with your actual data source
const samplePosts = [
  {
    raw: "Should I expect a interview call from Amazon for sde intern role as I filled up the form and they sent me oa ?There is a opening for sde intern role at Amazon so I filled up being 2025 grad and immediately received the oa link . I gave the oa and it went good like completed in 20 mins .\nSo should I expect a interview call or not ?",
    summary:
      "• Company: Amazon\n• Role: SDE Intern\n• Interview experience: \n  - Received OA link immediately after filling the form\n  - Completed OA in 20 minutes and it went well",
    url: "https://www.reddit.com/r/leetcode/comments/1gg9wnq/should_i_expect_a_interview_call_from_amazon_for/",
  },
  {
    raw: "Amazon: Got rejection after 2 hours of virtual onsite interviewToday, i got interviewed for SDE-1 at amazon. I cleared all codings given and answered all LP principles well. Interviewers are also impressed.\n\nBut i got rejection after 2 hours of completing all three interviews. I reached out to the recruiter no response.\n\nWhat is this, what's wrong.",
    summary:
      "• The interview was a virtual onsite interview.\n• It lasted for 2 hours.\n• The candidate cleared all coding given and answered all LP (likely LeetCode) principles well.\n• The interviewers were impressed.\n• The candidate received a rejection after completing all three interviews.\n• The candidate reached out to the recruiter but received no response.",
    url: "https://i.redd.it/wa1rs7cg58yd1.jpeg",
  },
  {
    raw: "Google L4 Software Engineer interview process was intense but fair. Had 4 rounds including system design and coding. The interviewers were really helpful and gave hints when I was stuck.",
    summary:
      "• Company: **<Google>**\n• Role: **<L4 Software Engineer>**\n• Interview experience: \n  - **<4 rounds>** total\n  - System design and coding rounds\n  - Helpful interviewers who provided hints",
    url: "https://www.reddit.com/r/cscareerquestions/example1",
  },
];

interface InterviewPost {
  raw: string;
  summary: string;
  url: string;
}

const extractCompanyFromPost = (post: InterviewPost): string => {
  // Try structured format first
  const structuredMatch = post.summary.match(/• Company: (.+)/i);
  if (structuredMatch) return structuredMatch[1].trim();

  const companies = [
    "Amazon",
    "Google",
    "Microsoft",
    "Meta",
    "Apple",
    "Netflix",
    "Tesla",
    "Uber",
    "Airbnb",
    "Spotify",
    "Twitter",
    "LinkedIn",
    "Salesforce",
    "Oracle",
    "IBM",
    "Intel",
    "NVIDIA",
    "Adobe",
    "Shopify",
    "Stripe",
    "Coinbase",
    "Palantir",
    "Databricks",
    "Snowflake",
    "TikTok",
  ];

  // Search only in summary text, match whole words only
  const summaryText = post.summary.toLowerCase();
  for (const company of companies) {
    const companyLower = company.toLowerCase();
    const regex = new RegExp(`\\b${companyLower}\\b`, "i");
    if (regex.test(summaryText)) {
      return company;
    }
  }

  // If not found in summary, return Unknown
  return "Unknown";
};

const extractRoleFromPost = (post: InterviewPost): string => {
  // Patterns for normalization
  const rolePatterns = [
    {
      regex:
        /sde[\s\-]?i\b|sde[\s\-]?1\b|sdei\b|sde1\b|software engineer[\s\-]?i\b|software engineer[\s\-]?1\b/i,
      norm: "SDE I",
    },
    {
      regex:
        /sde[\s\-]?ii\b|sde[\s\-]?2\b|sdeii\b|sde2\b|software engineer[\s\-]?ii\b|software engineer[\s\-]?2\b/i,
      norm: "SDE II",
    },
    {
      regex:
        /sde[\s\-]?iii\b|sde[\s\-]?3\b|sdeiii\b|sde3\b|software engineer[\s\-]?iii\b|software engineer[\s\-]?3\b/i,
      norm: "SDE III",
    },
    { regex: /sde[\s\-]?intern|software engineer intern/i, norm: "SDE Intern" },
    { regex: /swe[\s\-]?intern/i, norm: "SWE Intern" },
    { regex: /software engineer/i, norm: "Software Engineer" },
    { regex: /software developer/i, norm: "Software Developer" },
    { regex: /backend engineer/i, norm: "Backend Engineer" },
    { regex: /frontend engineer/i, norm: "Frontend Engineer" },
    { regex: /full[\s\-]?stack engineer/i, norm: "Full Stack Engineer" },
    { regex: /data scientist/i, norm: "Data Scientist" },
    { regex: /data engineer/i, norm: "Data Engineer" },
    { regex: /product manager/i, norm: "Product Manager" },
    { regex: /engineering manager/i, norm: "Engineering Manager" },
    { regex: /l\d+/i, norm: "Google L Level" },
    { regex: /e\d+/i, norm: "Meta E Level" },
    { regex: /new grad/i, norm: "New Grad" },
    { regex: /intern/i, norm: "Intern" },
  ];

  // Try structured format first
  const structuredMatch = post.summary.match(/• Role: (.+)/i);
  let roleRaw = structuredMatch ? structuredMatch[1].trim() : "";
  let role = "";

  // If roleRaw contains multiple roles (e.g., "Intern & New Grad"), split and normalize each
  if (roleRaw) {
    // Split on common delimiters
    const roleParts = roleRaw
      .split(/[,/&]| and |\s*\+\s*/i)
      .map((r) => r.trim())
      .filter(Boolean);
    const normalizedRoles = [];
    for (const part of roleParts) {
      let found = false;
      for (const { regex, norm } of rolePatterns) {
        if (part.match(regex)) {
          normalizedRoles.push(norm);
          found = true;
          break;
        }
      }
      if (!found) normalizedRoles.push(part);
    }
    // Prioritize summary roles, join with ' & ' if multiple
    role = normalizedRoles.length > 0 ? normalizedRoles.join(" & ") : roleRaw;
  } else {
    // Only look in raw if summary role is missing
    const fullText = post.raw;
    for (const { regex, norm } of rolePatterns) {
      if (fullText.match(regex)) {
        role = norm;
        break;
      }
    }
  }

  return role || "Unknown";
};

// Utility function to remove bold patterns from text
const parseBoldPatterns = (text: string): string => {
  if (!text) return text;

  // Remove all **word** patterns from the text
  return text.replace(/\*\*[^*]+\*\*/g, "");
};

export default function InterviewSearchPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [companyFilter, setCompanyFilter] = useState("all");
  const [roleFilter, setRoleFilter] = useState("all");
  const [posts, setPosts] = useState<InterviewPost[]>(samplePosts);
  const [isFetching, setIsFetching] = useState(false);
  const [fetchStatus, setFetchStatus] = useState<string>("");
  useEffect(() => {
    console.log(
      "InterviewSearchPage mounted, starting fetch for filtered_summaries.json"
    );
    fetch("/filtered_summaries.json")
      .then((res) => {
        console.log("Fetched filtered_summaries.json, status:", res.status);
        if (!res.ok) {
          console.error("Fetch failed with status:", res.status);
        }
        return res.json();
      })
      .then((data) => {
        console.log("Loaded data from filtered_summaries.json:", data);
        if (!Array.isArray(data)) {
          console.error("filtered_summaries.json is not an array:", data);
        } else {
          console.log(`filtered_summaries.json contains ${data.length} items.`);
        }
        setPosts(data);
        // Log first 3 items for inspection
        if (Array.isArray(data)) {
          data.slice(0, 3).forEach((item, idx) => {
            console.log(`Post[${idx}]:`, item);
          });
        }
      })
      .catch((err) => {
        console.error("Error loading filtered_summaries.json:", err);
        setPosts([]);
      });
  }, []);

  // Function to fetch new Reddit posts
  const fetchNewPosts = async () => {
    setIsFetching(true);
    setFetchStatus("Fetching new Reddit posts...");

    try {
      const response = await fetch(
        "http://localhost:8000/api/fetch-reddit-posts",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      setFetchStatus(
        `Success! Fetched ${result.reddit_posts_count} posts and created ${result.summaries_count} summaries.`
      );

      // Reload the data after successful fetch
      setTimeout(() => {
        window.location.reload();
      }, 2000);
    } catch (error) {
      console.error("Error fetching posts:", error);
      setFetchStatus(
        `Error: ${
          error instanceof Error ? error.message : "Failed to fetch posts"
        }`
      );
    } finally {
      setIsFetching(false);
    }
  };

  // Companies are only from currently filtered posts (by role and search)
  const companies = useMemo(() => {
    // Count interviews per company in filtered posts
    const companyCounts: Record<string, number> = {};
    const filtered = posts.filter((post) => {
      const matchesSearch =
        searchQuery === "" ||
        post.raw.toLowerCase().includes(searchQuery.toLowerCase()) ||
        post.summary.toLowerCase().includes(searchQuery.toLowerCase());
      //fasdfasdfasdf
      const postRole = extractRoleFromPost(post);
      const matchesRole =
        roleFilter === "all" ||
        postRole.toLowerCase().includes(roleFilter.toLowerCase()) ||
        roleFilter.toLowerCase().includes(postRole.toLowerCase());

      return matchesSearch && matchesRole;
    });
    filtered.forEach((post) => {
      const company = extractCompanyFromPost(post);
      if (company !== "Unknown") {
        companyCounts[company] = (companyCounts[company] || 0) + 1;
      }
    });
    // Only include companies with at least one interview
    return Object.keys(companyCounts).sort();
  }, [posts, searchQuery, roleFilter]);

  // (removed duplicate filteredPosts declaration)

  // Roles are only from currently filtered posts (by company and search)
  const roles = useMemo(() => {
    const rolesSet = new Set<string>();
    const filtered = posts.filter((post) => {
      const matchesSearch =
        searchQuery === "" ||
        post.raw.toLowerCase().includes(searchQuery.toLowerCase()) ||
        post.summary.toLowerCase().includes(searchQuery.toLowerCase());

      const postCompany = extractCompanyFromPost(post);
      const matchesCompany =
        companyFilter === "all" ||
        postCompany.toLowerCase() === companyFilter.toLowerCase();

      const postRole = extractRoleFromPost(post);
      const matchesRole =
        roleFilter === "all" ||
        postRole.toLowerCase().includes(roleFilter.toLowerCase()) ||
        roleFilter.toLowerCase().includes(postRole.toLowerCase());

      return matchesSearch && matchesCompany && matchesRole;
    });
    filtered.forEach((post) => {
      const role = extractRoleFromPost(post);
      if (role !== "Unknown") rolesSet.add(role);
    });
    return Array.from(rolesSet).sort();
  }, [posts, searchQuery, companyFilter, roleFilter]);

  const filteredPosts = useMemo(() => {
    return posts.filter((post) => {
      const matchesSearch =
        searchQuery === "" ||
        post.raw.toLowerCase().includes(searchQuery.toLowerCase()) ||
        post.summary.toLowerCase().includes(searchQuery.toLowerCase());

      const postCompany = extractCompanyFromPost(post);
      const matchesCompany =
        companyFilter === "all" ||
        postCompany.toLowerCase() === companyFilter.toLowerCase();

      const postRole = extractRoleFromPost(post);
      const matchesRole =
        roleFilter === "all" ||
        postRole.toLowerCase().includes(roleFilter.toLowerCase()) ||
        roleFilter.toLowerCase().includes(postRole.toLowerCase());

      return matchesSearch && matchesCompany && matchesRole;
    });
  }, [posts, searchQuery, companyFilter, roleFilter]);

  const getCompanyForDisplay = (post: InterviewPost) => {
    return extractCompanyFromPost(post);
  };

  const getRoleForDisplay = (post: InterviewPost) => {
    return extractRoleFromPost(post);
  };

  // Pagination state
  const [currentPage, setCurrentPage] = useState(1);
  const postsPerPage = 10;
  const totalPages = useMemo(
    () => Math.min(10, Math.ceil(filteredPosts.length / postsPerPage)),
    [filteredPosts]
  );
  const paginatedPosts: InterviewPost[] = useMemo(() => {
    const startIdx = (currentPage - 1) * postsPerPage;
    return filteredPosts.slice(startIdx, startIdx + postsPerPage);
  }, [filteredPosts, currentPage]);

  // State to track expanded posts
  const [expandedPosts, setExpandedPosts] = useState<{
    [key: number]: boolean;
  }>({});
  const toggleExpand = (index: number) => {
    setExpandedPosts((prev) => ({ ...prev, [index]: !prev[index] }));
  };

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex flex-col items-center justify-center gap-2">
            <div className="flex items-center gap-2">
              <h1 className="text-4xl font-bold text-foreground mb-2">
                Interview Experience Search
              </h1>
            </div>
            <div className="mb-2 flex items-center justify-center gap-2">
              <img
                src="https://www.redditstatic.com/desktop2x/img/favicon/apple-icon-57x57.png"
                alt="Reddit Logo"
                className="h-6 w-6"
              />
              <span className="text-orange-500 text-lg font-semibold">
                sourced from Reddit
              </span>
            </div>
            <p className="text-muted-foreground text-lg">
              Search through thousands of interview experiences from top tech
              companies
            </p>
          </div>
        </div>

        {/* Disclaimer */}
        <Card className="mb-6 border-orange-200 bg-orange-50 dark:border-orange-800 dark:bg-orange-950/20">
          <CardContent className="p-4">
            <div className="flex items-start gap-3">
              <div className="flex-shrink-0 mt-0.5">
                <div className="w-5 h-5 bg-orange-100 dark:bg-orange-900 rounded-full flex items-center justify-center">
                  <span className="text-orange-600 dark:text-orange-400 text-sm font-bold">
                    !
                  </span>
                </div>
              </div>
              <div className="flex-1">
                <h3 className="text-sm font-semibold text-orange-800 dark:text-orange-200 mb-1">
                  Important Disclaimer
                </h3>
                <p className="text-sm text-orange-700 dark:text-orange-300 leading-relaxed">
                  This application is for{" "}
                  <strong>educational and research purposes only</strong>. All
                  interview experiences are collected from public Reddit posts
                  and are user-generated content. Please respect Reddit's terms
                  of service and API usage guidelines. The information provided
                  may not be accurate, complete, or up-to-date. Always verify
                  information from official sources and consult with
                  professionals for career advice.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Search and Filters */}
        <Card className="mb-8">
          <CardContent className="p-6">
            <div className="flex flex-col gap-4">
              {/* Search Input */}
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
                <Input
                  placeholder="Search interview experiences..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10 h-12 text-base"
                />
              </div>

              {/* Filters */}
              <div className="flex flex-col sm:flex-row gap-4">
                <div className="flex-1">
                  <Select
                    value={companyFilter}
                    onValueChange={setCompanyFilter}
                  >
                    <SelectTrigger className="h-10">
                      <Building2 className="h-4 w-4 mr-2" />
                      <SelectValue placeholder="Filter by company" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Companies</SelectItem>
                      {companies.map((company) => (
                        <SelectItem key={company} value={company}>
                          {company}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="flex-1">
                  <Select value={roleFilter} onValueChange={setRoleFilter}>
                    <SelectTrigger className="h-10">
                      <Briefcase className="h-4 w-4 mr-2" />
                      <SelectValue placeholder="Filter by role" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Roles</SelectItem>
                      {roles.map((role) => (
                        <SelectItem key={role} value={role}>
                          {role}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <Button
                  variant="outline"
                  onClick={() => {
                    setSearchQuery("");
                    setCompanyFilter("all");
                    setRoleFilter("all");
                  }}
                  className="h-10"
                >
                  Clear Filters
                </Button>

                <Button
                  variant="default"
                  onClick={fetchNewPosts}
                  disabled={isFetching}
                  className="h-10"
                >
                  <RefreshCw
                    className={`h-4 w-4 mr-2 ${
                      isFetching ? "animate-spin" : ""
                    }`}
                  />
                  {isFetching ? "Fetching..." : "Fetch New Posts"}
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Fetch Status */}
        {fetchStatus && (
          <Card className="mb-4">
            <CardContent className="p-4">
              <p
                className={`text-sm ${
                  fetchStatus.includes("Error")
                    ? "text-red-600"
                    : "text-green-600"
                }`}
              >
                {fetchStatus}
              </p>
            </CardContent>
          </Card>
        )}

        {/* Results Count */}
        <div className="mb-6 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <p className="text-muted-foreground">
            Showing {filteredPosts.length} of {posts.length} interview
            experiences
          </p>
          {totalPages > 1 && (
            <div className="flex items-center gap-2">
              <span className="text-muted-foreground">Page:</span>
              <select
                value={currentPage}
                onChange={(e) => setCurrentPage(Number(e.target.value))}
                className="border rounded px-2 py-1"
              >
                {Array.from({ length: totalPages }, (_, i) => i + 1).map(
                  (pageNum) => (
                    <option key={pageNum} value={pageNum}>
                      {pageNum}
                    </option>
                  )
                )}
              </select>
            </div>
          )}
        </div>

        {/* Results */}
        <div className="space-y-6">
          {paginatedPosts.length === 0 ? (
            <Card>
              <CardContent className="p-8 text-center">
                <p className="text-muted-foreground text-lg">
                  No interview experiences found matching your criteria.
                </p>
                <p className="text-muted-foreground mt-2">
                  Try adjusting your search terms or filters.
                </p>
              </CardContent>
            </Card>
          ) : (
            paginatedPosts.map((post: InterviewPost, index: number) => {
              // Use global index for expandedPosts
              const globalIndex = (currentPage - 1) * postsPerPage + index;
              return (
                <Card
                  key={globalIndex}
                  className="hover:shadow-md transition-shadow"
                >
                  <CardHeader>
                    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                      <div className="flex flex-wrap gap-2">
                        <Badge
                          variant="secondary"
                          className="flex items-center gap-1"
                        >
                          <Building2 className="h-3 w-3" />
                          {getCompanyForDisplay(post)}
                        </Badge>
                        <Badge
                          variant="outline"
                          className="flex items-center gap-1"
                        >
                          <Briefcase className="h-3 w-3" />
                          {getRoleForDisplay(post)}
                        </Badge>
                      </div>
                      <Button variant="ghost" size="sm" asChild>
                        <a
                          href={post.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-center gap-1"
                        >
                          View Original
                          <ExternalLink className="h-3 w-3" />
                        </a>
                      </Button>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div>
                        <h3 className="font-semibold text-foreground mb-2">
                          Summary
                        </h3>
                        <div className="text-muted-foreground whitespace-pre-line text-sm leading-relaxed">
                          {parseBoldPatterns(post.summary)}
                        </div>
                      </div>

                      <div>
                        <h3 className="font-semibold text-foreground mb-2">
                          Full Experience
                        </h3>
                        <div>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => toggleExpand(globalIndex)}
                            className="mb-2"
                          >
                            {expandedPosts[globalIndex]
                              ? "Hide Full Post"
                              : "Show Full Post"}
                          </Button>
                          <p
                            className={`text-muted-foreground text-sm leading-relaxed whitespace-pre-line ${
                              expandedPosts[globalIndex] ? "" : "line-clamp-3"
                            }`}
                          >
                            {post.raw}
                          </p>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })
          )}
        </div>
      </div>
      {/* Disclaimer */}
      <div className="mt-12 text-center text-xs text-muted-foreground">
        <hr className="my-4" />
        <p>
          <strong>Disclaimer:</strong> This content is scraped from Reddit. All
          interview experiences and posts belong to their respective Reddit
          users and are not my own.
        </p>
      </div>
    </div>
  );
}
