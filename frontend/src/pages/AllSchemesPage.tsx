import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Search, Filter, ExternalLink, RefreshCw, CheckCircle2, Layers, Tag } from 'lucide-react';

export const AllSchemesPage: React.FC = () => {
  const [selectedLevel, setSelectedLevel] = useState<string>('ALL');
  const [selectedCategory, setSelectedCategory] = useState<number | null>(null);
  const [selectedBenefitType, setSelectedBenefitType] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState<string>('');

  // Fetch Categories
  const { data: categories = [] } = useQuery({
    queryKey: ['scheme-categories'],
    queryFn: async () => {
      const res = await fetch('/api/v1/schemes/categories');
      if (!res.ok) throw new Error('Failed to load categories');
      return res.json();
    },
  });

  // Fetch Schemes with Filters
  const { data: schemes = [], isLoading, refetch } = useQuery({
    queryKey: ['schemes', selectedLevel, selectedCategory, selectedBenefitType, searchQuery],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (selectedLevel !== 'ALL') params.append('level', selectedLevel);
      if (selectedCategory !== null) params.append('category_id', selectedCategory.toString());
      if (selectedBenefitType !== 'ALL') params.append('benefit_type', selectedBenefitType);
      if (searchQuery.trim()) params.append('search', searchQuery.trim());

      const res = await fetch(`/api/v1/schemes?${params.toString()}`);
      if (!res.ok) throw new Error('Failed to load scheme catalog');
      return res.json();
    },
  });

  return (
    <div className="space-y-6 py-6 max-w-7xl mx-auto">
      
      {/* Header Banner */}
      <div className="gov-card p-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <Layers className="w-5 h-5 text-gov-navy" />
            <h1 className="text-xl font-bold text-gov-navy">Master Welfare Scheme Catalog (યોજના કેટેલોગ)</h1>
          </div>
          <p className="text-xs text-slate-500">
            Consolidated repository of Gujarat State & Central Government Welfare Schemes & Entitlements
          </p>
        </div>

        <button
          onClick={() => refetch()}
          className="px-3 py-1.5 rounded bg-slate-100 hover:bg-slate-200 text-slate-700 border border-slate-300 text-xs font-semibold flex items-center gap-1.5"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin text-gov-blue' : ''}`} />
          <span>Sync Connectors</span>
        </button>
      </div>

      {/* Main Layout: Filters Sidebar + Schemes Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        
        {/* Left Filter Sidebar */}
        <div className="space-y-4">
          <div className="gov-card p-4 space-y-4">
            <div className="flex items-center gap-2 text-xs font-bold text-gov-navy uppercase tracking-wider border-b border-slate-100 pb-2">
              <Filter className="w-4 h-4 text-gov-blue" />
              <span>Filter Schemes</span>
            </div>

            {/* Level Filter Tabs */}
            <div className="space-y-1">
              <label className="block text-[11px] font-bold text-slate-500 uppercase">Government Jurisdiction</label>
              <div className="flex flex-col gap-1 text-xs">
                {['ALL', 'STATE', 'CENTRAL'].map((level) => (
                  <button
                    key={level}
                    onClick={() => setSelectedLevel(level)}
                    className={`px-3 py-2 rounded text-left font-semibold transition-colors flex items-center justify-between ${
                      selectedLevel === level
                        ? 'bg-gov-navy text-white shadow-sm'
                        : 'bg-slate-50 text-slate-700 hover:bg-slate-100'
                    }`}
                  >
                    <span>{level === 'ALL' ? 'All Schemes' : level === 'STATE' ? 'Gujarat State Govt' : 'Central Govt'}</span>
                    {selectedLevel === level && <CheckCircle2 className="w-3.5 h-3.5 text-saffron" />}
                  </button>
                ))}
              </div>
            </div>

            {/* Benefit Type Filter */}
            <div className="space-y-1">
              <label className="block text-[11px] font-bold text-slate-500 uppercase">Benefit Type</label>
              <select
                value={selectedBenefitType}
                onChange={(e) => setSelectedBenefitType(e.target.value)}
                className="w-full p-2 bg-white border border-slate-300 rounded text-xs text-slate-900 font-medium focus:outline-none focus:ring-2 focus:ring-gov-blue"
              >
                <option value="ALL" className="bg-white text-slate-900">All Benefit Types</option>
                <option value="CASH" className="bg-white text-slate-900">Cash Direct Transfer (DBT)</option>
                <option value="IN_KIND" className="bg-white text-slate-900">In-Kind Subsidized Ration</option>
                <option value="INSURANCE" className="bg-white text-slate-900">Health & Insurance Cover</option>
                <option value="SUBSIDY" className="bg-white text-slate-900">Subsidy & Financial Aid</option>
                <option value="LOAN" className="bg-white text-slate-900">Loan Interest Subsidy</option>
                <option value="SERVICE" className="bg-white text-slate-900">Service & Toolkits</option>
              </select>
            </div>

            {/* Categories List */}
            <div className="space-y-1 pt-2 border-t border-slate-100">
              <label className="block text-[11px] font-bold text-slate-500 uppercase mb-2">Categories</label>
              <button
                onClick={() => setSelectedCategory(null)}
                className={`w-full px-3 py-1.5 rounded text-left text-xs font-semibold mb-1 transition-colors ${
                  selectedCategory === null ? 'bg-gov-blue text-white' : 'text-slate-700 hover:bg-slate-100'
                }`}
              >
                All Categories ({categories.length})
              </button>

              <div className="space-y-1 max-h-60 overflow-y-auto pr-1">
                {categories.map((c: any) => (
                  <button
                    key={c.category_id}
                    onClick={() => setSelectedCategory(c.category_id)}
                    className={`w-full px-3 py-1.5 rounded text-left text-xs transition-colors flex items-center justify-between ${
                      selectedCategory === c.category_id
                        ? 'bg-gov-blue text-white font-bold'
                        : 'text-slate-600 hover:bg-slate-100'
                    }`}
                  >
                    <span className="truncate">{c.name}</span>
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Right Schemes Grid */}
        <div className="lg:col-span-3 space-y-4">
          
          {/* Search Box */}
          <div className="relative">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search schemes by name, department, or keyword (e.g. Kisan, Health, Ration)..."
              className="w-full pl-10 pr-4 py-2.5 bg-white border border-slate-300 rounded-md text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-gov-blue text-sm"
            />
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3.5" />
          </div>

          {/* Scheme Cards Grid */}
          {isLoading ? (
            <div className="p-12 text-center text-slate-500 text-xs flex items-center justify-center gap-2">
              <RefreshCw className="w-4 h-4 animate-spin text-gov-blue" />
              <span>Fetching scheme catalog from departmental connectors...</span>
            </div>
          ) : schemes.length === 0 ? (
            <div className="gov-card p-8 text-center text-slate-500 text-sm">
              No schemes match the selected filters.
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {schemes.map((s: any) => {
                const isState = s.level === 'STATE';

                return (
                  <div key={s.scheme_id} className="gov-card p-5 space-y-3 flex flex-col justify-between hover:border-gov-blue transition-colors">
                    <div className="space-y-2">
                      <div className="flex items-center justify-between gap-2">
                        <span className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded border ${
                          isState
                            ? 'bg-amber-50 text-amber-800 border-amber-200'
                            : 'bg-blue-50 text-blue-800 border-blue-200'
                        }`}>
                          {isState ? 'Gujarat State Govt' : 'Central Govt'}
                        </span>

                        <span className="text-[10px] font-semibold text-slate-500 flex items-center gap-1">
                          <Tag className="w-3 h-3 text-slate-400" />
                          {s.benefit_type}
                        </span>
                      </div>

                      <h3 className="font-bold text-sm text-gov-navy leading-snug">{s.name}</h3>
                      <p className="text-xs text-slate-600 line-clamp-2 leading-relaxed">{s.short_description}</p>
                    </div>

                    <div className="pt-3 border-t border-slate-100 space-y-2">
                      <div className="p-2 bg-slate-50 rounded border border-slate-200 text-xs font-semibold text-slate-800 flex items-center gap-1.5">
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                        <span className="truncate">{s.benefit_summary}</span>
                      </div>

                      <div className="flex items-center justify-between text-xs pt-1">
                        <span className="text-slate-400 font-mono text-[10px]">Synced: {s.source_system}</span>

                        <a
                          href={s.official_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-gov-blue hover:underline font-bold flex items-center gap-1"
                        >
                          <span>Official Portal</span>
                          <ExternalLink className="w-3.5 h-3.5" />
                        </a>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}

        </div>

      </div>

    </div>
  );
};
