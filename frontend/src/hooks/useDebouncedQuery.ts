import { useState, useEffect } from "react"

export function useDebouncedQuery(delay = 300) {
    const [query, setQuery] = useState("")
    const [debounced, setDebounced] = useState("")
    useEffect(() => {
        const id = setTimeout(() => setDebounced(query), delay)
        return () => clearTimeout(id)
    }, [query, delay])
    return { query, setQuery, debouncedQuery: debounced }
}