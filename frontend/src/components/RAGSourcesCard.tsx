import React, { useState } from 'react';
import { BookOpen, ExternalLink, ChevronDown, ChevronUp, CheckCircle2 } from 'lucide-react';
import { RAGSource } from '../types';

interface RAGSourcesCardProps {
  sources: RAGSource[];
}

export const RAGSourcesCard: React.FC<RAGSourcesCardProps> = ({ sources }) => {
  const [expandedIndex, setExpandedIndex] = useState<number | null>(0);

  if (!sources || sources.length === 0) {
    return (
      <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 text-center text-slate-500 text-xs">
        <BookOpen className="w-5 h-5 mx-auto mb-1 text-slate-600" />
        No policy citations retrieved for this query.
      </div>
    );
  }

  return (
    <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 space-y-2.5">
      <div className="flex items-center justify-between pb-2 border-b border-slate-800">
        <div className="flex items-center space-x-2">
          <BookOpen className="w-4 h-4 text-sky-400" />
          <h3 className="text-xs font-bold text-white uppercase tracking-wider">
            Approved University Evidence (RAG)
          </h3>
        </div>
        <span className="text-[11px] text-slate-400 font-medium">
          {sources.length} Verified {sources.length === 1 ? 'Citation' : 'Citations'}
        </span>
      </div>

      <div className="space-y-2">
        {sources.map((src, idx) => {
          const isExpanded = expandedIndex === idx;
          return (
            <div
              key={src.document_id + idx}
              className="bg-slate-950/70 border border-slate-800 rounded-lg overflow-hidden transition"
            >
              <div
                onClick={() => setExpandedIndex(isExpanded ? null : idx)}
                className="p-2.5 flex items-center justify-between cursor-pointer hover:bg-slate-900/60"
              >
                <div className="flex items-center space-x-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-sky-400 flex-shrink-0" />
                  <div>
                    <h4 className="text-xs font-semibold text-slate-200 line-clamp-1">
                      {src.title}
                    </h4>
                    <span className="text-[10px] text-sky-400 font-mono">
                      {src.clause}
                    </span>
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-sky-500/10 text-sky-400 border border-sky-500/20">
                    {Math.round(src.relevance_score * 100)}% match
                  </span>
                  {isExpanded ? (
                    <ChevronUp className="w-3.5 h-3.5 text-slate-400" />
                  ) : (
                    <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
                  )}
                </div>
              </div>

              {isExpanded && (
                <div className="px-3 pb-3 pt-1 text-xs text-slate-300 border-t border-slate-800/80 bg-slate-950/90 font-sans leading-relaxed">
                  <blockquote className="border-l-2 border-sky-500/60 pl-2.5 my-1 italic text-slate-300">
                    "{src.excerpt}"
                  </blockquote>
                  <div className="mt-2 flex items-center justify-between text-[10px] text-slate-500 font-mono">
                    <span>Document ID: {src.document_id}</span>
                    <span>Status: Approved for Official Triage</span>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
