"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import type { SearchableDropdownQuestion } from "@/lib/questionnaire.types";
import { QuestionBlock } from "../QuestionBlock";
import { SelectChevron } from "../SelectChevron";

type Props = {
  question: SearchableDropdownQuestion;
  value: string;
  onChange: (v: string) => void;
  options: string[];
};

export function SearchableDropdownField({ question, value, onChange, options }: Props) {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const rootRef = useRef<HTMLDivElement>(null);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return options;
    return options.filter((o) => o.toLowerCase().includes(q));
  }, [options, query]);

  useEffect(() => {
    if (!open) return;
    const onDoc = (e: MouseEvent) => {
      if (!rootRef.current?.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", onDoc);
    return () => document.removeEventListener("mousedown", onDoc);
  }, [open]);

  useEffect(() => {
    if (open) setQuery("");
  }, [open]);

  const placeholder = question.placeholder ?? "Search or select";

  return (
    <QuestionBlock order={question.order} label={question.label} description={question.description}>
      <div ref={rootRef} className="relative w-full">
        <button
          type="button"
          id={question.id}
          aria-haspopup="listbox"
          aria-expanded={open}
          className="relative box-border flex h-9 w-full items-center rounded-full border border-slate-300/40 bg-white px-4 pr-10 text-left font-sans text-xs text-[#0C1A3A] focus:border-sky-500 focus:outline-none"
          onClick={() => setOpen((o) => !o)}
        >
          <span className={`min-w-0 flex-1 truncate ${value ? "text-[#0C1A3A]" : "text-slate-400"}`}>
            {value || placeholder}
          </span>
          <SelectChevron />
        </button>

        {open ? (
          <div
            className="absolute left-0 right-0 z-50 mt-1 max-h-64 overflow-hidden rounded-2xl border border-slate-200 bg-white py-1 shadow-lg"
            role="listbox"
          >
            <div className="border-b border-slate-100 px-2 pb-1 pt-1">
              <input
                type="search"
                className="box-border h-8 w-full rounded-full border border-slate-200 px-3 font-sans text-xs text-[#0C1A3A] focus:border-sky-500 focus:outline-none"
                placeholder="Search countries…"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                autoComplete="off"
                aria-label="Filter countries"
              />
            </div>
            <ul className="max-h-48 overflow-y-auto py-1">
              {filtered.length === 0 ? (
                <li className="px-4 py-2 text-xs text-slate-400">No matches</li>
              ) : (
                filtered.map((opt) => (
                  <li key={opt} role="option" aria-selected={opt === value}>
                    <button
                      type="button"
                      className="w-full px-4 py-2 text-left font-sans text-xs text-[#0C1A3A] hover:bg-sky-50"
                      onClick={() => {
                        onChange(opt);
                        setOpen(false);
                      }}
                    >
                      {opt}
                    </button>
                  </li>
                ))
              )}
            </ul>
          </div>
        ) : null}
      </div>
    </QuestionBlock>
  );
}
