import { NavigationBar } from "../components/NavigationBar"

export default function Profile() {
    return (
        <>
            <NavigationBar />
            <div className="flex flex-col p-10">
                <h1>Games played</h1>
                <div className="grid grid-cols-screenshots gap-3">
                    {/* TODO: Map games played */}
                </div>
            </div>
        </>
    )
}