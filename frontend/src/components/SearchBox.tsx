import type { GameSearchResult } from '../client'
import { useState } from 'react'

type Props = {
    query: string
    onQueryChange: (value: string) => void
    suggestions: GameSearchResult[]
    showSuggestions: boolean
    onSelectGame: (game: GameSearchResult) => void
}

export function SearchBox({ query, onQueryChange, suggestions, showSuggestions, onSelectGame }: Props) {
    const [isFocused, setIsFocused] = useState(false)
    const [activeIndex, setActiveIndex] = useState(-1)
    const isOpen = isFocused && showSuggestions && suggestions.length > 0

    const selectItem = (index: number) => {
        if (index >= 0 && index < suggestions.length) {
            onSelectGame(suggestions[index])
            setActiveIndex(-1)
        }
    }

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (!isOpen) return

        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault()
                setActiveIndex((i) => (i + 1) % suggestions.length)
                break
            case 'ArrowUp':
                e.preventDefault()
                setActiveIndex((i) => (i - 1 + suggestions.length) % suggestions.length)
                break
            case 'Enter':
                e.preventDefault()
                selectItem(activeIndex)
                break
            case 'Escape':
                setIsFocused(false)
                setActiveIndex(-1)
                break
        }
    }

    return (
        <div className="relative w-full">
            <input
                type="text"
                placeholder="Search for a game..."
                value={query}
                onChange={(e) => {
                    onQueryChange(e.target.value)
                    setActiveIndex(-1)
                }}
                onFocus={() => setIsFocused(true)}
                onBlur={() => setTimeout(() => { setIsFocused(false); setActiveIndex(-1) }, 100)}
                onKeyDown={handleKeyDown}
                role="combobox"
                aria-expanded={isOpen}
                aria-controls="search-suggestions"
                aria-activedescendant={activeIndex >= 0 ? `search-suggestion-${activeIndex}` : undefined}
                aria-autocomplete="list"
                className="bg-surface w-full border border-border rounded-lg p-2.5 outline-none focus:border-accent hover:border-accent
                placeholder:text-text-dim"
            />

            {isOpen && (
                <ul
                    id="search-suggestions"
                    role="listbox"
                    className="absolute left-0 right-0 top-[calc(100%+4px)] bg-surface border border-border rounded-lg z-10 overflow-hidden"
                    data-testid="suggestions"
                >
                    {suggestions.map((g, i) => (
                        <li
                            key={g.app_id}
                            id={`search-suggestion-${i}`}
                            role="option"
                            aria-selected={i === activeIndex}
                        >
                            <button
                                onClick={() => selectItem(i)}
                                className={`cursor-pointer w-full text-left p-2.5 ${i === activeIndex ? 'bg-accent' : 'hover:bg-accent'}`}
                            >
                                {g.game_name}
                            </button>
                        </li>
                    ))}
                </ul>
            )}
        </div>
    )
}
