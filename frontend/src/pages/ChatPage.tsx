import { useEffect, useRef, useState } from "react"
import { useMutation } from "@tanstack/react-query"
import { useHead } from "@unhead/react"
import ReactMarkdown from "react-markdown"
import type { Components } from "react-markdown"
import { NavigationBar } from "../components/NavigationBar"
import { GameCard } from "../components/GameCard"
import { chatChatPostMutation } from "../client/@tanstack/react-query.gen"
import { useProfileGames } from "../hooks/useProfileGames"
import { useChatHistory } from "../hooks/useChatHistory"
import { SITE_URL, SITE_NAME } from "../lib/seo"

const MAX_MESSAGE_CHARS = 4000
const MAX_HISTORY_MESSAGES = 20
const MAX_LIBRARY_GAMES = 1000

// Markdown styling for assistant replies 
const markdownComponents: Components = {
    p: (props) => <p className="mb-2 last:mb-0">{props.children}</p>,
    ul: (props) => <ul className="list-disc pl-5 mb-2 last:mb-0 space-y-1">{props.children}</ul>,
    ol: (props) => <ol className="list-decimal pl-5 mb-2 last:mb-0 space-y-1">{props.children}</ol>,
    a: (props) => (
        <a href={props.href} target="_blank" rel="noopener noreferrer" className="text-accent underline">
            {props.children}
        </a>
    ),
}

const SUGGESTIONS = [
    "I loved Elden Ring, what should I play next?",
    "Recommend me a co-op game for two players",
    "What's a good short indie game?",
]

export default function ChatPage() {
    useHead({
        title: `Game Advisor - ${SITE_NAME}`,
        meta: [
            { name: 'description', content: 'Chat with the game advisor and get personalized game recommendations' },
            { property: 'og:title', content: `Game Advisor - ${SITE_NAME}` },
            { property: 'og:description', content: 'Chat with the game advisor and get personalized game recommendations' },
            { property: 'og:url', content: `${SITE_URL}/chat` },
            { property: 'og:site_name', content: SITE_NAME },
            { property: 'og:type', content: 'website' },
        ],
        link: [
            { rel: 'canonical', href: `${SITE_URL}/chat` },
        ],
    })

    const { savedGames } = useProfileGames()
    const { messages, addMessage, clearMessages } = useChatHistory()
    const [input, setInput] = useState("")
    const bottomRef = useRef<HTMLDivElement>(null)

    const { mutate, isPending } = useMutation({
        ...chatChatPostMutation(),
        onSuccess: (data) => {
            addMessage({ role: "assistant", content: data.reply, games: data.games })
        },
        onError: () => {
            addMessage({ role: "assistant", content: "Sorry, something went wrong. Please try again." })
        },
    })

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: "smooth" })
    }, [messages, isPending])

    const send = (text: string) => {
        const message = text.trim()
        if (!message || isPending) return

        const history = messages.slice(-MAX_HISTORY_MESSAGES).map(({ role, content }) => ({ role, content }))
        const library = savedGames.slice(0, MAX_LIBRARY_GAMES)
        addMessage({ role: "user", content: message })
        setInput("")

        mutate({
            body: {
                message,
                history,
                ...(library.length > 0 && {
                    app_ids: library.map((g) => g.app_id),
                    hours_played: library.map((g) => g.hours),
                }),
            },
        })
    }

    return (
        <>
            <NavigationBar />
            <div className="flex flex-col max-w-3xl mx-auto p-4 sm:p-6 h-[calc(100vh-3.5rem)]">
                <div className="flex items-center justify-between mb-3">
                    <h1 className="text-2xl font-semibold">Game Advisor</h1>
                    {messages.length > 0 && (
                        <button
                            onClick={clearMessages}
                            className="text-sm text-text-dim hover:text-red-400 transition-colors cursor-pointer"
                        >
                            Clear chat
                        </button>
                    )}
                </div>
                <p className="text-text-dim text-sm mb-4">
                    Ask for game recommendations in plain language.
                    {savedGames.length > 0 && " Your profile games are included for personalized picks."}
                </p>

                <div className="flex-1 overflow-y-auto flex flex-col gap-3 pr-1">
                    {messages.length === 0 && (
                        <div className="flex flex-col items-center gap-2 mt-8">
                            <p className="text-text-dim">Try asking:</p>
                            {SUGGESTIONS.map((s) => (
                                <button
                                    key={s}
                                    onClick={() => send(s)}
                                    className="border border-border rounded-full px-4 py-2 text-sm text-text-dim
                                               hover:border-accent hover:text-text transition-colors cursor-pointer"
                                >
                                    {s}
                                </button>
                            ))}
                        </div>
                    )}

                    {messages.map((m, i) => (
                        <div
                            key={i}
                            className={m.role === "user"
                                ? "self-end max-w-[85%]"
                                : "self-start w-full sm:max-w-[90%]"}
                        >
                            <div className={m.role === "user"
                                ? "bg-accent text-white rounded-lg px-4 py-2.5 whitespace-pre-wrap"
                                : "bg-surface border border-border rounded-lg px-4 py-2.5"}
                            >
                                {m.role === "user"
                                    ? m.content
                                    : <ReactMarkdown components={markdownComponents}>{m.content}</ReactMarkdown>}
                            </div>
                            {m.games && m.games.length > 0 && (
                                <div className="flex flex-col gap-2 mt-2">
                                    {m.games.map((g) => (
                                        <GameCard
                                            key={g.app_id}
                                            appId={g.app_id}
                                            gameName={g.game_name}
                                            headerImage={g.header_image}
                                            score={g.hybrid_score}
                                        />
                                    ))}
                                </div>
                            )}
                        </div>
                    ))}

                    {isPending && (
                        <div className="self-start bg-surface border border-border rounded-lg px-4 py-2.5 text-text-dim">
                            Thinking…
                        </div>
                    )}
                    <div ref={bottomRef} />
                </div>

                <form
                    onSubmit={(e) => { e.preventDefault(); send(input) }}
                    className="flex gap-2 mt-4"
                >
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        maxLength={MAX_MESSAGE_CHARS}
                        placeholder="Ask for a game recommendation…"
                        className="flex-1 border border-border rounded-lg bg-surface p-2.5 text-text outline-none
                                   focus:border-accent hover:border-accent transition-colors"
                    />
                    <button
                        type="submit"
                        disabled={isPending || !input.trim()}
                        className="bg-accent text-white rounded-lg px-6 py-2.5 font-medium cursor-pointer
                                   hover:brightness-110 disabled:opacity-50 transition-all"
                    >
                        Send
                    </button>
                </form>
            </div>
        </>
    )
}
