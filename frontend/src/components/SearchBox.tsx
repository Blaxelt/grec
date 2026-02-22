import type { GameSearchResult } from '../client'

type Props = {
    query: string
    onQueryChange: (value: string) => void
    suggestions: GameSearchResult[]
    showSuggestions: boolean
    onSelectGame: (name: string) => void
}

export function SearchBox({ query, onQueryChange, suggestions, showSuggestions, onSelectGame }: Props) {
    return (
        <div className="search-wrapper">
            <input
                type="text"
                placeholder="Search for a game..."
                value={query}
                onChange={(e) => onQueryChange(e.target.value)}
                className="search-input"
            />

            {showSuggestions && suggestions.length > 0 && (
                <ul className="suggestions">
                    {suggestions.map((g) => (
                        <li key={g.game_name}>
                            <button onClick={() => onSelectGame(g.game_name)} className="suggestion-btn">
                                {g.game_name}
                            </button>
                        </li>
                    ))}
                </ul>
            )}
        </div>
    )
}
