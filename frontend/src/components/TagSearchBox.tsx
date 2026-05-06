import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { searchTagsGamesTagsGetOptions } from '../client/@tanstack/react-query.gen'
import { useDebouncedQuery } from '../hooks/useDebouncedQuery'

type Props = {
    selectedTags: string[]
    onAddTag: (tag: string) => void
    onRemoveTag: (tag: string) => void
}

export function TagSearchBox({ selectedTags, onAddTag, onRemoveTag }: Props) {
    const { query, setQuery, debouncedQuery } = useDebouncedQuery()
    const [isFocused, setIsFocused] = useState(false)

    const { data: suggestions = [] } = useQuery({
        ...searchTagsGamesTagsGetOptions({ query: { q: debouncedQuery } }),
        enabled: debouncedQuery.length > 0,
    })

    const filteredSuggestions = suggestions.filter(
        (tag) => !selectedTags.includes(tag)
    )

    const handleSelect = (tag: string) => {
        onAddTag(tag)
        setQuery('')
    }

    return (
        <div className="flex flex-col gap-3 w-full">
            {selectedTags.length > 0 && (
                <div className="flex flex-wrap gap-2">
                    {selectedTags.map((tag) => (
                        <span
                            key={tag}
                            className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full
                                bg-accent/15 text-accent text-sm font-medium border border-accent/30"
                        >
                            {tag}
                            <button
                                onClick={() => onRemoveTag(tag)}
                                className="hover:text-white transition-colors cursor-pointer text-xs ml-0.5"
                                aria-label={`Remove ${tag}`}
                            >
                                ✕
                            </button>
                        </span>
                    ))}
                </div>
            )}

            <div className="relative w-full">
                <input
                    type="text"
                    placeholder="Search for tags... (e.g. Action, RPG, Multiplayer)"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onFocus={() => setIsFocused(true)}
                    onBlur={() => setTimeout(() => setIsFocused(false), 150)}
                    className="bg-surface w-full border border-border rounded-lg p-2.5 outline-none
                        focus:border-accent hover:border-accent placeholder:text-text-dim"
                />

                {isFocused && query.length > 0 && filteredSuggestions.length > 0 && (
                    <ul className="absolute left-0 right-0 top-[calc(100%+4px)] bg-surface border border-border
                        rounded-lg z-10 overflow-hidden max-h-60 overflow-y-auto">
                        {filteredSuggestions.map((tag) => (
                            <li key={tag}>
                                <button
                                    onClick={() => handleSelect(tag)}
                                    className="cursor-pointer w-full text-left hover:bg-accent p-2.5 transition-colors"
                                >
                                    {tag}
                                </button>
                            </li>
                        ))}
                    </ul>
                )}
            </div>
        </div>
    )
}
