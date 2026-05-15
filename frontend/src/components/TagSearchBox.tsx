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
    const [activeIndex, setActiveIndex] = useState(-1)

    const { data: suggestions = [] } = useQuery({
        ...searchTagsGamesTagsGetOptions({ query: { q: debouncedQuery } }),
        enabled: debouncedQuery.length > 0,
    })

    const filteredSuggestions = suggestions.filter(
        (tag) => !selectedTags.includes(tag)
    )

    const isOpen = isFocused && query.length > 0 && filteredSuggestions.length > 0

    const handleSelect = (index: number) => {
        if (index >= 0 && index < filteredSuggestions.length) {
            onAddTag(filteredSuggestions[index])
            setQuery('')
            setActiveIndex(-1)
        }
    }

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (!isOpen) return

        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault()
                setActiveIndex((i) => (i + 1) % filteredSuggestions.length)
                break
            case 'ArrowUp':
                e.preventDefault()
                setActiveIndex((i) => (i - 1 + filteredSuggestions.length) % filteredSuggestions.length)
                break
            case 'Enter':
                e.preventDefault()
                handleSelect(activeIndex)
                break
            case 'Escape':
                setIsFocused(false)
                setActiveIndex(-1)
                break
        }
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
                    onChange={(e) => {
                        setQuery(e.target.value)
                        setActiveIndex(-1)
                    }}
                    onFocus={() => setIsFocused(true)}
                    onBlur={() => setTimeout(() => { setIsFocused(false); setActiveIndex(-1) }, 100)}
                    onKeyDown={handleKeyDown}
                    role="combobox"
                    aria-expanded={isOpen}
                    aria-controls="tag-suggestions"
                    aria-activedescendant={activeIndex >= 0 ? `tag-suggestion-${activeIndex}` : undefined}
                    aria-autocomplete="list"
                    className="bg-surface w-full border border-border rounded-lg p-2.5 outline-none
                        focus:border-accent hover:border-accent placeholder:text-text-dim"
                />

                {isOpen && (
                    <ul
                        id="tag-suggestions"
                        role="listbox"
                        className="absolute left-0 right-0 top-[calc(100%+4px)] bg-surface border border-border
                            rounded-lg z-10 overflow-hidden max-h-60 overflow-y-auto"
                    >
                        {filteredSuggestions.map((tag, i) => (
                            <li
                                key={tag}
                                id={`tag-suggestion-${i}`}
                                role="option"
                                aria-selected={i === activeIndex}
                            >
                                <button
                                    onClick={() => handleSelect(i)}
                                    className={`cursor-pointer w-full text-left p-2.5 transition-colors ${i === activeIndex ? 'bg-accent' : 'hover:bg-accent'}`}
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
