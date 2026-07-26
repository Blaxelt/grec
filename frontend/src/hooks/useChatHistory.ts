import { useEffect, useState } from "react"
import type { ChatMessage, GameRecommendation } from "../client"

export type StoredChatMessage = ChatMessage & { games?: GameRecommendation[] }

const STORAGE_KEY = "chat-history"
const MAX_STORED_MESSAGES = 100

function loadMessages(): StoredChatMessage[] {
    try {
        const raw = localStorage.getItem(STORAGE_KEY)
        return raw ? JSON.parse(raw) : []
    } catch {
        return []
    }
}

export function useChatHistory() {
    const [messages, setMessages] = useState<StoredChatMessage[]>(loadMessages)

    useEffect(() => {
        try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(messages))
        } catch {
            // Ignore storage errors (private mode, quota exceeded)
        }
    }, [messages])

    const addMessage = (message: StoredChatMessage) => {
        setMessages((prev) => [...prev, message].slice(-MAX_STORED_MESSAGES))
    }

    const clearMessages = () => setMessages([])

    return { messages, addMessage, clearMessages }
}
