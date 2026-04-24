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

    const addGame = (game: { app_id: number; game_name: string; header_image?: string | null }) => {
        if (savedGames.some((g) => g.app_id === game.app_id)) return
        setGames([...savedGames, {
            app_id: game.app_id,
            game_name: game.game_name,
            header_image: game.header_image ?? null,
            hours: 10,
        }])
    }

    const removeGame = (app_id: number) => {
        setGames(savedGames.filter((g) => g.app_id !== app_id))
    }

    const updateHours = (app_id: number, hours: number) => {
        setGames(savedGames.map((g) => (g.app_id === app_id ? { ...g, hours } : g)))
    }

    const hasGame = (app_id: number) => savedGames.some((g) => g.app_id === app_id)

    return { savedGames, addGame, removeGame, updateHours, hasGame }
}
