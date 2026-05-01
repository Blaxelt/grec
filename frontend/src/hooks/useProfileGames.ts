import { useLocalStorage } from "react-use"

export type SavedGame = {
    app_id: number
    game_name: string
    header_image: string | null
    hours: number
}

export function useProfileGames() {
    const [games, setGames] = useLocalStorage<SavedGame[]>("profile-games", [])
    const savedGames = games ?? []

    const addGame = (game: { app_id: number; game_name: string; header_image?: string | null; hours?: number }) => {
        if (savedGames.some((g) => g.app_id === game.app_id)) return
        setGames([...savedGames, {
            app_id: game.app_id,
            game_name: game.game_name,
            header_image: game.header_image ?? null,
            hours: game.hours ?? 10,
        }])
    }

    const addGames = (newGames: { app_id: number; game_name: string; header_image?: string | null; hours?: number }[]) => {
        setGames((prev) => {
            const current = prev ?? []
            const toAdd = newGames.filter(g => !current.some(s => s.app_id === g.app_id))
            return [...current, ...toAdd.map(g => ({
                app_id: g.app_id,
                game_name: g.game_name,
                header_image: g.header_image ?? null,
                hours: g.hours ?? 10,
            }))]
        })
    }

    const removeGame = (app_id: number) => {
        setGames(savedGames.filter((g) => g.app_id !== app_id))
    }

    const updateHours = (app_id: number, hours: number) => {
        setGames(savedGames.map((g) => (g.app_id === app_id ? { ...g, hours } : g)))
    }

    const hasGame = (app_id: number) => savedGames.some((g) => g.app_id === app_id)

    return { savedGames, addGame, addGames, removeGame, updateHours, hasGame }
}
