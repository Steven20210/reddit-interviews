"use client";
import { Analytics } from "@vercel/analytics/next";
import { useEffect, useState } from "react";
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
import { set } from "date-fns";

// ---------------------------------------------
// Types
// ---------------------------------------------
interface InterviewPost {
  raw: string;
  summary: string;
  url: string;
  company?: string;
  role?: string;
}

type ApiResponse = {
  posts: InterviewPost[];
  companies: string[];
  roles: string[];
  total: number;
  page: number;
  limit: number;
};

// ---------------------------------------------
// Utilities
// ---------------------------------------------
const parseBoldPatterns = (text: string): string =>
  text ? text.replace(/\*\*[^*]+\*\*/g, "") : "";

export function BoldText({ text }: { text: string }) {
  const parts = text.split(/(\*\*[^*]+\*\*)/g);
  return (
    <>
      {parts.map((part, i) =>
        part.startsWith("**") && part.endsWith("**") ? (
          <strong key={i}>{part.slice(2, -2)}</strong>
        ) : (
          <span key={i}>{part}</span>
        )
      )}
    </>
  );
}

// ---------------------------------------------
// Component
// ---------------------------------------------
export default function InterviewSearchPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [companyFilter, setCompanyFilter] = useState("all");
  const [roleFilter, setRoleFilter] = useState("all");
  const [posts, setPosts] = useState<InterviewPost[]>([]);
  const [companies, setCompanies] = useState<string[]>([]);
  const [roles, setRoles] = useState<string[]>([]);
  const [totalPages, setTotalPages] = useState(1);
  const [currentPage, setCurrentPage] = useState(1);

  const [isFetching, setIsFetching] = useState(false);
  const [fetchStatus, setFetchStatus] = useState<string>("");
  const [message, setMessage] = useState("Loading...");

  // ---------------------------------------------
  // Fetch posts from backend
  // ---------------------------------------------
  const fetchPosts = async () => {
    try {
      const tokenResp = await fetch(
        process.env.NEXT_PUBLIC_BACKEND_API_ENDPOINT! + "/token",
        {
          method: "GET",
          headers: { "Content-Type": "application/json" },
        }
      );
      if (!tokenResp.ok) {
        throw new Error(`Token fetch failed: ${tokenResp.status}`);
      }
      const { token } = await tokenResp.json();
      const page = currentPage.toString();
      const res = await fetch(
        process.env.NEXT_PUBLIC_BACKEND_API_ENDPOINT! + "/search",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            query: searchQuery,
            company: companyFilter,
            role: roleFilter,
            page: page,
            limit: 10,
          }),
        }
      );
      if (!res.ok) throw new Error(`Error: ${res.status}`);
      const data = await res.json();
      // 🔑 Parse raw backend results into what the frontend expects
      const posts: InterviewPost[] = (data.results ?? []).map((item: any) => ({
        raw: item.raw_post ?? "",
        summary: item.summary ?? "",
        url: item.url ?? "#",
        company: item.company ?? "Unknown",
        role: item.role ?? "Unknown",
      }));
      setCompanies(data.companies || []);
      setRoles(data.roles || []);

      const total = data.total ?? posts.length;
      const limit = data.limit ?? 10;
      setPosts(posts);
      setTotalPages(Math.min(10, Math.ceil(total / limit)));
    } catch (err) {
      console.error("Failed to fetch posts", err);
      setMessage("Error loading posts");
    }
  };

  // ---------------------------------------------
  // Triggers
  // ---------------------------------------------
  // Debounce search
  useEffect(() => {
    const handler = setTimeout(() => {
      setCurrentPage(1); // reset page on new search
      fetchPosts();
    }, 500);
    return () => clearTimeout(handler);
  }, [searchQuery]);

  // Immediate fetch on filter/page change
  useEffect(() => {
    fetchPosts();
    setCurrentPage(1); // reset page on new search
  }, [companyFilter, roleFilter, currentPage]);

  // ---------------------------------------------
  // UI
  // ---------------------------------------------
  const [expandedPosts, setExpandedPosts] = useState<Record<number, boolean>>(
    {}
  );
  const toggleExpand = (index: number) =>
    setExpandedPosts((prev) => ({ ...prev, [index]: !prev[index] }));

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

        {/* Search + Filters */}
        <Card className="mb-8">
          <CardContent className="p-6">
            <div className="flex flex-col gap-4">
              {/* Search */}
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
                      {(companies ?? []).map((company) => (
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
                      {(roles ?? []).map((role) => (
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
            Showing {(posts ?? []).length} posts (page {currentPage} of{" "}
            {totalPages})
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
          {(posts ?? []).length === 0 ? (
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
            posts.map((post: InterviewPost, index: number) => {
              const globalIndex = (currentPage - 1) * 10 + index;
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
                          {post.company || "Unknown"}
                        </Badge>
                        <Badge
                          variant="outline"
                          className="flex items-center gap-1"
                        >
                          <Briefcase className="h-3 w-3" />
                          {post.role || "Unknown"}
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
                            <BoldText text={post.raw} />
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

      {/* Footer Disclaimer */}
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
