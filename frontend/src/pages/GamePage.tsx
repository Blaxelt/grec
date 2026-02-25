import { useParams } from 'react-router-dom'

export default function GamePage() {
    const { id } = useParams<{ id: string }>()

    return (
        <div className="container">
            <h1>Game #{id}</h1>
            <p className="subtitle">Game detail page — coming soon</p>
        </div>
    )
}
