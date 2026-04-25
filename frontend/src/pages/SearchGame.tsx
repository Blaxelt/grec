import { SearchBox } from "../components/SearchBox";
import { NavigationBar } from "../components/NavigationBar";
import { useQuery } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { searchGamesGamesSearchGetOptions } from '../client/@tanstack/react-query.gen';
import type { GameSearchResult } from '../client';
import { useDebouncedQuery } from '../hooks/useDebouncedQuery';

export default function SearchGame() {
    const { query, setQuery, debouncedQuery } = useDebouncedQuery()
    const navigate = useNavigate();

    const { data: suggestions = [] } = useQuery({
        ...searchGamesGamesSearchGetOptions({ query: { q: debouncedQuery } }),
        enabled: debouncedQuery.length > 0,
    })

    const selectGame = (game: GameSearchResult) => {
        navigate(`/games/${game.app_id}`)
    }

    return (
        <>
            <NavigationBar />
            <div className="flex flex-col gap-4 pt-40 w-full max-w-2xl mx-auto">
                <h1 className="font-press text-4xl tracking-wider text-center mb-10">Game details</h1>
                <SearchBox
                    query={query}
                    onQueryChange={setQuery}
                    suggestions={suggestions}
                    showSuggestions={query.length > 0}
                    onSelectGame={selectGame}
                />
            </div>
        </>
    );
}