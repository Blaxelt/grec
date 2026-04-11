import { Link, useLocation } from "react-router-dom";

const navItems = [
    { label: "Home", to: "/"},
];

export function NavigationBar() {
    const { pathname } = useLocation();

    return (
        <nav className="flex items-center h-14 px-10 bg-surface border-b border-border gap-8">
            <Link to="/" className="font-press text-sm tracking-wider text-text shrink-0 mr-4">
                GREC
            </Link>

            <div className="flex items-center gap-1">
                {navItems.map(({ label, to }) => {
                    const isActive = pathname === to;

                    return (
                        <Link
                            key={label}
                            to={to}
                            className={`relative px-3 py-1.5 text-sm font-medium rounded-md transition-colors
                                ${isActive
                                    ? "text-accent"
                                    : "text-text-dim hover:text-text hover:bg-white/5"
                                }`}
                        >
                            {label}
                            {isActive && (
                                <span className="absolute bottom-0 left-3 right-3 h-0.5 bg-accent rounded-full" />
                            )}
                        </Link>
                    );
                })}
            </div>
        </nav>
    );
}